# P9 Final pre-layout simulation — record

**Question.** With the JLCPCB parts, the datasheet transformer values, core loss and the other non-idealities in one model, does the option C supply still regulate, trip and start, and what does it cost in efficiency and ripple?
**Status.** sim done 2026-11-15 (LTspice 26.1.1, batch, eight runs) · bench pending

## Setup
| | Sim [L] | Bench [B] |
|---|---|---|
| Circuit | `P9_final.net` (base); one file per run, `P9_run_M1…M7.net`, `P9_run_M4L.net` | power board |
| Switch | CSD19531Q5A as a VDMOS model: 6 mΩ at 6 V drive, 37 nC [DS]; capacitances [ASSUME] | |
| Transformers | 2 × DA2034-AL [DS]: 11 µH and 9 µH (±10 %), 1:10, 18 mΩ / 1.75 Ω, 0.25 µH leakage, 128 pF interwinding (half lumped to the hot secondary end [ASSUME]); core loss 230 Ω across the primaries, about 0.37 W total [ASSUME: not on the datasheet] | |
| Rectifiers, snubbers | ES1J model [ASSUME parameters]; 220 Ω + 22 pF across each; primary clamp 100 Ω + 100 nF | |
| Output | 3 × 10 µF at 3 Ω each [ASSUME] + 1 µF X7R derated to 0.45 µF [ASSUME]; LC filter 100 µH (0.35 Ω) + 0.45 µF + damping; SMBJ130A | |
| Feedback and trip | TL431B, MMBTA42 cascode, TCMT1108 at CTR 1.0 with a 3 µs response [ASSUME]; main 12.7 kΩ + 68 nF; trip blocks 2.32 kΩ, 22 kΩ, 4.7 nF; latch MMBT3904/3906 across UVLO | |
| Controller | idealized PWM with TI-model thresholds, 46 mV slope ramp, 120 ns blanking [ASSUME], 16.7 A nominal limit; **no soft start** | |
| Source | 9 V or 12.6 V behind 0.12 Ω and 200 nH [ASSUME]; UVLO divider 44.2 kΩ / 9.53 kΩ | |
| Not modelled | filter-inductor self-capacitance, ferrite-bead loss, sense-resistor inductance, PCB parasitics, temperature, CTR versus LED current, transformer saturation | |

Runs: M1 9 V load steps (6 ms) · M2 12.6 V load steps · M3 +HV rectifier opens · M4 / M4L main optocoupler opens (5 ms / 14 ms) · M5 start-up from zero, no soft start (14 ms) · M6 9 V, 171 mA per rail, as designed, run to settle (stopped at 15.8 ms once settled) · M7 as M6 with the current-sense filter capacitor raised from 470 pF to 2.2 nF (12 ms).

## Result
### Steady state, 9 V, 171 mA per rail
| Quantity | As designed (M6, 470 pF) | With 2.2 nF sense filter (M7) | Limit | Pass |
|---|---|---|---|---|
| Switching pattern | **a pulse is skipped every 5–6 cycles** (on-times 2.2 µs, then 0.01 µs) | every cycle 2.18 µs | regular | **no** / yes |
| +HV (regulated) | 100.35 V | 100.35 V | — | see caveat 1: about 102.5 V with a real TL431 |
| −HV (follows) | −95.4 V, **5.0 V below +HV** | −93.7 V, **6.7 V below +HV** | 90 V minimum at the channel | yes, with little margin |
| Ripple after the LC filter | 85–93 mV p-p (9 mV at the switching frequency, the rest a slower wander from the skipped pulses) | **6–7 mV p-p** | — | |
| Ripple before the filter | 0.48–0.53 V p-p | 0.39–0.41 V p-p | — | |
| Switch peak current | 14.5 A | 14.2 A | 16.2 A limit | yes, 12 % headroom |
| Transformer peak currents | 7.4 / 7.7 A (includes ringing) | 7.2 / 7.4 A | 10 A [DS] | yes |
| Switch voltage peak | 22 V | 23 V | 100 V | yes |
| Rectifier reverse voltage peak | 394 V | **389 V** (470 V at 12.6 V in M2) | 600 V | yes, but 1.7–2× the 228 V calculated |
| Battery terminal voltage | 8.47 V | 8.48 V | UVLO falls out at 8.17 V | 0.3 V margin |
| Input power / output power / efficiency | — (run stopped) | 36.4 W / 31.5 W / **86.5 %** | — | |
| Cascode node (KC) | 25 V | 25.1 V | above 12 V | yes |

Loss breakdown at 86.5 % (M7): primary clamp 1.34 W, switch 0.37 W, core 0.37 W [ASSUME], rectifiers 0.38 W, sense resistor 0.24 W; the remaining 2.2 W is winding resistance, feedback standing current, snubbers and capacitor series resistance.

### Faults (9 V, 171 / 131 mA)
| Quantity | +HV rectifier opens (M3) | Main optocoupler opens (M4L) | Limit | Pass |
|---|---|---|---|---|
| Trip and latch | yes, 1.4 ms after the fault | yes, 6.6 ms after the fault | must trip | yes |
| Rail peaks (+ / −) | +101.8 / −107.7 V | +107.3 / −107.0 V | 111 V | yes — but see caveat 2 |
| UVLO after trip | 0.63 V, held | 0.62 V, held | below 1.45 V | yes |
| False trips in M1, M2, M6, M7 | none | | none | yes |

### Start-up from zero, 9 V, no soft start (M5)
| Quantity | Sim | Pass |
|---|---|---|
| Rails after 14 ms | +97.8 / −92.5 V, still rising at the current limit | not finished |
| Switch current during start-up | 16–19.6 A peak; transformers 8.9 / 9.1 A | yes, under 10 A |
| Battery terminal voltage | sags to **8.16 V**; UVLO pin 1.458 V against a 1.45 V falling threshold | **8 mV from locking out** |
| Latch at battery connection (0.2 ms ramp) | gate stays at 0.5 mV | yes |

## Verdict
The design regulates, trips on both faults and does not false-trip with realistic parts, and it reaches 86.5 % efficiency at 9 V and full load. Four things need a decision before layout: (1) as designed the controller skips pulses, because the turn-on current spike from the winding capacitance and rectifier recovery passes the 94 ns sense filter; a 2.2 nF filter capacitor removes it in simulation and cuts filtered ripple from about 90 mV to 7 mV; (2) the unregulated rail sits 5–7 V below the regulated one at full load, not above it as the idealized runs showed; (3) the undervoltage lockout at 8.5 / 8.0 V is too close to the sagging battery, 0.3 V at full load and 8 mV during start-up; (4) the switch runs at 88 % of its current limit at 171 mA per rail, so the 215 mA sizing target is not reachable at 9 V with these transformers.

## What it changes
- Proposed: current-sense filter capacitor 470 pF → 2.2 nF (decision needed; it also slows the current limit by about 0.35 µs).
- Decision needed on the unregulated rail: accept about 94–95 V at full load, raise the setpoint, or sense the sum of both rails.
- Decision needed on the UVLO thresholds, and on adding a soft start so start-up does not run at the current limit.
- The 600 V rectifier stays; the snubber needs tuning on the bench because the reverse voltage rings to 390–470 V.
- The 215 mA figure (P-4) cannot be met at 9 V; 171 mA, the real worst-case load, can.

## Revision 2026-11-15 (later): new input capacitors, lockout, sense filter, and start-up

`P9_final.net` now carries Ccs 2.2 nF, UVLO 49.9 kΩ / 12.4 kΩ, input capacitors 40 µF ceramic [ASSUME derating] + 330 µF at 0.25 Ω [ASSUME], and the start-up network. Runs: N1 (9 V, 171 mA per rail, 12 ms), N5 / N5b (start-up without the network, 14 / 20 ms), N6 (start-up with the network, 40 ms).

| Quantity | Result | Limit | Pass |
|---|---|---|---|
| N1: switching, rails, efficiency | regular 2.18 µs; +100.35 / −93.9 V; 86.7 % | — | unchanged from M7 |
| N1: input ripple | 0.21 V p-p | — | as estimated |
| N1: ripple current in the ceramics / the electrolytic | 4.81 A RMS (0.6 A each) / 0.23 A RMS | — | electrolytic rating not read |
| N1: battery terminal / UVLO pin | 8.37 V minimum / 1.68 V | 1.45 V | yes, 1.3 V of battery margin |
| N5b: start-up **without** the start-up network | +HV passes the setpoint with COMP still at maximum, reaches **107.4 V, latch trips at 15.5 ms** | must start | **no** |
| N6: start-up **with** R21 998 kΩ, C21 1.3 µF, D21, D22 | COMP leaves its maximum at 9 ms; +HV max 100.28 V (no overshoot), −HV min −97.4 V; no trip; settled by 40 ms | must start | yes |
| N6: battery terminal / UVLO pin during start-up | 8.08 V / 1.63 V | 1.45 V | yes |
| N6: currents during the first 9 ms | **switch 26.2 A; transformers 12.4 / 14.6 A** | 16.2 A limit; 10 A each [DS] | **no** |

**Why start-up overshoots without the network.** The calculator's compensation makes the reference an integrator with a 6.8 ms time constant and a proportional gain of 0.13. At power-up its output node sits about 27 V from its operating value and moves at under 1 V/ms, so the optocoupler does not take control before the trip level.

**Why the start-up current exceeds the limit.** With the output near zero the transformers have almost no voltage to reset against, so each minimum-length pulse adds current that the off-time does not remove. The 2.2 nF sense filter lengthens that minimum pulse. With 470 pF the same condition gave 19.6 A (M5). This is open as P-20.

## Revision 2026-11-15/16: primary-side soft start (P-20), partial

`P9_final_softstart.net` = `P9_final.net` plus a PNP (MMBT3906) from COMP to GND with its base on a 220 nF soft-start capacitor charged at 10 µA once UVLO is released; the COMP pull-up and error-amp current are also gated on UVLO so the model starts from rest. Run `P9_run_N7.net` (start-up, 9 V, 91 mA per rail). **The run stopped at 18.1 ms**: the computer slept and the monitor's time limit ended it. The end of start-up was not reached.

| t (ms) | +HV (V) | COMP (V) | Switch peak (A) | Transformer peaks (A) |
|---|---|---|---|---|
| 0.5 | 1.3 | 0.76 | 8.0 | 3.8 / 4.5 |
| 4 | 6.3 | 1.03 | 3.8 | 1.8 / 2.2 |
| 8 | 9.0 | 1.32 | 7.6 | 3.6 / 4.4 |
| 12 | 29.5 | 1.60 | 12.6 | 5.9 / 7.0 |
| 16 | 56.4 | 1.84 | **16.9 (at the limit)** | 8.7 / 8.7 |

- The initial surge is gone: 4–8 A in the first milliseconds instead of 26 A.
- The 220 nF ramp is faster than the rail can follow. By 16 ms COMP has reached the current-limit level with the rail at 56 V, so the switch is back at the limit, though the transformers stay under 10 A.
- The LM51551 has hiccup protection ([TI E2E](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/951372/lm5155-what-is-different-between-lm5155-and-lm51551)): 64 cycles at the limit (0.26 ms) would stop it for 32,768 cycles. A slower ramp (larger capacitor, about 1 µF [H, untested]) should keep COMP below the limit until the loop takes over. **Open.**

## Revision 2026-11-16: soft-start capacitor 470 nF and 1 µF (P-20)

Runs `P9_run_S470.net` (70 ms) and `P9_run_S1u.net` (110 ms): start-up from zero at 9 V, 91 mA per rail, start-up network fitted. Analysed with `softstart_check.py`: per-cycle CS peak, a cycle counts as at the limit at 98 mV or more, and fewer than 8 normal cycles in a row do not reset the count [ASSUME from the datasheet figure]. Hiccup at 64.

| Quantity | 220 nF (N7, partial) | 470 nF | 1 µF | Limit |
|---|---|---|---|---|
| Cycles at the current limit (longest run) | at the limit by 16 ms | **0** | **0** | under 64 |
| Transformer peaks | 8.7 / 8.7 A by 16 ms | 8.6 / **9.3 A** | 7.6 / 7.8 A | 10 A [DS] |
| Switch peak (includes turn-on spike) | 16.9 A | 16.4 A | 14.6 A | — |
| +HV maximum | not reached | **100.5 V** (no overshoot) | **104.1 V** (3.7 V overshoot) | trip 109.0–110.6 V |
| +HV reaches 100 V | — | 55 ms | 71 ms | — |
| Latch gate maximum | — | 1 mV | 1 mV | fires near 0.6 V |
| UVLO pin minimum | — | 1.65 V | 1.68 V | 1.45 V |

**680 nF** (`P9_run_S680.net`, 90 ms, completed): 0 cycles at the limit; transformer peaks 8.0 / 8.6 A; switch peak 15.3 A; +HV reaches 100 V at 53.6 ms and peaks at 100.6 V, settling at 100.4 V (no overshoot); latch gate 1 mV; UVLO pin minimum 1.67 V. It keeps 1.4 A of transformer margin without the 1 µF overshoot. A ±10 % capacitor spans 612–748 nF, inside the 470 nF–1 µF range where both ends also pass.

Both 470 nF and 1 µF pass. 470 nF has 0.7 A of transformer margin; a capacitor at the low end of its tolerance ramps faster and would narrow it, with a hiccup as the failure. 1 µF has 2.2 A of transformer margin but overshoots; with the model's 2.1 V low reading the real peak would be about 106.2 V, 2.8 V below the lowest trip level. Both runs sit at about 7 V for the first 15–30 ms, because COMP must climb past about 1.2 V before the controller asks for more than minimum pulses.

## Caveats
1. **Regulated rail reads 2.1 V low.** The TL431 model has a soft turn-on knee (about 50 mV wide at the reference pin), so it regulates at 100.35 V where a real part would hold about 102.5 V. The 5–7 V gap between the rails is the finding; add about 2 V to both rail values.
2. **Trip level reads about 2 V low for the same reason.** The trips fired near 107–108 V; a real TL431 would trip near 109.8 V, later by roughly the time the rail takes to climb 2 V. The 111 V check is therefore not demonstrated by this run; P8's 110.06 V remains the best estimate.
3. Core loss, capacitor series resistance, the optocoupler response, the blanking time and the battery resistance are assumptions. The pulse-skipping result depends on the blanking time and on the size of the turn-on spike, both uncertain; the bench will show whether it occurs.
4. Start-up was run without soft start because the controller's soft-start behaviour is not in this model; the real part will ramp more gently. The end of start-up (overshoot, and whether the trip fires) was not reached in 14 ms.
5. Steady-state numbers at 131 mA and at 12.6 V (M1, M2) were taken before the unregulated rail had settled (it settles in about 10 ms); only M6 and M7 are settled.

## Simulation notes
- LTspice instances started at the same instant interfere with each other: only the last one launched runs properly, the others crawl or never start. `run_monitored.ps1` now leaves 25 s between launches. The "stalled" P7 variant A and the stalled P8 re-run were probably this, not the circuit.
- The operating point is found by pseudo-transient (`noopiter gminsteps=0 srcsteps=0`); ordinary stepping did not converge.
- `run_monitored.ps1` reports each run's simulated time every 30 s and stops a run that makes no progress for 150 s. `raw_analyze.py` extracts ripple, on-times and start-up tables from a waveform file.
- The computer slept for about 17 minutes during the last batch; the runs resumed and completed.
- Waveform files (up to 256 MB each) were deleted. A 6 ms run takes about 2.5 minutes on its own.
