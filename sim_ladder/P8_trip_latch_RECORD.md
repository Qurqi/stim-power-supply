# P8 Over-voltage trip with latch-off — record

**Question.** Does a comparator trip on each rail, latching the converter off, keep a faulted rail under the channel diode's 111 V? (Decision P-13.)
**Status.** sim done 2026-11-14 (LTspice 26.1.1, batch) · bench pending

## Setup
| | Sim [L] | Bench [B] |
|---|---|---|
| Circuit | `P8_trip_latch.net` (base), `P8_run_F1.net`, `P8_run_F2.net` | power board |
| Power stage and main loop | as P7: two 10 µH 1:10 transformers, 6 mΩ, 33 µF per rail, real main feedback block, 9 V in | |
| Trip block, one per rail | 3 × 33.2 kΩ / 2.32 kΩ (109.8 V), 4.7 nF on the reference pin, TL431 as comparator (no compensation), 300 V NPN cascode, 22 kΩ LED resistor, 2 kΩ LED shunt, optocoupler CTR 0.8 | |
| Optocoupler outputs | collector on COMP, emitter on the latch gate | |
| Latch | NPN + PNP pair across the UVLO pin; 100 kΩ on the PNP base, 10 kΩ and 10 nF on the gate | |
| UVLO divider | 44.2 kΩ / 9.53 kΩ; switching inhibited below 1.45 V [calc thresholds] | |
| Load | 91 mA idle per rail plus 80 mA extra on +HV | |
| Faults at 3 ms | F1: +HV rectifier opens. F2: main optocoupler output opens | F2 by lifting the optocoupler; F1 is not a bench test |

## Result
| Quantity | F1: +HV rectifier open | F2: main optocoupler open | Limit | Pass |
|---|---|---|---|---|
| Before fault: +HV / −HV | +101.9 / −106.5 V | same | under 110 V | yes |
| Before fault: latch gate, UVLO | 3 mV, 1.60 V | same | no false trip | yes |
| Rail peak after fault (+HV / −HV) | +101.9 / **−110.06 V** | +104.5 / **−109.97 V** | 111 V | yes |
| Time from fault to trip | 0.48 ms | 1.13 ms | — | |
| UVLO after trip | 0.64 V, held | 0.64 V, held | below 1.45 V | yes |
| Rails 9 ms later | +64.7 / −87.7 V, falling | +70.3 / −89.2 V, falling | both decaying | yes |

For comparison, the regulating clamp (P7) peaked at −114.8 V and −115.6 V in the same two faults.

## Verdict
The trip holds the faulted rail to 0.26 V above its threshold in both faults, against 5 V for the regulating clamp, and the converter stays off. At the top of the threshold tolerance (110.6 V [H]) the peak would be about 110.9 V, just inside 111 V. It does not false-trip at the worst normal load imbalance.

## What it changes
- P-13: clamp blocks become trip blocks; a two-transistor latch is added across the UVLO pin.
- After a trip the supply stays off until the battery is disconnected. The system needs a way to tell the operator.
- The −HV rail decays more slowly than +HV here because +HV carries the extra test load; with equal loads they fall together (P6b).

## Revision attempt, 2026-11-14 (not completed)
After the results above, the main compensation was corrected to 12.7 kΩ + 68 nF and the optocoupler changed to TCMT1108 (see `calc/CALC_RECORD_2026-11-14.md`). `P8_trip_latch.net` and the two run files now carry those values (CTR 1.0, start point KC 25.6 V, COMP 1.71 V). Both re-runs stalled in the solver after 18 minutes and were stopped. **The results table above is therefore for the earlier values (20.5 kΩ + 820 nF, CTR 0.8) and has not been reproduced with the current ones.** The trip path does not pass through the main compensation, so a large change is not expected [H], but that is not shown.

## Caveats
- Behavioural TL431 with no propagation delay; a real one adds some. The trip delay budget is about 0.1 ms per volt of extra overshoot at this rate of rise.
- The LM5155's response to UVLO going low is modelled as immediate. The fast stop relies on COMP being pulled down first, which the same optocoupler current does.
- UVLO sits at 0.64 V when latched; whether the controller treats that as standby or shutdown needs the datasheet. Either stops switching.
- Noise immunity of the latch gate (10 kΩ, 10 nF) is not tested against real switching noise.
- CTR 1.6, start-up, and battery connection transients were not run.

## Note added 2026-11-15
The stalled re-run above was probably not caused by the circuit. LTspice instances started at the same instant interfere with each other (found during P9). The final simulation P9_final_RECORD.md re-tests both faults with the current values and the real parts: the trip fires and latches in both.
