# P6 Rail tracking with one converter and two transformers — record

**Question.** With one controller and one switch driving two catalogue transformers (primaries in parallel), do the ±104 V rails track each other, and what happens when one output rectifier fails open? (Decision P-6, option C.)
**Status.** sim done 2026-11-14 (LTspice 26.1.1, batch run) · bench pending (power board not built)

## Setup
| | Sim [L] | Bench [B] |
|---|---|---|
| Circuit | `P6_rail_tracking.net`: idealized LM5155 from `L3_real_parts.net`, plus slope compensation 40 mV/period [ASSUME], 6 ms soft start [ASSUME], ideal gm error amp on +HV only | power board, resistor loads |
| Transformers | 2 × 10 µH, 1:10, k = 0.99 [DS summary, DA2034-AL, unconfirmed]; mismatch +10 % on +HV, −10 % on −HV [H]; winding resistance 15 mΩ / 1.5 Ω [ASSUME] | as fitted; measure Lp of each |
| Input | 9 V (runs 1–3), 12.6 V (run 4) | bench supply, then battery |
| Load | idle 91 mA per rail (1143 Ω); +80 mA step (1300 Ω) on +HV at 10–14 ms, on −HV at 14–18 ms, on both from 18 ms | switched resistors, same values |
| Faults | run 2: −HV rectifier opens at 10 ms; run 3: +HV rectifier opens at 10 ms; all runs: controller stops at 21 ms | not a bench test (run 3 over-volts the board) |
| Measured | rail averages per phase, max \|V(+HV)+V(−HV)\|, primary peaks, Vds | DMM on both rails per phase; scope on start-up and shutdown |

## Result
| Quantity | Sim 9 V | Sim 12.6 V | Bench | Limit | Pass |
|---|---|---|---|---|---|
| Rails, both idle (+ / −) | +104.5 / −105.9 V | +104.0 / −104.1 V | | under 110 V | yes |
| Rails, +HV heavy by 80 mA | +104.0 / **−108.6 V** | +104.0 / −107.3 V | | under 110 V | yes, 1.4 V margin |
| Rails, −HV heavy by 80 mA | +104.0 / −100.7 V | +104.0 / −101.9 V | | over 90 V | yes |
| Rails, both at 171 mA | +104.0 / −105.4 V | +104.0 / −104.1 V | | under 110 V | yes |
| Largest rail magnitude seen, no fault | +106.1 / −108.7 V | +106.3 / −107.4 V | | under 110 V | yes |
| Mismatch during start-up (max) | 2.3 V | 1.9 V | | — | |
| Mismatch after controller stops (max, 11 ms) | 1.8 V | 0.02 V | | — | |
| Primary peaks at full load (T1 / T2) | 5.6 / 6.1 A | 5.2 / 5.5 A | | 10 A [DS summary] | yes |
| Switch voltage peak | 28.7 V | 30.8 V | | — | |
| Efficiency at full load (no core loss) | 85 % | 91 % | | — | |
| Run 2, −HV rectifier open: rails 10 ms later | +104.0 / −69 V and falling | | | | not covered |
| Run 3, +HV rectifier open: rails 10 ms later | +69 V / **−191 V and rising** | | | under 110 V | **fail** |

## Verdict
The rails track: within 2.3 V through start-up and shutdown, and within 4.7 V under an 80 mA load imbalance, which is larger than normal operation produces because sourced and sunk currents sum to zero. The unregulated rail reaches 108.6 V in the worst imbalance, 1.4 V under the 110 V limit before setpoint tolerance (about ±1.6 V) is added. An open rectifier is not covered: losing the unregulated output leaves one rail up (run 2), and losing the regulated output drives the other rail to −191 V within 10 ms (run 3).

## What it changes
- P-6 option C stands for tracking.
- New decision needed: over-voltage protection must act on each rail independently, because the loop only sees +HV (run 3).
- New decision needed: margin to 110 V. Options are a lower setpoint (about 102 V) or sensing the sum of the two rails so the drift is shared.
- Run 2 remains a channel-side hazard (analog team decision D-A7).

## P6b: 102 V setpoint, 33 µF per rail, clamp on each rail (2026-11-14)
`P6b_rail_tracking_clamp.net`: same model with setpoint 102 V (P-12), 33 µF per rail and 46 mV slope ramp [calc], plus an idealized clamp on each rail at 109.8 V that pulls COMP down [ASSUME gain]. Events are 10 ms later than in P6 because start-up with 33 µF takes longer. 9 V input.

| Quantity | Sim 9 V [L] | Limit | Pass |
|---|---|---|---|
| Rails, both idle (+ / −) | +102.0 / −103.0 V | under 110 V | yes |
| Rails, +HV heavy by 80 mA | +102.0 / **−106.2 V** | under 110 V | yes, 3.8 V margin |
| Rails, −HV heavy by 80 mA | +102.0 / −99.5 V | over 90 V | yes, 9.5 V margin |
| Rails, both at 171 mA | +102.0 / −102.6 V | under 110 V | yes |
| Largest rail magnitude, no fault | +103.8 / −106.3 V | under 110 V | yes |
| Mismatch at start-up / after stop (max) | 2.1 V / 0.9 V | — | |
| Primary peaks at full load (T1 / T2) | 5.4 / 5.9 A | 10 A [DS summary] | yes |
| +HV rectifier open: −HV | **held at −110.2 V** (was −191 V) | D5 111 V minimum | yes, 0.8 V margin |
| +HV rectifier open: T2 primary peak | 8.0 A | 10 A [DS summary] | yes |

The clamp turns the run 3 failure into a pass. The real clamp block (TL431 + optocoupler + cascode per rail) is not in this model; its threshold tolerance (about ±0.8 V with a 0.5 % reference and 0.1 % resistors [H]) uses most of the window between the highest normal rail (107.9 V with tolerance) and D5's 111 V.

## Caveats
- Idealized controller and ideal switch; the TL431/optocoupler loop is not in this model.
- Cross-regulation depends on leakage and winding resistance, both taken from a datasheet summary or assumed. The bench imbalance test is the number to believe.
- No core loss; efficiency is optimistic.
- The waveform file (`.raw`, 1.8 GB) was deleted after the run. Opening the `.net` in LTspice and running it regenerates it; expect about 12 minutes.
