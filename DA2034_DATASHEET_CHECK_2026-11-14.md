# Coilcraft DA2034-AL — datasheet check

**Question.** Do the transformer figures the design has been using hold on the datasheet, and does the datasheet add any constraint?
**Status.** read 2026-11-14 · source: Coilcraft Document 510, "Flyback Transformers for Linear LT3750 Capacitor Charger Controllers", revised 03/07/25 [DS]

## Values
| Parameter | Datasheet [DS] | Used in the design | Agrees |
|---|---|---|---|
| Primary inductance at 0 A | 10.0 µH ±10 % | 10 µH, ±10 % mismatch simulated | yes |
| Primary inductance at peak current | 9.0 µH minimum | — | this defines the 10 A rating: inductance has fallen by no more than 10 % |
| Peak primary current | 10.0 A | 10 A; 8.9 A reaches the worse transformer at the current limit [H] | yes, 1.1 A margin |
| Turns ratio, primary : secondary | 1 : 10 | 1 : 10 | yes |
| Primary resistance, maximum | 0.018 Ω (both primary windings in parallel) | 0.015 Ω in simulation | close; about 0.21 W copper loss each at 3.4 A RMS [H] |
| Secondary resistance, maximum | 1.75 Ω | 1.5 Ω assumed | slightly worse; about 0.19 W each [H], and a little more drift on the unregulated rail |
| Leakage inductance, maximum | 0.250 µH | 0.2 µH (k = 0.99) in simulation | worse case is 25 % higher; primary clamp loss then sits at the top of the 2–4.5 W estimate [H] |
| Interwinding capacitance | 128 pF | not in the simulation | see below |
| Isolation | 1500 Vrms winding to winding, 750 Vrms winding to core, one minute | functional only (P-3) | yes |
| Intended use | 3–24 V input, charging a capacitor to 300 V | 9–12.6 V in, 102 V out, 228 V diode reverse voltage | yes, inside its range |
| Size, weight | about 30.0 × 24.6 mm, 11.4 mm high; 14.1 g | two per board | layout item |
| Ambient temperature | −40 to +125 °C | — | — |

## Constraints the datasheet adds
1. **Medical-use restriction.** The datasheet states: "This product may not be used in medical or high risk applications without prior Coilcraft approval." This year's scope is dummy loads with no human subjects, but the device is a stimulator, so approval is needed before any use on a person.
2. **Two primary windings per part,** to be connected in parallel on the PCB. The quoted primary resistance and leakage assume that connection.
3. **Hard-switched use is outside what the part was made for.** It was designed for a capacitor charger that switches at the boundary of conduction. Here it runs in continuous conduction at 250 kHz, where the 128 pF between windings is charged and discharged through about 230 V every cycle. A rough estimate is 0.5–1 W per transformer [H], which is not in the simulated 85 % efficiency.

## Verdict
Every figure the design relied on is confirmed or slightly on the worse side, and none breaks a check. The medical-use restriction is the new constraint.

## What it changes
- Ask Coilcraft for approval (and evaluation samples) if the design is ever to be used on a person.
- Layout: parallel the two primary windings on each transformer.
- Bench: measure transformer temperature and efficiency at full load; if the capacitive loss is as estimated, a lower switching frequency is the lever.
- Records that tagged transformer values [DS summary] can now read [DS].
