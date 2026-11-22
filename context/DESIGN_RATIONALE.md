# ±102 V Isolated Flyback Supply: Design Rationale

Exported 2026-11-22 from the shared design-rationale document (decision log P-1 to P-25).

> **Read this as a chronological log.** Sections near the top describe early designs (+110 V, one converter per rail,
> 100 mA) that were later superseded; the "Under revision" note and the decision log near the end say which. The
> current design is `../FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md`. Numbers are tagged [DS] datasheet, [calc] TI
> calculator, [L] LTspice, [H] hand calculation, [ASSUME] assumption.

**Under revision since 14 Nov 2026.** A review against the analog channel team's workspace (16 channels, their decisions D-B and D-C, their tests A1, A7 and A8) changes the load current, the rail setpoint and the two-converter plan. The sections below describe the design before that review. Decisions P-4, P-5 and P-6 to P-10 were taken on 14 Nov 2026; see the decision log at the end. The earlier sections will be rewritten after the WEBENCH re-run.

Numbers are tagged by source, following the analog team's convention: \[DS\] datasheet, \[H\] hand calculation, \[L\] LTspice, \[WB\] WEBENCH, \[B\] bench, \[ASSUME\] assumption.

## Requirements

Each rail delivers about 112 V at up to 100 mA from a 9–12.6 V battery, isolated from the battery side and low in noise.

| Requirement | Value | Where it comes from |
| --- | --- | --- |
| Load current | 80 mA maximum | 8 Howland pumps at 10 mA each |
| Design current | 100 mA | 25% margin, so parts run below their limits |
| Voltage across the load | 100 V | 10 mA through 10 kΩ (Ohm's law) |
| Clean rail at the pumps | 105 V or more | The pump output stage and sense resistor cannot swing to the rail |
| Raw flyback output | 112.6 V recommended (110 V in the first WEBENCH run) | Clean rail, plus about 3.5 V filter drop, plus setpoint tolerance |
| Input | 9–12.6 V | Three-cell lithium-ion battery, 11.1 V nominal |
| Minimum load | Zero | The pumps can idle |
| Isolation | Provided at the device boundary, not by the flyback (proposed 14 Nov 2026) | The load is two electrodes on skin |
| Negative rail | Identical copy with its positive terminal grounded | An isolated output floats, so either terminal can be the reference |

Margin is applied differently to current and voltage. Current margin is spare capacity. Voltage margin goes into component ratings, because the output voltage is a regulated setpoint the load actually receives.

## Topology

A flyback stores energy in a coupled inductor while the switch is on and releases it to an isolated secondary while the switch is off. One magnetic part therefore provides both the 12× voltage step-up and the isolation.

```latex
V_{out} = V_{in} \cdot \frac{N_s}{N_p} \cdot \frac{D}{1-D}
```

At 9 V in, a turns ratio of 18.62 and a duty cycle D of 0.397, this gives 110 V. The duty cycle is the fraction of each cycle the switch is on.

The power path runs in a straight line:

1. Battery, 9–12.6 V.
2. Flyback converter (LM51551 controller, 252 kHz), producing the raw rail.
3. LC filter.
4. Capacitance multiplier, producing the clean rail.
5. Eight Howland current pumps.

A reference and optocoupler on the output side send the error signal back to the controller.

| Choice | Why | Underlying principle |
| --- | --- | --- |
| Flyback, not a boost converter | A boost cannot isolate. A flyback is the lowest part count isolated topology at about 11 W | Energy stored in a magnetic field (E = ½LI²) crosses the barrier as flux, with no conductive path |
| Turns ratio of 18.6 | Keeps duty near 40% and switch stress near 30 V | A transformer reflects voltage by the turns ratio; volt-seconds on the inductor must balance each cycle |
| Continuous current at full load, discontinuous below about 23 mA | Lower peak currents at full load | Inductor ripple current ΔI = V·t / L |
| 252 kHz switching | Small magnetics and capacitors; ripple is far above the filter corner | Impedance of L and C scales with frequency |
| Peak current mode control | Limits current every cycle and simplifies the loop | Controlling inductor current directly turns the inductor into a current source, removing one pole from the loop |
| Regulation sensed on the output side | Holds the setpoint down to zero load | Negative feedback corrects only what it measures; the optocoupler carries the signal as light |

## Power stage

Every power component is chosen by working out the worst voltage and current it sees, then picking a rating comfortably above that. Hand calculations of duty cycle, frequency, ripple current, peak current and sense resistor loss match the WEBENCH figures.

| Part | Worst-case stress | Choice | Underlying principle |
| --- | --- | --- | --- |
| Switch (MOSFET) | About 30 V: input, plus 6 V reflected from the output, plus a leakage spike | 100 V part (CSD19538Q2) | Voltage reflects through the turns ratio; flux that does not couple to the secondary produces V = L·di/dt when the switch opens |
| Primary snubber | About 0.3 W of leakage energy | Values to be set on the bench | Energy in uncoupled flux must be dissipated somewhere controlled |
| Output diode | About 347 V reverse: output plus input multiplied by the turns ratio | 600 V ultrafast or silicon carbide | While the switch is on, the secondary winding voltage adds to the output; stored charge in a slow diode causes current spikes |
| Output capacitors | 112 V DC, 79 mA RMS ripple current | 200 V electrolytic plus 250 V ceramics | I = C·dV/dt sets ripple; ceramics lose capacitance under DC bias |
| Current sense resistor | 16 mΩ, giving a 6.25 A trip against a 3.8–4.3 A working peak | 1 W part | Ohm's law converts current to a voltage the controller can compare |
| Transformer | 9 µH primary, 18.62 turns ratio, must not saturate below 6.5 A | Coilcraft DA2033-AL (1:10, 10 µH) proposed; a custom reinforced part only if the grounds are later separated | A core saturates above a flux limit, after which inductance collapses and current runs away |
| Input capacitors | Pulsed primary current, 3.8 A peak | Low-resistance polymer plus ceramic | Capacitors supply the alternating part of the current so the battery sees nearly DC |

A web search on 14 Nov 2026 found no catalogue transformer that combines a low-voltage input, a 110 V output and reinforced medical isolation. Catalogue reinforced flybacks, such as the [Würth MID-OLRM series](https://eepower.com/new-industry-products/flyback-transformers-with-grounded-core-and-reinforced-insulation/), have 5 V or 12 V outputs. The nearest electrical match is the [Coilcraft DA203x capacitor-charging family](https://www.coilcraft.com/en-us/products/transformers/power-transformers/capacitor-charging/da203x/): 1:10, 10 µH, but only 1500 Vrms functional isolation and 67–128 pF between windings. It suits bench prototyping only, never patient connection. These figures come from search summaries of the datasheet and need confirming on the datasheet itself.

## Feedback and regulation

The WEBENCH feedback template put 25–36 V parts on the 110 V rail. The redesign keeps TI's loop compensation and adds a high-voltage transistor that shields the reference from the rail. It is hand-calculated and not yet simulated.

Regulation works in three steps. A resistor divider scales the rail down to 2.495 V. A TL431 reference compares that with its internal 2.495 V and steers current through the optocoupler LED. The optocoupler transistor pulls down the controller's COMP pin, which sets the peak current in the transformer.

| Change | Why | Underlying principle |
| --- | --- | --- |
| 300 V transistor added between the optocoupler LED and the TL431, base held at 12 V (a cascode) | The TL431 is limited to 36 V, but that node sits at 54–82 V in regulation | A common-base stage passes current unchanged while absorbing the voltage |
| Compensation network moved to the transistor's collector, with a 250 V capacitor | The integrator must sense the node that actually swings | An op-amp integrator only works if its feedback encloses the output node |
| Divider raised from 30 kΩ to about 100 kΩ, compensation scaled to match (845 kΩ, 1.5 nF) | Divider loss falls from 0.40 W to 0.12 W with the same loop response | Scaling every impedance by the same factor leaves the RC products, and so the transfer function, unchanged |
| Every resistor on the 112 V rail split into three 1206 parts in series | Small resistors have voltage limits as well as power limits | Series elements share voltage; P = V²/R |
| 2 kΩ resistor across the optocoupler LED | Guarantees the TL431 at least 1 mA | An active device needs a minimum bias current to stay in its linear region |
| Start-up network re-rated: 1 MΩ, 2.2 µF at 250 V, 250 V diode | The original 25 V capacitor would charge to the full rail | A capacitor charges to its source voltage; I = C·dV/dt sets the ramp rate |
| 0.5% reference (TL431B) with 1% resistors | Holds the rail within about ±1.5% | Tolerances add in an error budget |

The feedback network's loss falls from 1.2 W to about 0.35 W. Its standing current of 2.6–3.2 mA doubles as the minimum load.

## Output filtering

Two stages cut roughly 100 mV of switching ripple to well under a millivolt before it reaches the pumps: a passive LC filter, then an active capacitance multiplier. Together they drop about 3.5 V, which is why the raw rail is set above 110 V. The values are first-pass estimates.

| Element | Value | Effect | Underlying principle |
| --- | --- | --- | --- |
| LC filter | 100 µH with about 1 µF effective | 16 kHz corner; about 48 dB at 252 kHz | A second-order low-pass falls at 40 dB per decade above f = 1 / (2π√LC) |
| Damping branch | 10 µF in series with 10 Ω | Stops ringing at the corner frequency | An undamped LC resonates; a resistance near √(L/C) absorbs the energy |
| Ferrite bead | In series | Attenuates spikes above 10 MHz | A real inductor turns capacitive above its self-resonance, so a second part covers the higher band |
| Capacitance multiplier | 250 V MOSFET follower; 100 kΩ and about 0.4 µF on its gate | About 40 dB more; 4 Hz corner; 40 ms start-up ramp | A follower copies its gate voltage at high current, so a small capacitor filtered at high impedance behaves like a very large one |
| Feedback taken before the filter |  | The filter cannot destabilise the loop | Each LC stage inside a loop adds up to 180° of phase lag |
| Both rails switched at one frequency |  | No beat tone in the signal band | Two nearby frequencies mix to produce their difference |

## Protection

The supply is designed so that no single fault lets the rail run away, and so that it stays in regulation with every pump idle.

| Measure | What it does | Underlying principle |
| --- | --- | --- |
| Standing load of 2.6–3.2 mA from the feedback network | Keeps the rail regulated at zero pump current; no separate bleeder resistor is needed | Energy balance: each switching pulse delivers a minimum energy, and any surplus over the load raises the capacitor voltage |
| Second optocoupler driven by a Zener string of about 130 V, in parallel with the main one | If the main feedback path fails open, the rail is held near 130 V | Redundancy; Zener breakdown acts as a voltage threshold |
| Transient suppressor diode, about 130 V standoff | Absorbs fast spikes only; it cannot survive a sustained fault | A clamp dissipates V·I, so its energy rating limits how long it can act |
| Parts on the raw rail rated 200 V or more | They survive the clamped fault level | Rating follows the worst case, not the normal case |
| Primary current limit at 6.25 A with hiccup restart | Protects against overload and output short circuit | Cycle-by-cycle limiting bounds the energy stored in the transformer |
| Controlled start-up ramp | Prevents overshoot when the rail first rises | An integrator that has saturated needs time to recover; ramping the target avoids saturating it |

The supply's own current limit does not protect the patient. It can deliver 100 mA at over 100 V, so each pump channel needs an independent hardware current limit.

## Isolation and patient safety

The flyback's barrier gives no patient protection, because the pump, DAC, FPGA and battery grounds are joined through the signal path. An isolation barrier is only as good as every path across it. Patient protection is therefore proposed at the device boundary: the charger, any wired data link and the enclosure. The transformer can then be a catalogue part with functional isolation, and the output return is tied to battery ground at one point.

- **What crosses the barrier:** the transformer, the feedback optocoupler, the overvoltage optocoupler and the 1 nF barrier capacitor. With the grounds joined, none of them is a safety barrier.
- **When it matters:** on battery alone the device already floats. The barrier does its work when a charger, USB cable or other grounded equipment is attached.
- **Noise across the barrier:** capacitance between the windings carries switching current to the patient side (I = C·dV/dt). The barrier capacitor returns that current locally, but it is also a leakage path, so its value is a trade-off.
- **Typical requirement:** patient-connected equipment under IEC 60601-1 usually needs reinforced insulation, around 4 kV test voltage and 8 mm creepage. The applicable figures need confirming against the standard.
- **Effect on the transformer:** separating the windings for isolation raises leakage inductance. Triple-insulated wire is the usual compromise.

## Open items

- [ ] Confirm how the battery is charged and whether the FPGA has any wired link to other equipment during use; those connections now carry the patient isolation.
- [ ] Decide the raw rail setpoint: 112.6 V (lower divider resistor 2.26 kΩ, recommended) or 109.8 V (2.32 kΩ).
- [ ] Decide the turns ratio (18.6 as in WEBENCH, or 10 to match the bench stand-in), then send the transformer specification to custom winders for quotes.
- [ ] Simulate the redesigned feedback loop; it is hand-calculated only.
- [ ] Bench-check that the optocoupler can pull COMP low at its minimum current transfer ratio.
- [ ] Choose real output capacitors and re-check loop stability with them.
- [ ] Set snubber values on the bench.
- [ ] Read the ratings of the sense resistor, filter inductor, ferrite bead and input capacitors from their JLCPCB part pages, including the ripple rating of the 10 µF bulk electrolytic.
- [ ] Copy the design for the negative rail.
- [ ] Define per-channel patient current limiting.

## Inputs from the analog channel team

The analog team's records set five requirements on this supply that the first design did not include.

| Input | Their evidence | Effect on the supply | Underlying principle |
| --- | --- | --- | --- |
| Each channel draws about 5.2 mA per rail with no load | A1 record: 5.9 mA per rail at 2 mA peak, 6.8 mA at 5 mA peak, ±100 V \[L\]; idle figure derived \[H\] | 16 channels idle at about 83 mA per rail, more than the 80 mA load | Bias networks and amplifiers draw supply current whether or not the load does (Kirchhoff's current law at the rail) |
| 200 kΩ bleeder per rail on each channel board | Rev 1 edit list, R23/R24 | About 8 mA per rail across 16 boards \[H\] | Ohm's law; a bleeder trades standing power for safe discharge |
| Operating point is 5 mA into 13 kΩ or less; 10 mA is a hard fault limit only | Decision D-B | The load needs 65 V, not 100 V; a 100 V clean rail is enough | Compliance voltage is I·R at the operating point |
| Channel is specified for rails of 90–110 V | Design brief, scope | The 112.6 V raw setpoint could put up to 111 V on the channel \[H\] | A rating is a limit on the receiving side, not only the sending side |
| One rail present without the other drives the load: +23 mA with only the positive rail, −9.7 mA if it is lost | A7 record \[L\], FMEA row F04 | Both rails must rise and fall together | A bootstrapped stage needs both rails to define its operating point |
| Rail ripple reaches the load at about 17 µA per volt at 150 kHz | A8 archive figure: 0.29 Vpp gives 5 µA \[L\] | The LC filter alone gives roughly 7 nA \[H\]; the capacitance multiplier may be unnecessary | Supply rejection falls with frequency, so ripple amplitude at the switching frequency sets the residual |

Per-rail current tally \[H\]: 83 mA idle, plus 8 mA bleeders, plus 40 mA at the operating point or 80 mA at the hard limit. That is 131 mA operating and 171 mA worst case, against the 100 mA the first design assumed.

## Rail tracking options (P-6)

The choice is between regulating each rail well and making the two rails move together by construction. Leakage inductance is the link: windings that are not perfectly coupled do not share voltage perfectly, so an output that is not directly regulated drifts with load.

| Option | Transformer | Rails track | Regulation of each rail | Main cost | Underlying principle |
| --- | --- | --- | --- | --- | --- |
| A. Two independent converters with a shared enable, a shared clock and a symmetry interlock | Two catalogue parts | Only as well as the interlock makes them | Each rail has its own loop, so both are tight | A converter can still fail alone; the interlock must catch it | Two separate feedback loops share no state unless something couples them |
| B. One converter, one transformer with two secondaries | Custom | By construction: both windings see the same core flux | One rail (or the sum) is regulated; the other follows within a few percent | Custom part; one switch carries about 12 A peak \[H\] | Windings on one core share volts per turn, less the leakage between them |
| C. One converter, two catalogue transformers with primaries in parallel | Two catalogue parts | By construction: one switch feeds both | As B, but with two leakage inductances in the path | Unusual arrangement; WEBENCH cannot design it; unverified \[ASSUME\] | Parallel primaries force equal reflected voltage while both diodes conduct |

The channel loads are symmetric on average, because sourced and sunk currents sum to zero through the shared return (decision D-C). That is the favourable case for options B and C.

### Check P6: do the rails track? (14 Nov 2026)

Option C tracks well, but an open output rectifier is not covered and needs its own protection. The check is an LTspice run on the idealized controller from the earlier simulation ladder; the record is `sim_ladder/P6_rail_tracking_RECORD.md`. There is no bench twin yet.

| Condition, 9 V input | +HV | −HV | Against the 110 V limit |
| --- | --- | --- | --- |
| Both rails idle | 104.5 V | −105.9 V | Pass |
| +HV loaded 80 mA more than −HV | 104.0 V | −108.6 V | Pass, 1.4 V margin before tolerance |
| −HV loaded 80 mA more than +HV | 104.0 V | −100.7 V | Pass |
| Both at 171 mA | 104.0 V | −105.4 V | Pass |
| Start-up and shutdown | Within 2.3 V of each other |  | Pass |
| −HV rectifier fails open | 104.0 V | Falls towards zero | Not covered: one rail remains |
| +HV rectifier fails open | Falls | −191 V within 10 ms and rising | Fail |

All values are \[L\], with transformer leakage from a datasheet summary and winding resistance assumed. The underlying principle of the last row: a feedback loop corrects only what it measures. When the measured rail disappears, the loop drives full power into the rail it cannot see.

Open from this check:

- Over-voltage protection that senses each rail independently.
- Margin to 110 V on the unregulated rail: a lower setpoint, or sensing the sum of both rails so the drift is shared.
- The earlier rationale in the project folder (3 Nov 2026) chose discontinuous conduction at 500 kHz with a custom 0.75 µH transformer. Today's catalogue-transformer design runs in continuous conduction at 250 kHz. Decided 14 Nov 2026 (P-11): keep today's catalogue-transformer design, because an off-the-shelf transformer is the priority. The 3 Nov design is superseded; its simulation ladder remains the model basis.

## Validation against TI's calculator (14 Nov 2026)

Every check in TI's LM5155 flyback calculator passes once three values change: output capacitance, soft-start capacitor and slope resistor. The setpoint is now 102 V (decision P-12), to keep voltage exposure low. The record is `calc/CALC_RECORD_2026-11-14.md`.

The calculator has no model for two transformers on one switch. It was entered as the equivalent single supply: 102 V at 0.43 A through one 5 µH primary, because two equal inductors in parallel halve the inductance and share the current.

| Check | Calculator \[calc\] | Design value | Pass |
| --- | --- | --- | --- |
| Maximum duty at 9 V | 53.1% | 54% by hand \[H\] | Yes |
| Recommended primary inductance | 4.8 µH | 5 µH | Yes |
| Peak primary current, both transformers | 11.1 A, no losses | 11.7 A simulated with losses \[L\] | Yes |
| Sense resistor | 6.73 mΩ recommended | 6 mΩ, giving a 16.2 A limit | Yes |
| Worst transformer at the current limit |  | 8.9 A against a 10 A rating \[H\] | Yes |
| Slope resistor | 191 Ω needed | 200 Ω (was 100 Ω) | Yes |
| Output capacitance | 55 µF minimum | 33 µF per rail (was 22 µF) | Yes; fails at 22 µF |
| Soft-start capacitor | 157 nF minimum | 200 nF (was 10 nF) | Yes; fails at 10 nF |
| Bottom feedback resistor for 102 V | 2.497 kΩ | 2.49 kΩ | Yes |
| LED resistor | 60.8 kΩ maximum | 44.1 kΩ | Yes |
| Compensation | 20.6 kΩ and 773 nF | Superseded by P-14: 12.7 kΩ and 68 nF | Yes |
| Loop at 11.1 V | Crossover 537 Hz, phase margin 87°, gain margin 34 dB |  | Stable |

Two principles explain the changes. Slope compensation: above 50% duty a peak-current loop amplifies any disturbance from one cycle to the next unless a ramp is added to the sensed current. Compensation: the loop must be re-tuned whenever the power stage changes, because its gain depends on the sense resistor, the output capacitance and the load. The values carried over from the 100 mA design no longer apply.

## Over-voltage clamp on each rail (14 Nov 2026)

Each rail gets its own clamp at 109.8 V, built as a second copy of the feedback block with a different bottom resistor (2.32 kΩ instead of 2.49 kΩ). Each clamp's optocoupler pulls the controller's COMP pin down in parallel with the main one, so whichever block sees the highest voltage takes control.

| Choice | Why | Underlying principle |
| --- | --- | --- |
| A precision reference per rail, not a Zener | The window between the highest normal rail and the channel's 111 V protection diode is about 2 V; a 5% Zener spans 11 V | A threshold is only as good as its tolerance |
| One clamp on each rail | The main loop sees only +HV; check P6 showed −HV reaching −191 V when +HV was lost | A loop corrects only what it measures |
| Clamps act through COMP, in parallel | Any one of three blocks can reduce power; none can raise it | A wired-OR of pull-downs gives the lowest command priority |
| Clamp block referenced to its own rail | The −HV clamp sits between ground and −HV; its optocoupler carries the signal back | Optical coupling removes the need for a common reference |
| Transient suppressor kept as a backstop | Covers spikes faster than the loop | Energy rating limits it to short events |

In simulation the clamp holds −HV at −110.2 V when the +HV rectifier fails open, against −191 V without it \[L\]. The clamp there is idealized; the real block is not yet simulated.

At the 102 V setpoint with 33 µF per rail, the same simulation gives these rail voltages at 9 V input \[L\]:

| Condition | +HV | −HV | Margin |
| --- | --- | --- | --- |
| Both rails idle | 102.0 V | −103.0 V | 7 V under the 110 V limit |
| +HV loaded 80 mA more | 102.0 V | −106.2 V | 3.8 V under the limit |
| −HV loaded 80 mA more | 102.0 V | −99.5 V | 9.5 V over the channel's 90 V minimum |
| Both at 171 mA | 102.0 V | −102.6 V | 7 V under the limit |
| +HV rectifier open, clamp acting | Falls | −110.2 V | 0.8 V under the 111 V protection diode |

The 2 V given up by moving from 104 V to 102 V is not critical: the lowest rail in normal operation is 99.5 V, and the channel is specified down to 90 V with an operating load that needs 65 V (decision D-B). The clamp window is the tight spot. With a 0.5% reference and 0.1% resistors the clamp threshold spans 109.0–110.6 V \[H\], between a highest normal rail of 107.9 V and the diode's 111 V.

The clamp block's compensation is still open. The main block's 820 nF capacitor would make a clamp respond in about a second \[H\], while the faulted rail rises about 9 V per millisecond \[L\]. A clamp must act as a fast comparator, so it needs a much smaller capacitor and its own simulation. The principle: a compensator tuned for steady regulation is deliberately slow, and a protection circuit has the opposite job.

The component-level changes from the WEBENCH schematic are listed in `SCHEMATIC_CHANGES_2026-11-14.md` in the project folder.

### Check P7: the real clamp block (14 Nov 2026)

A clamp that regulates through COMP is too slow for the 2 V window: the faulted rail overshoots to −114.8 V before settling at −110.7 V. The record is `sim_ladder/P7_clamp_real_RECORD.md`. Four of six cases completed; the fastest compensation did not finish and has no result.

| Clamp compensation | −HV peak, +HV rectifier open | −HV peak, main optocoupler open | Settled behaviour |
| --- | --- | --- | --- |
| 68 kΩ with 1 nF | −114.8 V | −115.6 V | −110.7 V steady; 2–3 V oscillation with the main optocoupler open |
| 68 kΩ with 4.7 nF | −118.4 V | −120.4 V | −112.4 V, still settling; 3–5 V oscillation |

All values are \[L\] at 9 V input with the weakest optocoupler. Before the fault the real main loop holds +101.9 V and −106.5 V under the worst load imbalance, and the clamps take no action.

The limit is structural. To act within 1 V a clamp needs high gain, and a high-gain loop around this power stage is unstable. With low gain it must integrate, and its output node has about 80 V to travel. The principle: a feedback loop trades speed against stability, and a protection threshold only 2 V above normal operation asks for both.

Decision P-13 (taken, see below) was whether to accept a brief overshoot to about 115 V, or change the clamp from a regulator to a trip that latches the converter off. A trip has no loop to stabilise, so it can be a fast comparator, and it leaves both rails decaying together.

### Decision P-13 and check P8: trip and latch off (14 Nov 2026)

The clamp on each rail is now a trip: when a rail passes 109.8 V the converter is stopped and latched off until the battery is disconnected. In simulation the faulted rail peaks at −110.06 V, against −114.8 V for the regulating clamp. The record is `sim_ladder/P8_trip_latch_RECORD.md`.

| Fault | Rail peak | Time to trip | Afterwards |
| --- | --- | --- | --- |
| +HV rectifier fails open | −110.06 V | 0.48 ms | Converter held off; rails decaying |
| Main optocoupler fails open | +104.5 V and −109.97 V | 1.13 ms | Converter held off; rails decaying |

All values are \[L\] at 9 V input with the weakest optocoupler. There is no false trip at the worst normal load imbalance.

| Choice | Why | Underlying principle |
| --- | --- | --- |
| Trip, not regulate | A comparator has no loop to stabilise, so it can be as fast as its parts allow | Positive feedback (a latch) is decisive where negative feedback must be slow to stay stable |
| One optocoupler current does two jobs | It pulls COMP down, stopping the next switching cycle, and fires the latch | The fastest path acts first; the latching path makes it permanent |
| Latch across the UVLO pin, held by the battery | The controller's own enable input keeps it off, and the hold does not depend on the converter running | A latch needs holding current from a source that survives the shutdown |
| Reset only by removing the battery | A fault that trips the supply should be looked at before it runs again | Fail-safe: the default state after a fault is off |
| Small filter on the reference pin | Keeps switching ripple from tripping it | A low-pass filter trades a few microseconds of delay for noise immunity |

After a trip both rails fall together, which also avoids the single-rail condition the analog team's A7 test warns about. The system needs a way to tell the operator that the supply has tripped.

## JLCPCB library check (14 Nov 2026)

The transformer is the one part that cannot come from the JLCPCB library; three others need a library substitute. The full list is in `JLCPCB_CHECK_2026-11-14.md` in the project folder. Lookups used [jlcsearch.tscircuit.com](https://jlcsearch.tscircuit.com/), a third-party mirror of the library, so each part needs confirming on JLCPCB's own site before ordering.

| Part | In library | Nearest alternative | Consequence |
| --- | --- | --- | --- |
| Coilcraft DA2034-AL transformer | No | DA2032-ALD, the 3 A member of the family | Too small; buy DA2034-AL separately and hand-fit or consign |
| CSD19502Q5B switch | No | CSD19531Q5A, 100 V, 5.3 mΩ at 10 V | Check its on-resistance at the controller's gate-drive voltage |
| TCMT1107 optocoupler | No | TCMT1103, 1106, 1108, 1109 or TLP291 | A different transfer-ratio grade changes loop gain; re-run the calculator |
| SMBJ120A transient suppressor | No | SMBJ130A | Acceptable as a backstop |
| Controller, reference, shielding transistor, Zener, output diode, latch transistors, 0.1% divider resistors | Yes |  | None |

A second pass on JLCPCB's own site found the high-voltage capacitors, the sense resistor, the filter inductor, the ferrite bead and the special resistor values in stock. Two consequences: the 1 µF, 250 V ceramic is an 1812 part, and the 200 V bulk capacitors are through-hole only, with the 33 µF value in low stock. Three 10 µF parts per rail are the better-stocked route. Ratings on the sense resistor, inductor and bead still need reading from their part pages.

### Substitutes adopted and compensation corrected (P-14, 14 Nov 2026)

The switch is now CSD19531Q5A and all three optocouplers are TCMT1108, both in the JLCPCB library. Re-running TI's calculator with them gives a main compensation of 12.7 kΩ and 68 nF. This replaces the 820 nF value stated earlier in this document, which came from misreading the calculator: its capacitor value depends on the resistor selected, and that cell held a stale value.

| Item | Value | Source |
| --- | --- | --- |
| Switch on-resistance at 6 V gate drive | 6.0 mΩ typical, 7.8 mΩ maximum; 0.27–0.35 W conduction loss | \[DS\]; \[H\] |
| Optocoupler transfer ratio | 130–260% at 5 mA; 1.0 assumed as the minimum at 1–2 mA | \[DS\]; \[ASSUME\] |
| LED resistor limit | 76 kΩ maximum against 44.1 kΩ fitted | \[calc\] |
| Main compensation | 12.7 kΩ and 68 nF at 250 V | \[calc\] |
| Loop at 9, 11.1 and 12.6 V | Crossover 661–776 Hz, phase margin 80°, gain margin 30 dB or more | \[calc\] |

The principle behind the optocoupler change: its current transfer ratio is a gain inside the loop, so a different grade changes both how hard the LED must be driven and how much the compensation must attenuate.

The trip simulation (P8) was run with the earlier compensation and the weaker optocoupler. A re-run with these values stalled in the solver and was stopped, so the trip result has not been reproduced with the current values.

### Output bulk capacitor (P-15, 14 Nov 2026)

Each rail uses three 10 µF, 200 V electrolytics plus a 1 µF, 250 V ceramic, in place of one 33 µF part that JLCPCB stocks thinly. The total of 62 µF across both rails meets the calculator's 55 µF minimum, and the loop stays stable: crossover 708–832 Hz, phase margin 88° or more, gain margin 26 dB or more \[calc\]. The electrolytics' series resistance was assumed at 3 Ω each.

The principle: capacitors in parallel add their capacitance and divide their series resistance, so several small parts can replace one large one. The ceramic carries the switching-frequency ripple, because an electrolytic's series resistance makes it a poor path at 250 kHz. The electrolytics are through-hole parts.

### Transformer datasheet check (14 Nov 2026)

The Coilcraft DA2034-AL datasheet confirms every figure the design relied on, and adds one constraint: the part may not be used in medical applications without Coilcraft's approval. The record is `DA2034_DATASHEET_CHECK_2026-11-14.md`; the source is [Coilcraft Document 510](https://www.coilcraft.com/getmedia/88ef6a9b-3558-4004-8c5f-af97c95c7e8c/da2032.pdf), revised 7 March 2025.

| Parameter | Datasheet \[DS\] | Effect on the design |
| --- | --- | --- |
| Primary inductance | 10.0 µH ±10%; at least 9.0 µH at 10 A | As assumed; 8.9 A reaches the worse transformer at the current limit \[H\] |
| Turns ratio | 1:10 | As assumed |
| Winding resistance, maximum | 0.018 Ω primary, 1.75 Ω secondary | About 0.4 W copper loss per transformer \[H\] |
| Leakage inductance, maximum | 0.250 µH | Primary clamp loss at the top of the 2–4.5 W estimate \[H\] |
| Interwinding capacitance | 128 pF | Roughly 0.5–1 W extra switching loss per transformer \[H\], not in the simulation |
| Isolation | 1500 Vrms, one minute | Functional only, as decided in P-3 |
| Intended use | 3–24 V input, 300 V output | This design is inside that range |

The principle behind the capacitance row: a capacitor charged and discharged through a switch loses C·V² of energy every cycle, whatever the resistance in the path, so the loss rises with voltage squared and with frequency. The part was designed for a converter that switches when its voltage is low; this design switches it hard at 250 kHz.

## Final pre-layout simulation (P9, 15 Nov 2026)

With the JLCPCB parts, the datasheet transformer values and an assumed core loss in one model, the supply regulates, trips on both faults and reaches 86.5% efficiency at 9 V and full load. It also shows four problems that need a decision before layout. The record is `sim_ladder/P9_final_RECORD.md`; values are \[L\].

| Finding at 9 V, 171 mA per rail | As designed | With a 2.2 nF sense filter | Limit |
| --- | --- | --- | --- |
| Switching pattern | A pulse skipped every 5–6 cycles | Regular, 2.18 µs every cycle | Regular |
| Ripple after the LC filter | 85–93 mV peak to peak | 6–7 mV peak to peak |  |
| Unregulated rail relative to the regulated one | 5.0 V lower | 6.7 V lower | 90 V minimum at the channel |
| Switch peak current | 14.5 A | 14.2 A | 16.2 A limit |
| Rectifier reverse voltage | 394 V | 389 V; 470 V at 12.6 V input | 600 V part |
| Battery terminal voltage | 8.47 V | 8.48 V | Lockout releases at 8.17 V |
| Efficiency |  | 86.5% (36.4 W in, 31.5 W out) |  |

| Open decision | Options | Underlying principle |
| --- | --- | --- |
| P-16: sense filter capacitor | 470 pF · 2.2 nF | Charging the winding capacitance at turn-on draws a current spike; a comparator that sees it ends the pulse early, so the filter must outlast the spike |
| P-17: unregulated rail 5–7 V low at full load | Accept · raise the setpoint · sense the sum of both rails | Winding resistance, diode drop and leakage all subtract from the rail the loop does not watch |
| P-18: undervoltage lockout too close to the sagging battery | Keep 8.5 / 8.0 V · lower to about 7.5 / 7.0 V | A source has internal resistance, so its terminal voltage falls with current (V = E − I·R) |
| P-19: load rating | 215 mA per rail · 171 mA per rail at 9 V | Power out is limited by peak current, and losses raise the peak current needed for a given load |

Both faults trip and latch: 1.4 ms after the +HV rectifier opens and 6.6 ms after the main optocoupler opens. The trip level in this model reads about 2 V low, because the reference model turns on softly, so the 111 V check rests on the earlier P8 run. Start-up was simulated without soft start, as a worst case: it ran at the current limit for more than 14 ms without finishing, and the battery sagged to within 8 mV of the lockout threshold.

Decision P-16 (15 Nov 2026): the sense filter capacitor is 2.2 nF. The cost is a current limit that acts about 0.35 µs later, which lets the current run roughly 0.6 A past the limit \[H\]. That puts the worse transformer near 9.3 A against its 10 A rating, so the margin there is thin. P-17, P-18 and P-19 remain open.

Decision P-17 (15 Nov 2026): the lower unregulated rail is accepted. A Howland pump sets its current from the command and its sense resistor, so the rails matter only at the voltage limit. Sinking channels therefore lose 5–7 V of reach, about 1.2 kΩ of load at 5 mA \[H\], and still cover the analog team's 5 mA into 13 kΩ with a rail as low as 90 V. If an electrode's resistance rises, a sinking channel now clips before a sourcing one, and the difference flows in the shared return electrode.

Decision P-18 (15 Nov 2026): the undervoltage lockout turns on at 7.5 V and off at 7.0 V, using 49.9 kΩ and 12.4 kΩ \[calc\]. That leaves 1.4 V of margin at full load and 1.1 V during start-up. The cost: 7.0 V is below a three-cell lithium-ion pack's safe minimum of about 9 V, so the lockout no longer protects the battery from over-discharge. The pack's own protection circuit has to do that. P-19 follows.

Decision P-19 (15 Nov 2026): the supply is rated at 171 mA per rail at 9 V input, replacing the 215 mA of P-4. That figure is the worst-case load itself: 83 mA of channel idle current, 8 mA of bleeders and 80 mA with all eight sourcing channels at their 10 mA hard limit. There is no load margin above it at minimum battery, only 12% of current-limit headroom \[L\]. At the 5 mA operating point the load is 131 mA per rail, which leaves room. The principle: a peak-current-limited converter delivers a fixed maximum power, and real losses and battery sag use up part of it.

## Consolidated design for layout (15 Nov 2026)

The parts, values and connections that result from decisions P-1 to P-19 are gathered in one file, `FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md` in the project folder. It is the list to capture the schematic from. The changes list keeps the history and the evidence.

| Item | Final value |
| --- | --- |
| Outputs | +102.5 V regulated; −HV follows, 5–7 V lower at full load |
| Rated load | 171 mA per rail at 9 V input |
| Converter | One LM51551 and one CSD19531Q5A switch driving two Coilcraft DA2034-AL transformers |
| Efficiency at 9 V and full load | 86.5% \[L\] |
| Ripple after the filter | 6–7 mV peak to peak \[L\] |
| Protection | Trip at 109.8 V on either rail, latched off until the battery is removed |

Five things are outside this design and still need an owner: the battery connector with its fuse, the output connectors, battery over-discharge protection, the low-voltage rails for the channel boards, and an indication that the supply has tripped.

### Stock and ratings pass (15 Nov 2026)

Opening each part's own JLCPCB page showed that several first choices had almost no stock, and that no 100 µF polymer input capacitor is available. The clamp parts are now chosen and every outstanding rating is read.

| Item | Outcome | Underlying principle |
| --- | --- | --- |
| Sense resistor | 6 mΩ, 3 W part with 3,872 in stock; it dissipates 0.24 W \[L\] | P = I²R; a rating many times the dissipation keeps the part cool and its value stable |
| Filter inductor | Saturation 1.15 A against a 0.17 A load | An inductor only filters while its core is unsaturated |
| Bulk output capacitors | 10 µF part rated 180 mA at 100 kHz; about 50 mA each expected \[H\] | Ripple current heats a capacitor through its series resistance |
| Input capacitors | Eight 10 µF ceramics carry the ripple; one 330 µF electrolytic damps them | A low-loss capacitor and lead inductance resonate; a lossy capacitor in parallel absorbs the energy |
| Primary clamp | 100 V, 5 A Schottky diode; three 300 Ω, 2 W resistors in parallel | Parallel resistors share power equally, so three bodies run at a third of the heat each |
| 110 kΩ and 7.32 kΩ resistors | Swapped to well-stocked equivalents |  |

The input capacitor change is the only electrical change, and it has not been re-simulated. Expected input ripple is about 0.2 V \[H\].

### Re-run with the new input capacitors, and a start-up finding (15 Nov 2026)

The new input capacitors behave as estimated, but a longer start-up run showed that the supply trips its own latch at power-up unless a start-up network is fitted. With the network fitted it starts cleanly, and a second problem appears: start-up current above the transformers' rating. That one is open as P-20. The record is the revision section of `sim_ladder/P9_final_RECORD.md`; values are \[L\].

| Check | Result | Verdict |
| --- | --- | --- |
| Input ripple with eight ceramics and one electrolytic | 0.21 V peak to peak; ceramics carry 0.6 A RMS each | As estimated |
| Steady state at 9 V, 171 mA per rail | Regular switching, 86.7% efficiency | Unchanged |
| Start-up without the start-up network | +HV reaches 107.4 V and the latch trips at 15.5 ms | Fails |
| Start-up with the network (two 499 kΩ, 2.2 µF, two BAS21 diodes) | No overshoot, no trip, settled in about 40 ms | Passes |
| Current during the first 9 ms of start-up | 26 A in the switch; 12.4 and 14.6 A in the transformers | Fails the 10 A rating |

Two principles are at work. A compensator tuned for small disturbances is an integrator, and an integrator recovers slowly from a large one; the start-up network removes the large disturbance by starting the loop already in control. And a flyback needs output voltage to reset its transformer, so at start-up, with the output near zero, each pulse adds current that the off-time cannot remove. The larger sense filter chosen in P-16 lengthens the shortest pulse the controller can make, which makes this worse: it was 19.6 A with the original 470 pF.

### Soft start and the path to layout (16 Nov 2026)

A primary-side soft start removes the initial surge (4–8 A in the first milliseconds instead of 26 A), but with a 220 nF capacitor it ramps faster than the rail can follow and reaches the current limit again by 16 ms \[L\]. The LM51551 shuts down for 32,768 cycles after 64 cycles at the limit, so the ramp must be slower; about 1 µF is to be simulated. The principle: a soft start trades start-up time for peak current, and it only works if the commanded current rises no faster than the output can absorb it.

Five items block layout because they change parts, footprints or connectors: the soft-start capacitor; the interface with the analog board (power connector, and his expectation of +12 V, −12 V and +5 V from this board); the battery-side protection and board outline; the transformer footprint, which has to be drawn; and the creepage rule for the 390–470 V rectifier nodes. The full list is section 0 of `FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md`.

Decisions on 16 Nov 2026:

| ID | Decision |
| --- | --- |
| P-21 | Off-the-shelf ±12 V regulator and a 5 V supply, which the analog board's aux connector expects; parts not yet chosen |
| P-22 | Connectors to the analog board laid out as they are; agreed with its owner later |
| P-23 | Rev 1 runs from a bench supply; battery-side protection deferred to Rev 2 |
| P-24 | Transformer stays the Coilcraft DA2034-ALD, bought outside JLCPCB and hand-soldered; LCSC has 12 in stock plus 864 through another supplier |

The layout follows JLCPCB's rules. Those are manufacturing minimums rather than voltage clearances, so the high-voltage nets get extra room where the board allows: the gap a voltage can arc across depends on the voltage, not on what the factory can etch.

### Soft-start capacitor results (16 Nov 2026)

Both 470 nF and 1 µF start the supply without a single cycle at the current limit, so the LM51551's hiccup protection is never triggered. They trade one margin for another \[L\]:

| Soft-start capacitor | Transformer peak | +HV overshoot | Time to 100 V |
| --- | --- | --- | --- |
| 220 nF | At the current limit by 16 ms | Not reached |  |
| 470 nF | 9.3 A of 10 A | None | 55 ms |
| 1 µF | 7.8 A of 10 A | 3.7 V, about 2.8 V below the lowest trip level | 71 ms |

A cycle counts as at the limit at 98 mV or more, and a gap of fewer than eight normal cycles does not reset the count. The principle: a slower ramp lowers the current the converter asks for during start-up, but it also changes when the feedback loop takes over, which is what sets the overshoot.

A third run at 680 nF combines the strengths of both: no cycles at the current limit, transformer peaks of 8.0 and 8.6 A, no overshoot (the rail peaks at 100.6 V and settles at 100.4 V in the model), and 100 V reached at 54 ms \[L\]. A ±10% capacitor spans 612–748 nF, so the part's tolerance stays inside a range whose ends have both been shown to work. The principle: when a value has to sit between two failure modes, choose it so that its tolerance band lies inside the region you have tested on both sides.

Decision P-20 (16 Nov 2026): the supply uses a primary-side soft start, one MMBT3906 transistor clamping COMP to the soft-start capacitor, with that capacitor at 680 nF. This closes the start-up current issue.

## Schematic (16 Nov 2026)

The Rev 1 schematic is generated in KiCad 10 from the consolidated parts list, and KiCad's own checks agree with it: zero rule violations, and its exported netlist matches the parts list on every one of 298 pins. The transformer pinout and footprint came from LCSC's data for the DA2034-ALD; the controller, reference and optocoupler pinouts were checked against their manufacturers' datasheets.

The principle: generating the schematic from the parts list, then comparing the netlist KiCad produces back against that list, turns a visual review of hundreds of connections into a mechanical check that cannot miss one. Each pin carries a net label for now, so the drawing is correct but still needs tidying into readable wiring.

## Decision log

Taken decisions and open questions, in the analog team's format. Open rows are for the power-board owner to decide.

| ID | Date | Question | Options | Evidence | Choice |
| --- | --- | --- | --- | --- | --- |
| P-1 | 14 Nov 2026 | Converter topology | Boost · isolated flyback | WEBENCH design 6 \[WB\]; hand checks \[H\] | Isolated flyback, LM51551, feedback sensed on the output side |
| P-2 | 14 Nov 2026 | Feedback block over-voltaged at 110 V | Low-voltage bias rail · cascode transistor | Schematic reading; hand calculation \[H\], not simulated | Cascode, with TI's compensation kept |
| P-3 | 14 Nov 2026 | Where patient isolation sits | Reinforced transformer · device boundary | Grounds joined through DAC and FPGA (ICD J3) | Proposed: device boundary; transformer functional only |
| P-4 | Open | Per-rail current rating | 100 mA · about 215 mA (171 mA plus 25%) · lower the channel idle current first | Tally above \[H\] from A1 \[L\] | 215 mA per rail; channel idle current cannot be reduced |
| P-5 | Open | Rail setpoint | 112.6 V raw for 105 V clean · about 104 V raw for 100 V clean | D-B; channel range 90–110 V | 104 V |
| P-6 | Open | How the two rails track | Two independent converters · one controller with two transformers · one transformer with two secondaries | A7 \[L\]; F04 | C: one converter, two catalogue transformers with primaries in parallel (14 Nov 2026). Removes single-converter faults by construction; drift on the unregulated rail accepted. LTspice check P6 to follow |
| P-7 | Open | Post-filter | LC only · LC plus capacitance multiplier | A8 \[L\]; needs repeating at 252 kHz | LC only; capacitance multiplier dropped. A8 still to be repeated at the switching frequency |
| P-8 | Open | Battery | Three-cell lithium-ion, 9–12.6 V · two 9 V alkaline cells (earlier team documents) | About 45 W output at the higher current \[H\] | Three-cell lithium-ion on the power-board side; the analog team's documents still say two 9 V cells |
| P-9 | Open | Channel count for sizing | 16 · 4 with 8 as a stretch (analog team documents) | Plan and proposal comparison | 16 |
| P-10 | Open | Low-voltage rails for the channel boards (+12 V, +5 V at J2) | From this board · from elsewhere | Rev 1 design definition, sheet 4 | Off-the-shelf regulator fed from the battery, not from this board |

## 9 V aux rail for the analog board (P-25, 22 Nov 2026)

The analog board now takes +9 V instead of +12 V, so a 9 V low-dropout regulator (LM2940IMP-9.0) on this board, fed straight from the battery, replaces the planned ±12 V regulator. It is rated 250 mA, and it leaves the ±102 V supply effectively unchanged \[H\]:

| Check | At 250 mA aux load |
| --- | --- |
| Extra battery current | 265 mA, 6% of the flyback's 4.3 A |
| Extra sag at the battery terminal | 32 mV |
| Undervoltage lockout margin | 1.33 V to 1.30 V at full load |
| HV trip and latch | 9 V stays up when the HV supply latches off |
| LDO dissipation at 12.6 V in | 1.1 W, junction 65 °C above ambient |

| Choice | Why | Underlying principle |
| --- | --- | --- |
| Linear regulator, not a switcher | No new switching noise on the analog board's supply | A linear regulator drops the excess voltage as heat instead of chopping it |
| Ferrite bead and 10 µF before it | Keeps the flyback's 252 kHz input ripple out of the regulator | A series impedance and a shunt capacitor form a low-pass filter |
| 330 µF electrolytic output capacitor, not ceramic | The LM2940 is only stable with 0.1–1 Ω of capacitor ESR | The capacitor's resistance adds a zero that keeps the regulator's loop stable |
| Fed from the battery, not switched by the HV lockout | Low-voltage electronics are powered before the HV and stay powered after a trip | Sequencing: control circuits should be alive whenever high voltage can be present |

The limitation: the regulator needs about 9.2 V in to hold 9 V, so near an empty battery the rail sits a few hundred millivolts low (8.4 V at 8.5 V in). On the Rev 1 bench supply set to 10.5 V or more it is fully regulated. The analog board's 9 V load current is still to be confirmed. The record is `calc/AUX_9V_LDO_RECORD_2026-11-22.md`.
