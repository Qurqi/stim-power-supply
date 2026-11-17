# Schematic changes: WEBENCH design 6 → option C (±102 V, 215 mA per rail)

Status 2026-11-14. Baseline: WEBENCH design 6 (`WBDesign6.svg`, `WBBOMDesign6.csv`: +110 V, 100 mA, one transformer).
Target: one LM51551 and one switch driving two catalogue transformers with primaries in parallel (P-6 option C),
±102 V (P-12), 215 mA per rail (P-4), LC filter only (P-7), a clamp on each rail.

Tags: [calc] TI calculator (`calc/CALC_RECORD_2026-11-14.md`) · [L] LTspice (`sim_ladder/P6_rail_tracking_RECORD.md`) ·
[H] hand calculation · [DS summary] datasheet figure from a search summary, not yet read on the datasheet · [ASSUME].
Voltage ratings follow the analog team's rule: 1.5× on anything the 110 V rail can reach, so 165 V or more.

## 1. Controller and primary side

| Ref | WEBENCH design 6 | Change to | Why | Evidence |
|---|---|---|---|---|
| U1 | LM51551DSSR | no change | hiccup current limit kept | — |
| T1 | custom, 9 µH, 1:18.62 | **T1 and T2: Coilcraft DA2034-AL**, 10 µH, 1:10; both primaries from VIN to the switch node | catalogue part; one switch feeds both rails so they rise and fall together | [L] tracking within 4.3 V; [DS summary] |
| M1 | CSD19538Q2 (100 V, about 49 mΩ) | **CSD19531Q5A** (100 V; 6.0 mΩ typical, 7.8 mΩ maximum at 6 V gate drive; JLCPCB C2760462) | switch now carries 11.7 A peak, about 6.7 A RMS; the old part would dissipate about 2 W, this one 0.27–0.35 W | [L] peak, 31 V on the switch; [H] RMS; [DS] |
| Rsns | 16 mΩ, 1 W | **6 mΩ**, 1 W | 16.2 A current limit: above the 11.7 A working peak, below 10 A per transformer with ±10 % mismatch (8.9 A) | [calc]; [H] |
| Rcs (sense resistor to CS pin) | 100 Ω | **200 Ω** | this resistor sets the external slope compensation; duty is above 50 % | [calc] 191 Ω needed |
| Ccs | 470 pF | **2.2 nF** (P-16, decided 2026-11-15) | with 470 pF the controller skipped a pulse every 5–6 cycles in the final simulation; 2.2 nF gave regular switching and 7 mV filtered ripple. Filter time constant becomes 440 ns, so the current limit acts about 0.35 µs later: roughly 0.6 A more at the limit [H] | [L] check P9 |
| Rt | 86.6 kΩ | no change (252 kHz) | — | [calc] 87.45 kΩ for 250 kHz |
| Css | 10 nF | **220 nF** | start-up must not hit the current limit while charging 2 × 33 µF | [calc] 157 nF minimum |
| Rent / Renb (UVLO) | 100 kΩ / 23.7 kΩ (on at 7.8 V) | **49.9 kΩ / 12.4 kΩ: on 7.5 V, off 7.0 V** (P-18, decided 2026-11-15; replaces the earlier 8.5 / 8.0 V proposal) | the battery terminal sags to 8.47 V at full load and 8.16 V during start-up [L]; the earlier thresholds left 8 mV of margin. At 7.0 V the lockout is below a three-cell pack's safe minimum, so it no longer protects the battery: the pack's own protection must | [calc] 49.9 kΩ / 12.475 kΩ; [H] 7.54 V / 7.04 V with E96 values |
| Cin, Cinx | 82 µF 16 V polymer + 4.7 µF | more capacitance and 20–25 V parts, sized for about 4.6 A RMS ripple; e.g. 2 × polymer + 4 × 10 µF X7R | input current is now about 5 A average; 16 V is only 79 % derated on 12.6 V | [H]; part choice open |
| Rsnub, Csnub, Dsnub (primary clamp, placeholders) | not valued | start: 100 Ω, 100 nF 100 V, fast 100 V diode; resistor rated for **2–4.5 W** | two leakage inductances dump into this clamp each cycle | [L] start values; [H] loss from 0.15–0.25 µH leakage [DS summary]; bench-tune |
| Rgate (placeholder) | not valued | start 2–5 Ω | — | bench |
| Rpullup | 5.11 kΩ | no change | above the 2.69 kΩ minimum | [calc] |
| Ccomp, Rcomp (COMP to GND) | 4.7 nF + 249 kΩ | keep footprints, do not fit | the validated loop model has no parts here | [calc] |
| Ciso | 1 nF 2 kV across the barrier | **delete** | output return is tied to battery ground at one point (P-3) | — |
| Cvcc, Cbias, Cbyp | 4.7 µF, 100 nF, 220 pF | no change | — | — |

## 2. Output side, built twice (+HV and −HV)

+HV: T1 secondary → diode → +HV, return to GND. −HV: T2 secondary dot end is −HV; the other end goes through the diode (anode at the winding) to GND.

| Ref | WEBENCH design 6 | Change to (each rail) | Why | Evidence |
|---|---|---|---|---|
| Dsec | custom, 689 V, 250 mA | 400–600 V ultrafast or SiC, 1 A or more | reverse voltage 102 + 12.6 × 10 = 228 V; peak current about 0.6 A, 0.8 A in a fault | [H]; [L] |
| R9, C11 (diode snubber, placeholders) | not valued | footprints, bench-tune | depends on the real transformer | bench |
| Cout1, Coutx | custom, 11.8 µF + 10 µF | **3 × 10 µF 200 V electrolytic** (JLCPCB C112474, through-hole, 8 × 12 mm) **plus 1 µF 250 V X7R ceramic** (C381468, 1812) for the ripple current (about 0.25 A RMS); P-15 | calculator's load-step rule fails at 22 µF; 33 µF parts are thinly stocked | [calc] 55 µF minimum for both rails, 62 µF fitted; loop re-checked: crossover 708–832 Hz, phase margin 88° or more, gain margin 26 dB or more, with 3 Ω per electrolytic [ASSUME]; [H] ripple current |
| new: LC filter | — | 100 µH shielded (0.5 A or more, 1 Ω or less) + about 1 µF effective 250 V ceramic; damping 10 µF 200 V in series with 10 Ω; ferrite bead in series | 16 kHz corner, about 48 dB at 252 kHz; feedback is taken before the filter | [H]; A8 to be repeated at 252 kHz |
| new: transient suppressor | — | SMBJ130A (130 V standoff; JLCPCB C224006, low stock), across the raw rail | fast spikes only; the clamp block does the sustained work | [H] |
| capacitance multiplier | planned earlier | **not fitted** | dropped (P-7) | A8 archive figure [L] |

## 3. Main feedback block (on +HV, referenced to GND)

| Ref | WEBENCH design 6 | Change to | Why | Evidence |
|---|---|---|---|---|
| Rfbt | 29.4 kΩ, one part | 3 × 33.2 kΩ, 1206, 0.1 % | voltage rating and 0.12 W instead of 0.40 W | [H] |
| Rfbb | 681 Ω | **2.49 kΩ**, 0.1 % → 102.5 V | setpoint (P-12) | [calc] 2.497 kΩ; [H] |
| VR | TL431I | TL431B (0.5 %) | rail tolerance about ±1.5 % | [H] |
| new: Q1 | — | MMBTA42 (300 V NPN): emitter to TL431 cathode, collector to LED cathode | keeps the TL431 under its 36 V limit; the node sits near 57 V | [H]; not simulated |
| new: Q1 bias | — | 3 × 110 kΩ from +HV to a 12 V Zener at Q1's base | sets the shield level | [H] |
| Rled | 44.2 kΩ, 0201 | 3 × 14.7 kΩ, 1206 | same value; rating | [calc] 60.8 kΩ maximum |
| new: LED shunt | — | 2 kΩ across the optocoupler LED | TL431 minimum current | [H] |
| Rcomp1, Ccomp1 | 249 kΩ, 4.7 nF 50 V | **12.7 kΩ, 68 nF 250 V**, from Q1's collector to the TL431 REF pin (an earlier 20.5 kΩ + 820 nF in this list was a misreading of the calculator) | re-tuned for this power stage and the TCMT1108: crossover 661–776 Hz, phase margin 80°, gain margin 30 dB or more | [calc] |
| R21, C21, D21 (start-up network) | 15.4 kΩ, 100 µF 25 V, BAT54 | footprints for 2 × 499 kΩ, 2.2 µF 250 V, BAS21 (200 V in the JLCPCB listing; it sees about 50 V); fit only if start-up overshoots | the original parts are over-voltaged; start-up with the new compensation is not simulated | bench |
| O1 | TCMT1107 | **TCMT1108** (130–260 % at 5 mA; JLCPCB C3014154); same part for both trip blocks | TCMT1107 is not in the JLCPCB library; the higher minimum transfer ratio also restores light-load margin | [DS]; [calc] |

## 4. Clamp blocks, built twice (new)

One on +HV referenced to GND; one on −HV, where GND is the block's positive side and −HV its return. Each is a copy of section 3 with these differences. Each optocoupler's transistor goes from COMP to GND, in parallel with O1.

| Item | Value | Why | Evidence |
|---|---|---|---|
| Bottom resistor | **2.32 kΩ**, 0.1 % → 109.8 V | threshold 109.0–110.6 V; highest normal rail 107.9 V; channel diode D5 111 V minimum | [H]; [L] 106.3 V normal, 110.2 V clamped |
| Divider top, TL431B, Q, bias, LED resistor, LED shunt, optocoupler | as section 3 | one block design, three instances | — |
| Architecture | **trip and latch off** (P-13) | a clamp that regulates through COMP overshoots to −114.8 V (check P7); a trip peaks at −110.06 V (check P8, `sim_ladder/P8_trip_latch_RECORD.md`) | [L] |
| Compensation (Rcomp1, Ccomp1) | **none** | the TL431 works as a comparator | [L] |
| Reference filter | 4.7 nF from the TL431 REF pin to the block's return | keeps ripple from tripping it; adds about 11 µs | [H] |
| LED resistor | 22 kΩ as 3 × 7.32 kΩ, 1206 (replaces 3 × 14.7 kΩ in these blocks) | about 4.4 mA when tripped, for a fast, firm pull | [L] |
| Optocoupler output | collector to COMP, **emitter to the latch gate** (not to GND) | one current pulls COMP down and fires the latch | [L] |
| new: latch | MMBT3904 + MMBT3906 pair across the UVLO pin; 100 kΩ PNP base to emitter; 10 kΩ and 10 nF from gate to GND | holds UVLO at about 0.64 V; holding current comes from the battery through Rent, so only removing the battery resets it | [L] |

## 4b. From the final simulation (P9, 2026-11-15) — decisions open

See `sim_ladder/P9_final_RECORD.md`. Numbers are [L] with assumed core loss, blanking time and battery resistance.

| Ref | Now | Proposed | Why | Status |
|---|---|---|---|---|
| Ccs (current-sense filter) | 470 pF | **2.2 nF** | as designed the controller skips a pulse every 5–6 cycles (turn-on spike from winding capacitance and rectifier recovery); with 2.2 nF every cycle is regular and filtered ripple falls from about 90 mV to 7 mV p-p | P-16, **decided: 2.2 nF** |
| Unregulated rail | follows +HV | accept · raise the setpoint · sense the sum of both rails | with real parts −HV sits 5–7 V below +HV at full load (about 95.8–97.4 V when +HV is 102.5 V) | P-17, **decided: accept**. Sinking channels have 5–7 V less reach than sourcing ones; the analog team should size compliance and return-current checks on the lower rail |
| Rent / Renb (UVLO) | 44.2 kΩ / 9.53 kΩ (8.5 V on, 8.0 V off) | 49.9 kΩ / 12.4 kΩ (7.5 V on, 7.0 V off) | battery terminal sags to 8.47 V at full load and 8.16 V during start-up with 0.12 Ω of source resistance [ASSUME] | P-18, **decided: 7.5 / 7.0 V** |
| Css / start-up | 220 nF | confirm on the bench that the LM51551 soft start keeps start-up off the current limit | start-up without soft start ran at the current limit for more than 14 ms | bench |
| Output diode | ES1J 600 V | keep 600 V; tune the 220 Ω + 22 pF snubber | reverse voltage rings to 390–470 V against 228 V calculated | bench |
| Load rating | 215 mA per rail (P-4) | 171 mA at 9 V | switch peaks at 14.2 A of a 16.2 A limit at 171 mA; 215 mA would need more than the transformers' 10 A | P-19, **decided: 171 mA per rail at 9 V** (supersedes the 215 mA of P-4). 171 mA is the worst-case load with no margin on top: 83 mA idle + 8 mA bleeders + 80 mA with every channel at its 10 mA hard limit |

## 5. Open before layout

- ~~Read the DA2034-AL datasheet.~~ Done: figures confirmed (`DA2034_DATASHEET_CHECK_2026-11-14.md`). New from the datasheet: Coilcraft approval is required for medical use; each part has two primary windings to parallel on the PCB; expect roughly 0.5–1 W of extra switching loss per transformer from its 128 pF interwinding capacitance [H].
- Simulate the real clamp block and choose its compensation (section 4).
- Simulate the cascode feedback block with the new compensation; the loop numbers are from the calculator's model, which has no cascode.
- Choose M1 and confirm its on-resistance at the LM51551 gate-drive voltage.
- Primary clamp loss of 2–4.5 W: confirm on the bench, or consider a lower-leakage part.
- Channel idle current: 5.2 mA per rail from A1 [L] against about 1 mA in the 3 Nov rationale. P-4 (215 mA) rests on the higher figure.
- UVLO thresholds and input capacitor parts (section 1).
- Check every part against the JLCPCB library.
