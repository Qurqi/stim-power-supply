# ±102 V supply — final parts and connections for layout

Status 2026-11-16. This file consolidates decisions P-1 to P-24. It supersedes `SCHEMATIC_CHANGES_2026-11-14.md` as the list to capture from; that file keeps the history and the evidence for each value.
The reference designators below are this file's working names; **the schematic's designators are authoritative** and section 13 maps one to the other.
The design is verified by TI's calculator and LTspice only. Nothing here has been built.

Tags: [DS] datasheet · [calc] TI calculator · [L] LTspice · [H] hand calculation · [ASSUME] assumption.
"JLCPCB" gives the part number where it was looked up. "not looked up" means a standard value that was not searched individually.

## 0. Before layout (status 2026-11-16)

Decided 2026-11-16 (P-21 to P-24):

| Item | Decision | Still to do |
|---|---|---|
| 1. Soft start (P-20) | **decided 2026-11-16:** primary-side soft start (MMBT3906, COMP to GND, base on Css) with **Css 680 nF** (simulated: no current-limit cycles, 8.6 A transformer peak, no overshoot, 54 ms to 100 V) | — |
| 2. Connectors to the analog board (P-22) | lay out as is; agree with the analog-board owner later | — |
| 3. Battery side (P-23) | Rev 1 runs from a bench supply; battery connector, fuse, reverse-polarity and over-discharge protection deferred to Rev 2 | — |
| 4. Transformer (P-24) | keep the DA2034-ALD; buy outside JLCPCB and hand-solder (gull-wing SMD leads) | **done 2026-11-16:** pinout and footprint from LCSC's EasyEDA data (primary starts 7–10 dotted, ends 3–6; secondary 1 dotted, 12; 2 and 11 not connected; pads 3.30 × 1.27 mm, 3.0 mm pitch, 26.92 mm between columns), in `pcb/lib/`. Still cross-check against Coilcraft's drawing before ordering |
| 5. Spacing | follow JLCPCB's layout rules | see the note below |
| 6. Aux rails (P-21) | off-the-shelf ±12 V regulator and a 5 V supply, which the analog board's J2 expects | select the parts and decide whether they sit on this board |

**Schematic (2026-11-16):** `pcb/power_supply.kicad_sch` is generated from this file by `pcb/tools/gen_schematic.py`. KiCad ERC: 0 violations. KiCad's exported netlist matches this list pin for pin (132 parts, 298 pins, 64 nets; `pcb/tools/check_netlist.py`). Its component values match the final simulation netlist `sim_ladder/P9_final.net` on all 47 simulated elements (`pcb/tools/check_values.py`). Pinouts checked against manufacturers: LM51551 (TI), TL431 SOT-23 cathode 1 / REF 2 / anode 3 (TI; the TL432 differs, so order TL431BIDBZR), TCMT1108 (Vishay). Every pin has a net label; tidying into wires is left for review.

Transformer sources seen 2026-11-16: LCSC C5354095, 12 in stock at $11.79, plus 864 from another supplier through LCSC (5–7 days, $6.44); an aggregator lists about 1,200 at Mouser (994-DA2034-ALD) and about 670 at Coilcraft direct, both undated. Coilcraft also offers free samples. Two per board.

Spacing note: JLCPCB's rules are manufacturing minimums (how close copper can be made), not voltage clearances. The rectifier nodes ring to 390–470 V [L]; give the high-voltage nets extra room where the board allows.

**Needed but not blocking:** schematic capture in KiCad from this file, ERC, footprint check for every part; JLCPCB lookup of the standard values marked "not looked up"; review with the analog-board owner.

**Bench, provided for with footprints:** Ccs, Rgate, both snubbers, Css, trip level, transformer temperature.

## 1. What the supply does

| Item | Value | Source |
|---|---|---|
| Input | 9–12.6 V, three-cell lithium-ion | P-8 |
| Outputs | +102.5 V regulated; −HV follows, 5–7 V lower at full load | P-12, P-17; [L] |
| Rated load | 171 mA per rail at 9 V (131 mA at the 5 mA operating point) | P-19 |
| Topology | one LM51551, one switch, two transformers with primaries in parallel | P-6 |
| Switching frequency | 252 kHz | [calc] |
| Efficiency at 9 V, 171 mA per rail | 86.5 %; battery current about 4.3 A | [L] |
| Ripple after the filter | 6–7 mV peak to peak | [L] |
| Protection | trip at 109.8 V on either rail, latched off until the battery is removed; primary current limit 16.2 A | P-13; [calc] |
| Isolation | functional only; output return tied to battery ground at one point | P-3 |

## 2. Nets

`VIN` battery positive · `GND` battery negative, system ground and the midpoint of the two rails · `SW` switch node · `SNS` top of the sense resistor · `CS`, `COMP`, `UVLO`, `VCC`, `SS`, `RT`, `GATE` controller pins · `SNUB` primary clamp node · `SEC_P`, `SEC_N` switching ends of the two secondaries · `+HV_RAW`, `−HV_RAW` rails before the filter · `+HV`, `−HV` rails to the channel boards · `LATCH_G` latch gate.

## 3. Controller and primary side

| Ref | Part | Value / rating | Connects | JLCPCB |
|---|---|---|---|---|
| U1 | LM51551DSSR | WSON-12 | see pin table below | C778612 |
| Cin1 | SMD electrolytic | 330 µF, 25 V, 8 × 10 mm | VIN to GND; damps the ceramics against battery-lead inductance | C74593, 8,924 in stock (ripple and series resistance not on the page) |
| Cin2–Cin9 | ceramic | 8 × 10 µF, 25 V, X7R, 1206 | VIN to GND, tight to T1/T2 and M1; these carry the 4.6 A RMS ripple, about 0.6 A each [H] | C70462, 205,388 in stock |
| Cbias | ceramic | 100 nF, 25 V | BIAS pin to GND | not looked up |
| Cvcc | ceramic | 4.7 µF, 25 V, 0805 | VCC to GND | not looked up |
| Rt | resistor | 86.6 kΩ, 1 % | RT to GND | not looked up |
| Css | ceramic | **680 nF**, 16 V or more, X7R, ±10 % | SS to GND | not looked up |
| Qss | MMBT3906 | PNP | emitter COMP, base SS, collector GND (primary-side soft start, P-20) | C364311 |
| Rent | resistor | 49.9 kΩ, 1 % | VIN to UVLO | not looked up |
| Renb | resistor | 12.4 kΩ, 1 % | UVLO to GND | not looked up |
| Cbyp | ceramic | 220 pF | UVLO to GND | not looked up |
| Rpullup | resistor | 5.11 kΩ, 1 % | VCC to COMP | not looked up |
| Rcomp, Ccomp | footprints only | 249 kΩ, 4.7 nF | in series, COMP to GND; **do not fit** | — |
| T1, T2 | Coilcraft DA2034-ALD | 10 µH, 1:10, 10 A | both primaries VIN to SW: each part's four primary windings paralleled on the PCB, starts (pins 7–10, dotted) to VIN, ends (pins 3–6) to SW; pins 2 and 11 not connected | **not at JLCPCB**; LCSC C5354095, Mouser, Coilcraft; hand-fit |
| M1 | CSD19531Q5A | 100 V, 6 mΩ at 6 V | drain SW, source SNS, gate via Rgate | C2760462 |
| Rgate | resistor | 3.3 Ω start value | GATE to M1 gate | not looked up |
| Rsns | current-sense resistor | 6 mΩ, 1 %, 2512, **3 W** (0.24 W dissipated [L]) | SNS to GND, Kelvin sensed | **C429335**, 3,872 in stock (C76239 has only 5) |
| Rcs | resistor | 200 Ω, 1 % | SNS to CS | not looked up |
| Ccs | ceramic | **2.2 nF** | CS to GND, at the pin | not looked up |
| Dsnub | SS510C Schottky | 100 V, 5 A, SMC; sees about 33 V reverse at most [L] | anode SW, cathode SNUB | C123944, 22,339 in stock |
| Rsnub1–3 | resistor | **3 × 300 Ω in parallel** (100 Ω), 2512, 2 W each, 5 %; 0.45 W each simulated, 1.5 W each at the 4.5 W upper estimate | SNUB to VIN | C91264, 1,911 in stock |
| Csnub | ceramic | 100 nF, 100 V | SNUB to VIN | not looked up |

U1 pins: BIAS to VIN · VCC to Cvcc · GATE to Rgate · CS to Rcs/Ccs · COMP to Rpullup and the three optocoupler collectors · FB to GND · SS to Css · RT to Rt · UVLO/SYNC to the divider and the latch · PGND, AGND and pad to GND · PGOOD unconnected.

## 4. Each output rail

| Ref (+ / −) | Part | Value / rating | +HV connection | −HV connection | JLCPCB |
|---|---|---|---|---|---|
| T1 / T2 secondary | — | 1 mH nominal | pin 1 (dot) GND, pin 12 SEC_P | **pin 1 (dot) −HV_RAW**, pin 12 SEC_N | — |
| D1 / D2 | ES1J | 600 V, 1 A | anode SEC_P, cathode +HV_RAW | anode SEC_N, cathode GND | C86560 |
| Rsn1 / Rsn2, Csn1 / Csn2 | diode snubber | 220 Ω + 22 pF start values; capacitor rated 630 V or more | in series across D1 | in series across D2 | not looked up; tune on the bench |
| Co1–3 / Co4–6 | electrolytic, through-hole | 10 µF, 200 V, 8 × 12 mm, **180 mA at 100 kHz**; about 50 mA each expected [H] | +HV_RAW (+) to GND | GND (+) to −HV_RAW | **C106302**, 8,083 in stock (C112474 has more stock but no ripple rating on its page) |
| Co7 / Co8 | ceramic | 1 µF, 250 V, X7R, **1812** | +HV_RAW to GND | GND to −HV_RAW | C381468 |
| TVS1 / TVS2 | SMBJ130A | 130 V standoff | cathode +HV_RAW, anode GND | cathode GND, anode −HV_RAW | C224006 (124 in stock) |
| Lf1 / Lf2 | shielded inductor, 8 × 8 mm | 100 µH, saturation 1.15 A, rated 1 A, 0.29 Ω (load is 0.17 A) | +HV_RAW to bead | −HV_RAW to bead | C83468, 8,057 in stock |
| FB1 / FB2 | ferrite bead | 600 Ω at 100 MHz, 1.5 A, 80 mΩ, 1206 | inductor to +HV | inductor to −HV | C16902, 12,645 in stock |
| Cf1 / Cf2 | ceramic | 1 µF, 250 V, X7R, 1812 | +HV to GND | GND to −HV | C381468 |
| Cd1 / Cd2 | electrolytic, through-hole | 10 µF, 200 V | +HV (+) to Rd1 | Rd2 to −HV (+ towards GND) | C106302 |
| Rd1 / Rd2 | resistor | 10 Ω, 1206 | Cd1 to GND | GND to Cd2 | not looked up |

Feedback and both trip blocks sense the **raw** rails, before the filter.

## 5. Main feedback block (on +HV_RAW, referenced to GND)

| Ref | Part | Value / rating | Connects | JLCPCB |
|---|---|---|---|---|
| Rfbt1–3 | resistor | 3 × 33.2 kΩ, 0.1 %, 1206 | in series, +HV_RAW to REF | C2984513 |
| Rfbb | resistor | 2.49 kΩ, 0.1 % | REF to GND | C861299 |
| U2 | TL431BIDBZR | 0.5 % | REF pin to REF, anode GND, cathode to Q1 emitter | C41283 |
| Q1 | MMBTA42 | 300 V NPN | emitter U2 cathode, base to bias node, collector KC | C8515 |
| Rb1–3 | resistor | 3 × 110 kΩ, 1 %, 1206, 200 V | in series, +HV_RAW to Q1 base | **C17904**, 11,469 in stock (C246043 has only 3) |
| Dz1 | BZT52C12 | 12 V | cathode Q1 base, anode GND | C19077410 |
| Rled1–3 | resistor | 3 × 14.7 kΩ, 1206 | in series, +HV_RAW to U3 LED anode | C488648 |
| U3 | TCMT1108 | optocoupler | LED anode from Rled, LED cathode KC; collector COMP, emitter GND | C3014154 |
| Rsh | resistor | 2 kΩ | across U3's LED | not looked up |
| Rcomp1 | resistor | 12.7 kΩ, 1 % | in series with Ccomp1, KC to REF | not looked up |
| Ccomp1 | ceramic | 68 nF, 250 V, X7R, 1206 | in series with Rcomp1 | C513585 |
| R21a/b | resistor | 2 × 499 kΩ, 1206 | in series, +HV_RAW to node NSS | not looked up |
| C21 | ceramic | 2.2 µF, 250 V, X7R, 2220 (about 1.3 µF under bias [ASSUME]) | NSS to GND | C153032 |
| D21 | BAS21 | 200 V | anode KC, cathode NSS | C7502725 |
| D22 | BAS21 | 200 V | anode NSS, cathode +HV_RAW; discharges C21 when the rail falls, so the network re-arms | C7502725 |

**The start-up network (R21, C21, D21, D22) must be fitted.** Without it the rail overshoots to 107 V and trips the latch at every power-up; with it the rail reaches the setpoint with no overshoot in about 40 ms [L, P9 revision].

## 6. Trip blocks (one per rail)

Same circuit as section 5 with the differences below and **no compensation parts**. The −HV block is the same circuit turned over: GND is its positive side and −HV_RAW its return, so its TL431 anode, Zener anode and bottom divider resistor go to −HV_RAW, and its top divider, bias and LED resistors go to GND.

| Item | Value | JLCPCB |
|---|---|---|
| Divider top | 3 × 33.2 kΩ, 0.1 %, 1206 | C2984513 |
| Divider bottom | **2.32 kΩ**, 0.1 % (109.8 V) | C861296 |
| Reference filter | 4.7 nF from the REF pin to the block's return | not looked up |
| TL431BIDBZR, MMBTA42, 3 × 110 kΩ, BZT52C12, 2 kΩ LED shunt | as section 5 | as section 5 |
| LED resistor | 3 × **7.32 kΩ**, 1206 | **C247199**, 4,878 in stock (C488946 has only 10) |
| TCMT1108 output | collector COMP, **emitter LATCH_G** | C3014154 |

## 7. Latch (battery side)

| Ref | Part | Connects | JLCPCB |
|---|---|---|---|
| Q2 | MMBT3904 | emitter GND, base LATCH_G, collector to Q3 base | C916374 |
| Q3 | MMBT3906 | emitter UVLO, base to Q2 collector, collector LATCH_G | C364311 |
| Rpb | 100 kΩ | UVLO to Q3 base | not looked up |
| Rg, Cg | 10 kΩ, 10 nF | LATCH_G to GND, in parallel | not looked up |

## 8. Parts count per board

| Part | Quantity |
|---|---|
| DA2034-AL | 2 |
| TCMT1108, TL431BIDBZR, MMBTA42, BZT52C12 | 3 each |
| 33.2 kΩ 0.1 % 1206 / 110 kΩ 1206 | 9 / 9 |
| 14.7 kΩ 1206 / 7.32 kΩ 1206 | 3 / 6 |
| 10 µF 200 V electrolytic (through-hole) | 8 |
| 1 µF 250 V 1812 | 4 |
| ES1J, SMBJ130A, 100 µH inductor, ferrite bead, BAS21 | 2 each |
| MMBT3906 (latch + soft start) | 2 |
| 10 µF 25 V 1206 (input) | 8 |
| 300 Ω 2 W 2512 (clamp) | 3 |

## 9. Layout notes

- **High-current loop.** Input capacitors, transformer primaries, M1 and Rsns carry 14 A pulses. Keep that loop as small as possible and Kelvin-connect Rsns to Rcs.
- **Four primary windings per transformer.** Join pins 7–10 together and pins 3–6 together on the PCB with short, wide copper; the datasheet figures assume it. Confirm the pin numbers on Coilcraft's drawing.
- **Transformer symmetry.** Route T1 and T2 to SW and VIN with equal lengths. The two transformers ring against each other through their leakage, and unequal traces add to it.
- **Sense filter at the pin.** Place Ccs and Rcs next to U1, with Ccs returned to the controller's ground pin.
- **Clamp heat.** Rsnub dissipates 1.3 W in simulation and may reach 4.5 W; give it copper and keep it away from the electrolytics.
- **High-voltage spacing.** Layout follows JLCPCB's rules (decided 2026-11-16). Those are manufacturing minimums; the rails are 205 V apart and the rectifier nodes ring to 390–470 V, so give SEC_P, SEC_N and the raw rails extra room where the board allows.
- **Resistor strings.** Each three-resistor string shares about 100 V; lay them in a line so the voltage steps down along the board.
- **Quiet nodes.** Keep the REF pins, KC nodes and LATCH_G away from SW, SEC_P and SEC_N. LATCH_G must not pick up switching noise.
- **One ground tie.** The output return joins battery ground at one point near the supply; the channel boards return to that point.
- **Through-hole parts.** Eight 8 × 12 mm electrolytics; the two transformers are about 30 × 25 mm and 11.4 mm tall.
- **Test points.** +HV_RAW, −HV_RAW, +HV, −HV, SW, SNS, COMP, UVLO, LATCH_G, VCC, SS, GND.

## 10. Not in this design

- Battery connector, input fuse and reverse-polarity protection (Rev 2, P-23; Rev 1 runs from a bench supply through placeholder J1).
- Output connectors to the sixteen channel boards (to be agreed, P-22; placeholder J2).
- Battery over-discharge protection: the lockout at 7.0 V does not provide it.
- The ±12 V and +5 V rails for the channel boards (off-the-shelf ±12 V regulator and 5 V supply, P-21; parts not chosen).
- An indication to the operator that the supply has tripped.

## 10b. Open design issue: start-up current (P-20)

**Resolved 2026-11-16** by the primary-side soft start with Css = 680 nF (section 3; record in `sim_ladder/P9_final_RECORD.md`). The original finding follows.

With no output voltage to reset the transformers, the primary current climbs past the current limit during the first milliseconds of start-up. In simulation it reaches **26 A in the switch and 12.4 / 14.6 A in the transformers**, against their 10 A rating, with the 2.2 nF sense filter [L]. With the earlier 470 pF it was 19.6 A (about 9.8 A each), but that value skips pulses in steady state. The model has no transformer saturation and assumes a 120 ns blanking time, so the real figure is uncertain in both directions. The options considered were an intermediate filter value, reducing the turn-on spike at its source, or limiting current during start-up; the third was chosen.

## 11. To settle on the bench

1. Switching is regular with Ccs at 2.2 nF (no skipped pulses).
2. Trip level on each rail against the 111 V limit; latch does not fire from noise or when the battery is connected.
3. Start-up with the primary-side soft start (Css 680 nF): no current-limit dwell or hiccup, no overshoot, no trip, no lockout.
4. Rectifier snubber: reverse voltage, simulated at 390–470 V.
5. Primary clamp loss and transformer temperature at full load.
6. Actual −HV level across load, and which rail sits low.
7. Channel idle current against the 5.2 mA per rail assumed.
8. Ripple-to-load sensitivity at 252 kHz (the analog team's A8).

Before ordering: re-check stock on every part (several first choices turned out to have fewer than ten), look up the standard values marked "not looked up", and get Coilcraft's approval before any use on a person.

## 12. Stock and ratings pass, 2026-11-15

Read from each part's own JLCPCB page. Stock moves, so treat the counts as a snapshot.

| Part | Finding | Action taken above |
|---|---|---|
| Sense resistor C76239 | 2 W, but 5 in stock | changed to C429335 (3 W, 3,872) |
| Filter inductor C83468 | saturation 1.15 A, rated 1 A, 0.29 Ω; 8,057 | confirmed |
| Ferrite bead C16902 | 1.5 A, 80 mΩ; 12,645 | confirmed |
| Bulk electrolytic C112474 | 57,166 in stock, no ripple rating on the page | changed to C106302 (180 mA at 100 kHz; 8,083) |
| Polymer input capacitor | C3274630, C1020104, C2919878, C723101, C5129328 all show 0 in stock | replaced by 8 ceramics plus one 330 µF electrolytic; re-simulated 2026-11-15 (0.21 V input ripple, 0.6 A RMS per ceramic) |
| 110 kΩ 1206 C246043 | 3 in stock | changed to C17904 (11,469) |
| 7.32 kΩ 1206 C488946 | 10 in stock | changed to C247199 (4,878) |
| 2.49 kΩ 0.1 % C861299, 2.32 kΩ 0.1 % C861296, 14.7 kΩ C488648, 10 µF 25 V C70462 | 7,739 / 5,277 / 3,211 / 205,388 | confirmed |
| Clamp diode and resistor | were not chosen | SS510C (C123944) and 3 × 300 Ω 2 W (C91264) |

The input capacitor change was the one electrical change here; the final simulation now models it (40 µF effective ceramic [ASSUME 50 % loss under bias] plus the 330 µF electrolytic) and gives 0.21 V of input ripple [L].

## 13. Designator map: this file to the schematic

The schematic's designators are the ones to use from now on (BOM, layout, bench notes).

| Block | This file | Schematic |
|---|---|---|
| Input, controller | Cin1 · Cin2–Cin9 · Cbias · Cvcc · Rt · Css · Qss · Rent · Renb · Cbyp · Rpullup · Rcomp, Ccomp (DNP) | C1 · C2–C9 · C10 · C11 · R1 · C12 · Q1 · R2 · R3 · C13 · R4 · R5, C14 |
| Power stage | T1, T2 · M1 · Rgate · Rsns · Rcs · Ccs · Dsnub · Rsnub1–3 · Csnub | T1, T2 · Q2 · R6 · R7 · R8 · C15 · D1 · R9–R11 · C16 |
| +HV output | D1 · Rsn1, Csn1 · Co1–3 · Co7 · TVS1 · Lf1 · FB1 · Cf1 · Cd1 · Rd1 | D2 · R12, C17 · C18–C20 · C21 · D3 · L1 · FB1 · C22 · C23 · R13 |
| −HV output | D2 · Rsn2, Csn2 · Co4–6 · Co8 · TVS2 · Lf2 · FB2 · Cf2 · Cd2 · Rd2 | D4 · R14, C24 · C25–C27 · C28 · D5 · L2 · FB2 · C29 · C30 · R15 |
| Main feedback | Rfbt1–3 · Rfbb · U2 · Q1 · Rb1–3 · Dz1 · Rled1–3 · U3 · Rsh · Rcomp1 · Ccomp1 · R21a/b · C21 · D21 · D22 | R16–R18 · R19 · U2 · Q3 · R20–R22 · D6 · R23–R25 · U3 · R26 · R27 · C31 · R28, R29 · C32 · D7 · D8 |
| Trip +HV | divider top · bottom · filter · TL431 · MMBTA42 · bias · Zener · LED resistors · optocoupler · LED shunt | R30–R32 · R33 · C33 · U4 · Q4 · R34–R36 · D9 · R37–R39 · U5 · R40 |
| Trip −HV | same order | R41–R43 · R44 · C34 · U6 · Q5 · R45–R47 · D10 · R48–R50 · U7 · R51 |
| Latch | Q2 (MMBT3904) · Q3 (MMBT3906) · Rpb · Rg · Cg | Q6 · Q7 · R52 · R53 · C35 |
| Connectors, test points | bench input · HV output · test points | J1 · J2 · TP1–TP12 |
