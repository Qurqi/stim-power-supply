# 9 V aux rail for the analog board (P-25) — record

**Question.** Can a 9 V LDO fed from the battery supply the analog board's aux input without affecting the ±102 V supply?
**Status.** hand calculation 2026-11-22; not simulated; bench pending.
**Decision.** P-25: the analog-board owner dropped his +12 V input (A1212S module) and wants +9 V instead. The planned ±12 V regulator (P-21) is replaced by this 9 V LDO; the 5 V supply is still open.

Tags: [DS] TI LM2940-N datasheet SNVS769J · [L] P9 simulation · [H] hand calculation · [ASSUME].

## Circuit (schematic block "9 V AUX RAIL")
VIN → FB3 (600 Ω bead, C16902) → VIN_AUX → C36 10 µF 25 V → U8 LM2940IMP-9.0 (SOT-223, C471057) → +9V_AUX → C37 330 µF 25 V electrolytic (C74593) → J3 (placeholder) and TP13. The LDO tab is GND.

## Part data [DS]
| Parameter | Value |
|---|---|
| Output | 9 V, 8.55–9.45 V over 5 mA–1 A and temperature |
| Dropout | 110 mV typ / 200 mV max at 100 mA; 0.5 V typ / 1 V max at 1 A |
| Input range for specified regulation | 10.5–26 V (60 V transient) |
| Ground current | 10 mA typ at 5 mA load; 30 mA typ at 1 A |
| Current limit | about 1.6–1.9 A at 25 °C |
| Output capacitor | at least 22 µF, ESR 0.1–1 Ω |
| Thermal resistance, SOT-223 | 59.3 °C/W |
| Pins | 1 IN, 2 GND, 3 OUT, 4 (tab) GND |

## Effect on the ±102 V supply [H]
| Check | 100 mA aux load | 250 mA aux load | Verdict |
|---|---|---|---|
| Extra battery current (load + ground current) | 112 mA, +2.6 % on the flyback's 4.30 A | 265 mA, +6.2 % | small |
| Extra terminal sag (0.12 Ω source [ASSUME]) | 13 mV | 32 mV | negligible |
| UVLO margin at full HV load (8.37 V [L] vs 7.04 V off) | 1.33 → 1.32 V | 1.33 → 1.30 V | unaffected |
| UVLO margin during start-up (8.05 V [L]) | 1.01 → 1.00 V | 1.01 → 0.98 V | unaffected |
| Controller | BIAS, UVLO divider and current sense are untouched; the LDO only adds load on VIN | | unaffected |
| Converter input ripple (0.21 V p-p at 252 kHz [L]) into the LDO | FB3 plus C36 (0.063 Ω at 252 kHz) filter it before the LDO; the LDO's rejection at 252 kHz is not specified | | see caveats |
| Short on the 9 V output | LDO limits at about 1.9 A, battery current rises to about 6.2 A at 9 V, extra sag about 0.23 V; UVLO still above 7.04 V; LDO shuts down thermally | | HV supply keeps running |
| HV trip and latch | the LDO is not switched by UVLO, so +9 V stays up when the HV supply latches off | | analog board stays powered with HV off, the safe state |
| Power-up order | +9 V is up within milliseconds of the supply; HV takes about 54 ms (S680 [L]) | | low-voltage rail before HV, as wanted |

## The LDO itself [H]
| Input | Dissipation at 100 mA | at 250 mA |
|---|---|---|
| 12.6 V | 0.51 W, junction +30 °C | 1.09 W, +65 °C |
| 11.1 V | 0.34 W, +20 °C | 0.69 W, +41 °C |
| 10.5 V | 0.28 W, +16 °C | 0.53 W, +32 °C |

Thermal limit at 12.6 V input and 50 °C ambient (junction ≤ 125 °C): about 300 mA. **The rail is rated 250 mA.** Give the tab copper on the board.

## Limitation: 9 V needs more than 9 V in
The LDO regulates only while the input is above about 9.2 V (9 V plus dropout). Below that the output follows the battery:

| Input (battery terminal) | +9V_AUX at 100 mA, typ / worst |
|---|---|
| 9.2 V or more | 9.00 V |
| 9.0 V (empty battery, light HV load) | 8.89 / 8.80 V |
| 8.48 V (9 V source at full HV load [L]) | 8.37 / 8.28 V |

On Rev 1 with a bench supply (P-23), set the supply to 10.5 V or more and the rail is fully regulated. On a battery, the rail sits a few hundred millivolts low near the end of discharge. A buck-boost converter would hold 9 V to empty, at the cost of switching noise on the analog board's supply.

## Output capacitor
The LM2940 needs at least 22 µF with ESR between 0.1 and 1 Ω for stability. A ceramic capacitor's ESR is too low, so C37 is the 330 µF 25 V electrolytic already on the BOM: at 120 Hz its ESR is about 0.56 Ω [H, tan δ 0.14 ASSUME]. Its ESR was not on the JLCPCB page; confirm on the bench that the rail does not ring after a load step.

## Caveats
- The analog board's 9 V load current is not known; 100 and 250 mA bracket it. Get the figure from the analog-board owner.
- His board also needs −9 V (OPA192 on ±9 V) and +5 V; how he now makes them is his design. This rail provides +9 V only.
- LDO rejection at 252 kHz is not on the datasheet (64 dB is at 120 Hz); measure ripple on +9V_AUX at the bench.
- At low temperature an electrolytic's ESR rises and could pass 1 Ω; fine for indoor use.
