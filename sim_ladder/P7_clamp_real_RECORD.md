# P7 Real feedback and clamp blocks — record

**Question.** With real TL431 + cascode + optocoupler blocks (one main, one clamp per rail), does a clamp acting through COMP hold a faulted rail under the channel diode's 111 V, and which compensation does it need?
**Status.** sim done 2026-11-14 (LTspice 26.1.1, batch) · four of six cases completed · bench pending

## Setup
| | Sim [L] | Bench [B] |
|---|---|---|
| Circuit | `P7_clamp_real.net` (base), run files `P7_run_B_F1/F2.net`, `P7_run_C_F1/F2.net` | power board |
| Power stage | as P6b: two 10 µH 1:10 transformers, 6 mΩ, 33 µF per rail, 9 V in | |
| Feedback blocks | 3 × 33.2 kΩ divider, behavioural TL431 (from L3), 300 V NPN cascode with 330 kΩ + 12 V bias, 44.1 kΩ LED resistor, 2 kΩ LED shunt, optocoupler CTR 0.8 (worst case) | |
| Main block | 2.49 kΩ, 20.5 kΩ + 820 nF [calc] | |
| Clamp blocks | 2.32 kΩ (109.8 V); compensation A: 100 pF, B: 68 kΩ + 1 nF, C: 68 kΩ + 4.7 nF | |
| COMP pin | 5.11 kΩ to 6.8 V; error amp sourcing 150 µA [ASSUME]; three optocoupler outputs in parallel, 2 nF each [ASSUME] | |
| Load | 91 mA idle per rail plus 80 mA extra on +HV (worst normal case for −HV) | |
| Faults at 3 ms | F1: +HV rectifier opens. F2: main optocoupler output opens | F1 is not a bench test |
| Start | node voltages preset near the operating point; start-up not simulated | |

## Result
| Quantity | B: 68 kΩ + 1 nF | C: 68 kΩ + 4.7 nF | Limit | Pass |
|---|---|---|---|---|
| Before fault: +HV / −HV | +101.9 / −106.5 V | +101.9 / −106.5 V | under 110 V | yes |
| Before fault: clamp optocoupler current | 58 µA peak (capacitive) | same | no clamp action | yes |
| Before fault: main cascode node (KC) | 19.8 V | 19.8 V | above the 12 V shield level | yes, 8 V margin |
| F1: −HV peak | **−114.8 V** | **−118.4 V** | 111 V | **no** |
| F1: −HV 8–9 ms later | −110.7 V, 0.03 V ripple | −112.4 V, still settling | 111 V | B yes |
| F2: +HV peak / −HV peak | +109.8 / **−115.6 V** | +113.8 / **−120.4 V** | 111 V | **no** |
| F2: rails 8–9 ms later | +103.0 / −110.5 V, 2–3 V peak-to-peak | +100.4 / −112.4 V, 3–5 V peak-to-peak | steady | no: limit cycle |

Compensation A (100 pF, no resistor) did not complete: both runs made no progress after 17 minutes and were stopped. No number is claimed for it.

## Verdict
The real main loop regulates and the clamps stay out of the way in normal operation, including the worst load imbalance. A clamp that regulates through COMP is too slow for the window: it overshoots the threshold by 5 V with 1 nF and 8.6 V with 4.7 nF, so the faulted rail passes the diode's 111 V minimum for a few milliseconds. With the main optocoupler open it also limit-cycles by 2–3 V. The cause is structural: to act within 1 V the clamp needs high gain, and a high-gain loop around this power stage is unstable; with low gain it must integrate, and the collector node has about 80 V to slew.

## What it changes
- The clamp compensation question becomes a clamp architecture question: regulate (this test) or trip and latch the converter off.
- Main block: at CTR 0.8 the cascode node sits at 19.8 V at this load and would fall to about 8 V at light load [H], below the 12 V shield level. A smaller LED resistor (about 33 kΩ, with the compensation resistor scaled) would restore margin. Open.
- Three optocoupler outputs on COMP triple its capacitance, which lowers the pole the calculator assumed. Open.

## Caveats
- Behavioural TL431 with no internal dynamics; behavioural optocoupler with fixed CTR and capacitance; idealized PWM.
- The rate at which the faulted rail rises depends on how fast the main loop raises COMP, so the overshoot numbers are specific to this compensation.
- Start-up, and CTR 1.6, were not run.
- Waveform files were deleted after the runs (about 150–180 MB each); running a `.net` regenerates one in about 4 minutes.
