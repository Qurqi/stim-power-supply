# Project context: STIM ±102 V power board

Status 27 Nov 2026. This is a briefing for anyone picking up this board, written from the design sessions of 14–27 Nov 2026. Read it first, then [`../DESIGN.md`](../DESIGN.md) for the design itself and [`DESIGN_RATIONALE.md`](DESIGN_RATIONALE.md) for why each choice was made, as a chronological log.

## 1. What this board is

This is the power board of a multi-channel electrical vestibular stimulator (UBC ELEC 491 capstone, project JY063). Each channel is a bootstrapped Howland current pump (INA149) on the channel board, which needs a positive and a negative high-voltage rail. This board makes those rails from a three-cell lithium-ion battery (9–12.6 V). It also passes fused battery voltage to the channel board, which makes its own low-voltage rails.

| Item | Value |
|---|---|
| Rails | +102.5 V regulated; −HV follows, 5–7 V closer to ground at full load |
| Rated load | 171 mA per rail at 9 V input: 16 channels at the 10 mA fault limit (requirement 4 channels, goal 8) |
| Topology | One LM51551 controller, one CSD19531Q5A switch, two Coilcraft DA2034-ALD transformers with primaries in parallel; 252 kHz, continuous conduction |
| Regulation | Secondary side (TL431B and optocoupler on +HV_RAW) |
| Protection | Latching trip at 109.8 V on either rail; 16.2 A primary current limit; undervoltage lockout on at 7.5 V, off at 7.0 V; 10 A input fuse |
| Start-up | Primary-side soft start (680 nF) plus a start-up network on the feedback block |
| Grounds | PGND and AGND (primary) isolated from SGND (HV return), so the channel board's isolation barrier stays intact |
| Battery feed out | Battery voltage through a 500 mA fuse to the channel board |
| Efficiency | 86.5 % at 9 V and full load [L]; ripple after the filter 6–7 mV [L] |
| Status | Hierarchical schematic complete; **layout not started; nothing built or bench-tested** |

## 2. Who owns what

| Area | Owner | Where |
|---|---|---|
| Power board (this repo) | Power-board owner | This repository |
| Channel board (Howland pumps, isolators, DAC, ADC) | Channel-board owner | [Capstone-Stimulator-Channel](https://github.com/WeymenKoo/Capstone-Stimulator-Channel): 4-channel KiCad project, acceptance tests A1–A8, decisions D-A onward, FMEA, safety loop, ICD for the FPGA connector |
| FPGA, firmware | CPEN team members | Red Pitaya |

Interfaces between the boards are **not yet agreed** (P-22):

| This board | Carries | Channel board |
|---|---|---|
| J2 (placeholder) | +HV, SGND, −HV | J1 HV input (+HV / COM / −HV), participant side (ISO_GND) |
| J3 (placeholder) | Fused battery voltage, PGND | J2 VBAT input, FPGA side |

## 3. How the design got here

1. **Requirement.** Started as a single +100 V rail at 80 mA for 8 channels. Clarified to 16 channels (8 source, 8 sink), 10 mA each, ± rails, and a patient-connected load (electrodes on skin), so isolation and low noise mattered.
2. **WEBENCH baseline** (+110 V, 100 mA, LM51551 isolated flyback). Its secondary feedback template used 25–36 V parts on a 110 V rail; we redesigned it with a 300 V cascode transistor shielding the TL431 (P-2).
3. **Isolation, first pass.** At the time the channel board's grounds were joined through the DACs and FPGA, so a transformer barrier protected nobody. We put patient isolation at the device boundary and treated the transformer as functional only (P-3). This made a catalogue transformer acceptable.
4. **Reading the channel team's records** changed the load: each channel idles at about 5.2 mA per rail (their A1), plus bleeders, so the supply must deliver 131–171 mA per rail, not 80–100 mA. Their D-B (5 mA into ≤ 13 kΩ) allowed a lower setpoint. Their A7 (one rail without the other drives the load) drove the topology.
5. **Rail tracking (P-6).** Two independent converters can fail one at a time, and an interlock cannot guarantee safety. We chose one converter driving two transformers with primaries in parallel, so the rails rise and fall together. LTspice check P6 confirmed tracking within about 5 V.
6. **Setpoint 102 V (P-12)** to keep voltage exposure low and leave margin under the channel's 110–111 V limits.
7. **Over-voltage protection.** A regulating clamp per rail (P7) overshot to 115 V, so we changed to a comparator trip that latches the converter off through the UVLO pin (P-13, check P8: peak 110.06 V).
8. **TI calculator validation** of the shared-switch design (entered as one 5 µH, 0.43 A converter). It found an error: the compensation was 12.7 kΩ + 68 nF, not 20.5 kΩ + 820 nF (P-14).
9. **JLCPCB library checks.** Several first-choice parts had almost no stock, and the polymer input capacitor had none. We chose substitutes; the transformer is not at JLCPCB, so it is bought separately and hand-soldered (P-24).
10. **Final simulation P9** with real parts and losses found five problems, each now fixed or accepted:
    - pulse skipping, fixed with a 2.2 nF sense filter (P-16);
    - −HV sitting 5–7 V low, accepted (P-17);
    - lockout too close to battery sag, lowered to 7.5/7.0 V (P-18);
    - 215 mA not reachable, so the supply is rated at 171 mA (P-19);
    - start-up overshoot tripping the latch, fixed with a start-up network, and a 26 A start-up current surge, fixed with a primary-side soft start of 680 nF (P-20).
11. **Schematic** generated in KiCad 10 from the parts list and verified mechanically (ERC clean, netlist pin for pin, values against the simulation).
12. **9 V aux rail (P-25, 22 Nov).** The channel board dropped its +12 V input and asked for +9 V, so we added a 9 V LDO. Superseded on 26 Nov (P-27).
13. **Hierarchical schematic and protection updates (26 Nov, commit `af865cc`).** The top sheet became a block diagram with one sub-sheet per block. The grounds were split into PGND, AGND and SGND. A 10 A input fuse was added, the LDO was replaced by a fused battery feed, and 20 kΩ bleeders were added on each rail (P-27, P-28). Per-sheet ngspice benches were added in `sim_ladder/sheet_benches/`; they showed the two transformers must be paired within 2 % primary inductance.
14. **Isolation, second pass (P-26, 27 Nov).** The channel board now isolates its FPGA side from its participant side with a 7.0 mm barrier. Its VBAT input is on the FPGA side and its HV return on the participant side. The net tie NT2 joining SGND to PGND would have bypassed that barrier, so we removed it and added an SGND test point (TP13).

## 4. Decision log

| ID | Date | Decision | Why |
|---|---|---|---|
| P-1 | 14 Nov | Isolated flyback, LM51551, secondary-side feedback | Regulates to zero load; senses the rails directly, so no accumulated error slows the response to a rail fault; isolation available |
| P-2 | 14 Nov | Cascode (MMBTA42) shields the TL431 from the HV rail | TL431 is a 36 V part |
| P-3 | 14 Nov | Transformer isolation functional only (single ground tie later replaced by P-26) | Grounds then joined through the DAC/FPGA path |
| P-4 | 14 Nov | 215 mA per rail (superseded by P-19) | Idle current cannot come down |
| P-5 | 14 Nov | 104 V (superseded by P-12) | |
| P-6 | 14 Nov | One converter, two catalogue transformers, primaries in parallel | Removes single-converter faults by construction |
| P-7 | 14 Nov | LC filter only; capacitance multiplier dropped | A8 suggests enough rejection |
| P-8 | 14 Nov | Three-cell lithium-ion battery | Power level |
| P-9 | 14 Nov | Size for 16 channels | Requirement 4, goal 8; fewer channels only reduce the load |
| P-10 | 14 Nov | Low-voltage rails from an off-the-shelf regulator (refined by P-21, P-25, P-27) | |
| P-11 | 14 Nov | Keep the catalogue-transformer design (3 Nov custom-transformer design superseded) | Off-the-shelf priority |
| P-12 | 14 Nov | Setpoint 102 V | Lower voltage exposure; margin to 110 V |
| P-13 | 14 Nov | Over-voltage trip per rail, latched off until the battery is removed | Regulating clamp overshot to 115 V |
| P-14 | 15 Nov | CSD19531Q5A switch and TCMT1108 optocouplers; compensation 12.7 kΩ + 68 nF | JLCPCB stock; calculator |
| P-15 | 15 Nov | Output bulk 3 × 10 µF 200 V + 1 µF ceramic per rail | 33 µF part thinly stocked |
| P-16 | 15 Nov | Current-sense filter 2.2 nF | Stops pulse skipping |
| P-17 | 15 Nov | Accept −HV 5–7 V low at full load | Sink-side headroom to spare |
| P-18 | 15 Nov | UVLO 7.5 V on / 7.0 V off (49.9 kΩ / 12.4 kΩ) | Battery sag margin |
| P-19 | 15 Nov | Rated 171 mA per rail at 9 V | Switch at 88 % of its limit at 171 mA |
| P-20 | 16 Nov | Primary-side soft start, MMBT3906 + 680 nF | Start-up current surge; LM51551 hiccup |
| P-21 | 16 Nov | Off-the-shelf ±12 V and 5 V for the channel board (superseded by P-25, P-27) | |
| P-22 | 16 Nov | Board connectors laid out as placeholders; agree with the channel-board owner later | |
| P-23 | 16 Nov | Bench supply for first power-up; battery-side protection later (input fuse added by P-27; discharge protection in the next design document) | |
| P-24 | 16 Nov | DA2034-ALD bought outside JLCPCB, hand-soldered | Not in the JLCPCB library |
| P-25 | 22 Nov | 9 V LDO (LM2940IMP-9.0) for the channel board (superseded by P-27) | Channel board then took +9 V |
| P-26 | 27 Nov | Keep the channel board's isolation barrier: SGND isolated from PGND; NT2 removed; SGND test point TP13 added | Tying SGND to PGND bypassed the channel board's 7.0 mm barrier |
| P-27 | 26 Nov | Battery input J1 with 10 A slow-blow fuse F2; LDO removed; fused battery feed (F1 500 mA, J3) to the channel board | Channel board makes its own rails from VBAT (its D-I) |
| P-28 | 26 Nov | 20 kΩ bleeder per HV rail (R54–R57) | Supply regulates with no load attached |

## 5. Open items

**Before ordering:**
- Agree J2 (HV) and J3 (battery feed) connectors and pin-outs with the channel-board owner.
- Confirm the F1 (500 mA) rating against the channel board's measured draw (estimated 0.13 A at 9 V).
- Run ERC and `pcb/tools/check_netlist.py` in KiCad after the P-26 ground change.
- Cross-check the DA2034 footprint against Coilcraft's drawing.
- Look up the standard resistor and capacitor values at JLCPCB at order time.

**Design, later:**
- Battery discharge protection (next design document).
- Whether to add a capacitor across the barrier (SGND to PGND) for switching noise. It trades noise against leakage across the barrier.
- This board's bleeders add about 5.1 mA per rail on top of the 171 mA rating; confirm the margin.
- Trip indication for the operator (FR-11).
- Coilcraft approval and insulation verification before any use on a person (see `../DESIGN.md` §3).

**Layout (not started):** see [`../DESIGN.md`](../DESIGN.md) §8: the high-current primary loop, transformer symmetry, the sense filter at the controller, clamp heat, the gap between the primary and secondary grounds, high-voltage spacing, and quiet nodes for the references and latch.

**Bench:** see [`../DESIGN.md`](../DESIGN.md) §9.

## 6. Things learned the hard way

- **JLCPCB search results include parts with zero stock.** Open each part's own page to check stock.
- **LTspice instances started at the same instant interfere**: only the last one runs properly. `sim_ladder/run_monitored.ps1` leaves 25 s between launches and stops runs that make no progress.
- **The P9 TL431 model turns on softly**, so the regulated rail reads about 2 V low (100.35 V instead of about 102.5 V) and trip levels read about 2 V low. Trip-level margins rest on P8.
- **The TI calculator derives its compensation capacitor from the selected resistor cell**, so a stale cell gives a wrong capacitor.
- **The TL431 and TL432 SOT-23 pinouts differ.** Order TL431BIDBZR.
- **Mismatched paralleled transformers ring.** Beyond about 2 % primary-inductance mismatch, start-up winding currents rise well above the 10 A rating in simulation [N]. Pair them.
- **Simulation waveforms are large** (up to 1.8 GB). They are git-ignored; rerun a netlist to regenerate.
- **A ground tie can defeat another board's isolation.** Check every connection between boards against their ground domains.

## 7. Conventions

- Numbers are tagged by source: [DS] datasheet, [calc] TI calculator, [L] LTspice, [N] ngspice, [H] hand calculation, [B] bench, [ASSUME] assumption.
- Decisions are logged as P-n, with date, options, evidence and choice; the channel board uses D-x.
- Options are framed with evidence; the owner of the board decides.
- Simulations are added only when they gate a decision or have a bench twin.
- The schematic's reference designators are authoritative; `../DESIGN.md` uses them throughout.

## 8. Working on this repo in parallel

- **Schematic.** Edit it in KiCad. `pcb/tools/gen_schematic.py` writes the old flat schematic; do not run it. Keep `pcb/tools/intended_netlist.json` in step and run the checks in the top-level README.
- **Avoid editing the same KiCad file at the same time.** KiCad files merge poorly. Split work by file (for example, one person on layout, the other on records and simulations) or by branch, and merge often.
- **Records.** Add a new `*_RECORD.md` for each check, in the existing format (question, setup, result, verdict, what it changes, caveats), and add any decision to the log here and to `../DESIGN.md`.
- **Tools needed:** KiCad 10, LTspice, ngspice 42, Python 3 with NumPy, Excel (for the TI calculator), Git.

## 9. Key sources

- TI LM5155/LM51551 datasheet (SNVSB75E); the LM51551 has hiccup protection, the LM5155 does not.
- Coilcraft Document 510 (DA2032/2033/2034).
- Vishay TCMT1100 series datasheet (83510).
- TI TL431 datasheet (pin table, DBZ package).
- TI CSD19531Q5A datasheet.
- Channel board repository: decisions, tests A1, A7, A8, FMEA, safety loop, ICD J3, `02_rev1_channel/PWR_Rev1/README.md` (load estimates).
