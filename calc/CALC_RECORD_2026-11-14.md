# TI LM5155/56 flyback calculator — record for option C (P-6)

**Question.** Do the option C values pass TI's own design calculator?
**Status.** done 2026-11-14 · file `LM5155_flyback_calc_P6_optionC.xlsx` (a copy; the original workbook is untouched) · calculator rev 1.0.1

## How option C was entered
The calculator has no model for two transformers on one switch. It was entered as the electrically equivalent single supply: both rails' current through one 5 µH primary (two 10 µH in parallel), 1:10. Controller-side results apply to the shared controller; per-rail parts are half the output values.

| Input | Value | Source |
|---|---|---|
| Vin min / typ / max | 9 / 11.1 / 12.6 V | battery |
| Vout, Iout | 102 V, 0.43 A (2 × 0.215 A) | P-4, P-5 revised |
| Turns ratio Ns/Np | 10 | [DS summary] DA2034-AL, unconfirmed |
| Primary inductance, resistance | 5 µH, 7.5 mΩ | two primaries in parallel [H] |
| Secondary resistance | 750 mΩ equivalent | [ASSUME] 1.5 Ω each |
| Switching frequency | 250 kHz | P6 simulation |
| Current-limit margin | 30 % | calculator default |
| Output capacitance, ESR | 66 µF total (33 µF per rail), 10 mΩ | this record; ESR [ASSUME] |
| Soft-start time | 20 ms | [ASSUME] |
| UVLO on / off | 8.5 / 8.0 V | proposal, below the 9 V battery minimum |
| Reference, divider | 2.495 V, 99.6 kΩ / 2.49 kΩ | TL431B; feedback redesign |
| Optocoupler CTR min / max | 0.8 / 1.6 | TCMT1107 [DS summary] |
| Pull-up voltage, resistor | 6.8 V, 5.11 kΩ | calculator default; WEBENCH |
| LED resistor | 44.1 kΩ | feedback redesign |
| Target crossover | 2 kHz | [H] |

## Result
| Check | Calculator [calc] | Design value | Hand / sim | Pass |
|---|---|---|---|---|
| Maximum duty at 9 V | 53.1 % | — | 54 % [H] | yes |
| Recommended primary inductance | 4.8 µH | 5 µH | — | yes |
| Peak primary current at 9 V (both transformers, no losses) | 11.09 A | — | 11.7 A [L] with losses and ±10 % mismatch | yes |
| Timing resistor for 250 kHz | 87.45 kΩ | 86.6 kΩ (252 kHz) | — | yes |
| Sense resistor | 6.73 mΩ recommended | 6 mΩ | 6 mΩ in P6 [L] | yes |
| Peak current limit | 14.4 A target | 16.2 A actual | 8.9 A in the worse transformer [H] vs 10 A rating | yes |
| External slope resistor | 191 Ω needed | 200 Ω | internal ramp 40 mV confirmed (30 µA × 1333 Ω) | yes, with 200 Ω; fails with 0 Ω |
| Output capacitance | 55 µF minimum | 66 µF | 44 µF (2 × 22 µF) was used before | yes at 66 µF; **fails at 44 µF** |
| Soft-start capacitor | 157 nF minimum | 200 nF | WEBENCH had 10 nF | yes at 200 nF; **fails at 10 nF** |
| UVLO divider | 43.9 kΩ / 9.41 kΩ | as calculated | — | yes |
| Bottom feedback resistor for 102 V | 2.497 kΩ | 2.49 kΩ | 102.5 V with reference input current [H] | yes |
| Pull-up resistor | 2.69 kΩ minimum | 5.11 kΩ | — | yes |
| LED resistor | 60.8 kΩ maximum | 44.1 kΩ | — | yes |
| Right-half-plane zero at 9 V | 31.2 kHz | — | 38 kHz [H] | — |
| Maximum advisable crossover | 6.25 kHz | — | — | — |
| Compensation RCOMP / CCOMP | 20.6 kΩ / 773 nF | 20.5 kΩ / 820 nF | replaces 845 kΩ / 1.5 nF carried from the 100 mA design | see below |
| Loop with those values, 11.1 V | crossover 537 Hz, phase margin 87°, gain margin 34 dB | — | 0.3–0.6 kHz over the CTR range [H] | yes (stable) |

## Verdict
Every calculator check passes once three values change from the earlier design: output capacitance up to 33 µF per rail, soft-start capacitor up to 200 nF, slope resistor (the resistor between the sense resistor and the CS pin) up to 200 Ω. The compensation carried over from the 100 mA design is not valid for this power stage and is replaced by the calculator's values. The loop crosses at about 0.5 kHz, not the 2 kHz entered: the calculator's formula does not account for the direct path through the LED resistor.

## What it changes
- Cout 22 µF → 33 µF per rail; Css 10 nF → 200 nF; Rcs (slope) 100 Ω → 200 Ω; Rsns 6 mΩ; Rt 86.6 kΩ.
- Rcomp1 / Ccomp1 → 20.5 kΩ / 820 nF.
- A load step of half load droops about 1 V at this bandwidth [H]; the channel accepts 90–110 V.

## Revision: library substitutes and corrected compensation (2026-11-14, later)
**Correction.** The 773 nF compensation capacitor above was a misreading. The calculator derives its capacitor from the *selected* resistor cell, which still held a stale 1.2 kΩ when that value was read. With the resistor selected properly the capacitor is tens of nanofarads. The 20.5 kΩ + 820 nF pair was stable in the calculator's loop model, but it was not the calculator's recommendation.

Substitutes entered (both in the JLCPCB library):

| Input | Was | Now | Source |
|---|---|---|---|
| Optocoupler | TCMT1107, CTR 0.8–1.6 | TCMT1108, CTR 1.0–2.6 | [DS] Vishay 83510: 130–260 % at 5 mA; minimum derated to 1.0 for about 1–2 mA LED current [ASSUME] |
| Switch on-resistance | 8.7 mΩ (file default) | 7.8 mΩ | [DS] CSD19531Q5A maximum at 6 V gate drive; 6.0 mΩ typical |
| Gate charge total / gate-drain / gate-source | file defaults | 37 / 6.6 / 10.5 nC | [DS] |
| Threshold voltage | 1.7 V | 2.7 V | [DS] typical; 3.3 V maximum |

| Check | Calculator [calc] | Design value | Pass |
|---|---|---|---|
| LED resistor | 76.0 kΩ maximum | 44.1 kΩ | yes |
| Compensation resistor | 12.68 kΩ | 12.7 kΩ | yes |
| Compensation capacitor, with 12.7 kΩ selected | 73.1 nF | 68 nF, 250 V | yes |
| Loop at 9 / 11.1 / 12.6 V | crossover 661 / 741 / 776 Hz; phase margin 80.3° / 80.7° / 80.8°; gain margin 30 / 32 / 32 dB | — | stable at all three |

Switch conduction loss at 6.7 A RMS: 0.27 W typical, 0.35 W maximum [H]. Light-load margin on the cascode node improves with the higher minimum CTR: about 21 V at light load instead of 8 V [H].

## Revision: output bulk as 3 × 10 µF per rail (P-15, 2026-11-14)
Entered 62 µF total (2 × (30 µF + about 1 µF ceramic)) with 500 mΩ equivalent series resistance (3 Ω per electrolytic [ASSUME], three in parallel per rail, two rails).

| Check | Calculator [calc] | Design value | Pass |
|---|---|---|---|
| Output capacitance | 55 µF minimum | 62 µF | yes |
| Soft-start capacitor | 147 nF minimum | 220 nF | yes |
| Compensation resistor | 11.9 kΩ | 12.7 kΩ kept | yes |
| Loop at 9 / 11.1 / 12.6 V | crossover 708 / 794 / 832 Hz; phase margin 88° / 89° / 90°; gain margin 26 / 27 / 28 dB | — | stable at all three |

The electrolytic's ripple-current rating and real series resistance are not read; the 1 µF ceramic is there to carry the switching-frequency ripple.

## Revision: undervoltage lockout 7.5 V on / 7.0 V off (P-18, 2026-11-15)
| Check | Calculator [calc] | Design value | Result |
|---|---|---|---|
| Top resistor | 50.5 kΩ | 49.9 kΩ | — |
| Bottom resistor, with 49.9 kΩ selected | 12.475 kΩ | 12.4 kΩ | on 7.54 V, off 7.04 V [H] |

Margin to the sagging battery [L, P9]: 1.4 V at full load (8.47 V), 1.1 V during start-up without soft start (8.16 V). Latch holding current through the top resistor at 9 V: about 0.17 mA [H].

## Caveats
- The calculator assumes 100 % efficiency, so its peak current is low by the loss fraction.
- Its capacitance check is a load-step rule (50 % step, 100 mV, at the maximum crossover), not a ripple rule.
- Capacitor ESR and the optocoupler capacitance are assumed; both shift the loop.
- Transformer values are from a datasheet summary until the DA2034-AL datasheet is read.
