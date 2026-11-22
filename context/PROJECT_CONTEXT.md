# Project context: STIM ±102 V power board

Status 2026-11-22. A briefing for anyone picking up this board, written from the design sessions of 14–22 Nov 2026.
Read this first, then `../FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md` (the design itself) and `DESIGN_RATIONALE.md`
(why each choice was made, as a chronological log).

## 1. What this board is

The power board of a 16-channel electrical vestibular stimulator (UBC ELEC 491 capstone, project JY063). Each
channel is a bootstrapped Howland current pump (INA149) on the analog board, which needs a positive and a negative
high-voltage rail. This board makes those rails from a three-cell lithium-ion battery (9–12.6 V), plus a 9 V aux rail
for the analog board.

| Item | Value |
|---|---|
| Rails | +102.5 V regulated; −HV follows, 5–7 V lower at full load |
| Rated load | 171 mA per rail at 9 V input (131 mA at the 5 mA operating point) |
| Topology | one LM51551 controller, one CSD19531Q5A switch, two Coilcraft DA2034-ALD transformers with primaries in parallel, 252 kHz, continuous conduction |
| Protection | latching trip at 109.8 V on either rail; 16.2 A primary current limit; undervoltage lockout 7.5 V on / 7.0 V off |
| Start-up | primary-side soft start (680 nF) plus a start-up network on the feedback block |
| Aux | 9 V LDO (LM2940IMP-9.0), 250 mA, fed from the battery input |
| Efficiency | 86.5 % at 9 V and full load [L]; ripple after the filter 6–7 mV [L] |
| Status | schematic generated and verified; **layout not started; nothing built or bench-tested** |

## 2. Who owns what

| Area | Owner | Where |
|---|---|---|
| Power board (this repo) | power-board owner | this repository |
| Analog channel board (Howland pump) | analog-board owner | his own workspace: Rev 1 single-channel KiCad project, acceptance tests A1–A8, decisions D-A to D-H, FMEA, ICD for the FPGA connector |
| FPGA, DAC, firmware | CPEN team members | Red Pitaya |

Interfaces between the boards are **not yet agreed** (P-22): J2 (HV out: +HV, GND, −HV) and J3 (+9 V aux) are
placeholders. The analog board's Rev 1 HV connector J1 is +HV, GND, −HV.

## 3. How the design got here

1. **Requirement.** Started as a single +100 V rail at 80 mA for 8 channels. Clarified to 16 channels (8 source, 8
   sink), 10 mA each, ±rails, patient-connected load (electrodes on skin), so isolation and low noise mattered.
2. **WEBENCH baseline** (+110 V, 100 mA, LM51551 isolated flyback). Its secondary feedback template used 25–36 V parts
   on a 110 V rail; redesigned with a 300 V cascode transistor shielding the TL431 (P-2).
3. **Isolation.** The analog board's grounds are joined through the DACs and FPGA, so a transformer barrier protects
   nobody. Patient isolation moved to the device boundary (charger, data links); the transformer is functional only
   (P-3). This made a catalogue transformer acceptable.
4. **Reading the analog team's records** changed the load: each channel idles at about 5.2 mA per rail (their A1),
   plus bleeders, so the supply must deliver 131–171 mA per rail, not 80–100 mA. Their D-B (5 mA into ≤ 13 kΩ)
   allowed a lower setpoint. Their A7 (one rail without the other drives the load) drove the topology.
5. **Rail tracking (P-6).** Two independent converters can fail one at a time; an interlock cannot guarantee safety.
   Chose one converter driving two transformers with primaries in parallel, so the rails rise and fall together.
   LTspice check P6 confirmed tracking within about 5 V.
6. **Setpoint 102 V (P-12)** to keep voltage exposure low and margin under the channel's 110–111 V limits.
7. **Over-voltage protection.** A regulating clamp per rail (P7) overshot to 115 V; changed to a comparator trip that
   latches the converter off through the UVLO pin (P-13, check P8: peak 110.06 V).
8. **TI calculator validation** of the shared-switch design (entered as one 5 µH / 0.43 A converter). Found an error:
   the compensation was 12.7 kΩ + 68 nF, not 20.5 kΩ + 820 nF (P-14).
9. **JLCPCB library checks.** Several first-choice parts had almost no stock; the polymer input capacitor had none.
   Substitutes chosen; the transformer is not at JLCPCB and is bought separately and hand-soldered (P-24).
10. **Final simulation P9** with real parts and losses found: pulse skipping (fixed with a 2.2 nF sense filter, P-16);
    −HV sitting 5–7 V low (accepted, P-17); lockout too close to battery sag (lowered to 7.5/7.0 V, P-18); 215 mA not
    reachable, rated 171 mA (P-19); start-up overshoot tripping the latch (start-up network fitted); and a 26 A
    start-up current surge, fixed by a primary-side soft start with 680 nF (P-20).
11. **Schematic** generated in KiCad 10 from the parts list and verified mechanically (ERC clean, netlist pin-for-pin,
    values against the simulation).
12. **9 V aux rail (P-25).** The analog board dropped its +12 V input; a 9 V LDO on this board now feeds it.

## 4. Decision log

| ID | Date | Decision | Why |
|---|---|---|---|
| P-1 | 14 Nov | Isolated flyback, LM51551, secondary-side feedback | regulates to zero load; isolation available |
| P-2 | 14 Nov | Cascode (MMBTA42) shields the TL431 from the HV rail | TL431 is a 36 V part |
| P-3 | 14 Nov | Patient isolation at the device boundary; transformer functional only | grounds are joined through the DAC/FPGA path |
| P-4 | 14 Nov | 215 mA per rail (superseded by P-19) | idle current cannot come down |
| P-5 | 14 Nov | 104 V (superseded by P-12) | |
| P-6 | 14 Nov | One converter, two catalogue transformers, primaries in parallel | removes single-converter faults by construction |
| P-7 | 14 Nov | LC filter only; capacitance multiplier dropped | A8 suggests enough rejection |
| P-8 | 14 Nov | Three-cell lithium-ion battery | power level |
| P-9 | 14 Nov | Size for 16 channels | |
| P-10 | 14 Nov | Low-voltage rails from an off-the-shelf regulator (refined by P-21, P-25) | |
| P-11 | 14 Nov | Keep the catalogue-transformer design (3 Nov custom-transformer design superseded) | off-the-shelf priority |
| P-12 | 14 Nov | Setpoint 102 V | lower voltage exposure; margin to 110 V |
| P-13 | 14 Nov | Over-voltage trip per rail, latched off until the battery is removed | regulating clamp overshot to 115 V |
| P-14 | 15 Nov | CSD19531Q5A switch and TCMT1108 optocouplers; compensation 12.7 kΩ + 68 nF | JLCPCB stock; calculator |
| P-15 | 15 Nov | Output bulk 3 × 10 µF 200 V + 1 µF ceramic per rail | 33 µF part thinly stocked |
| P-16 | 15 Nov | Current-sense filter 2.2 nF | stops pulse skipping |
| P-17 | 15 Nov | Accept −HV 5–7 V low at full load | sink-side headroom to spare |
| P-18 | 15 Nov | UVLO 7.5 V on / 7.0 V off (49.9 kΩ / 12.4 kΩ) | battery sag margin |
| P-19 | 15 Nov | Rated 171 mA per rail at 9 V | switch at 88 % of its limit at 171 mA |
| P-20 | 16 Nov | Primary-side soft start, MMBT3906 + 680 nF | start-up current surge; LM51551 hiccup |
| P-21 | 16 Nov | Off-the-shelf ±12 V and 5 V for the analog board (±12 V superseded by P-25) | |
| P-22 | 16 Nov | Board connectors laid out as placeholders; agree with the analog-board owner later | |
| P-23 | 16 Nov | Rev 1 runs from a bench supply; battery-side protection in Rev 2 | |
| P-24 | 16 Nov | DA2034-ALD bought outside JLCPCB, hand-soldered | not in the JLCPCB library |
| P-25 | 22 Nov | 9 V LDO (LM2940IMP-9.0) from the battery for the analog board | analog board now takes +9 V |

## 5. Open items

**Before ordering:**
- Agree J2 (HV) and J3 (+9 V) connectors and the 5 V supply with the analog-board owner.
- Get the analog board's 9 V load current (the LDO is rated 250 mA).
- Choose the 5 V supply (P-21).
- Cross-check the DA2034 footprint against Coilcraft's drawing.
- Look up the standard resistor and capacitor values at JLCPCB at order time ("not looked up" in the design file).
- Tidy the schematic into readable wiring (every pin currently has a net label).

**Layout (not started):** see section 9 of the design file. The high-current primary loop, transformer symmetry,
sense filter at the controller, clamp heat, high-voltage spacing (follow JLCPCB's rules, with extra room on the
390–470 V rectifier nodes), quiet nodes for the feedback references and latch.

**Bench (section 11 of the design file):** pulse skipping with 2.2 nF, trip level against 111 V, start-up and soft start,
rectifier snubber, clamp loss and transformer temperature, −HV level, channel idle current, ripple to load, 9 V rail.

**Rev 2:** battery connector, fuse, reverse-polarity and over-discharge protection; a tripped indicator; Coilcraft
approval before any use on a person (the DA2034 datasheet restricts medical use without it).

## 6. Things learned the hard way

- **JLCPCB search results include parts with zero stock.** Open each part's own page to check stock.
- **LTspice instances started at the same instant interfere**: only the last one runs properly. `sim_ladder/run_monitored.ps1` leaves 25 s between launches and stops runs that make no progress.
- **The P9 TL431 model turns on softly**, so the regulated rail reads about 2 V low (100.35 V instead of about 102.5 V) and trip levels read about 2 V low. Trip-level margins rest on P8.
- **The TI calculator derives its compensation capacitor from the selected resistor cell**, so a stale cell gives a wrong capacitor.
- **The TL431 and TL432 SOT-23 pinouts differ.** Order TL431BIDBZR.
- **The LM2940 needs 0.1–1 Ω of output-capacitor ESR**; a ceramic output capacitor can make it oscillate.
- **Simulation waveforms are large** (up to 1.8 GB). They are git-ignored; rerun a netlist to regenerate.

## 7. Conventions

- Numbers tagged by source: [DS] datasheet, [calc] TI calculator, [L] LTspice, [H] hand calculation, [B] bench, [ASSUME].
- Decisions logged as P-n, with date, options, evidence and choice; the analog board uses D-x.
- Options are framed with evidence; the owner of the board decides.
- Simulations are added only when they gate a decision or have a bench twin.
- The schematic's reference designators are authoritative; the design file's section 13 maps its working names.

## 8. Working on this repo in parallel

- **Schematic.** `pcb/power_supply.kicad_sch` is generated by `pcb/tools/gen_schematic.py` from the parts list in that
  script. While it is still generated, change parts in the script, then regenerate and run the checks (see the
  top-level README). Once anyone edits the schematic by hand in KiCad, stop regenerating, and say so in the README so
  the other person does not overwrite it.
- **Avoid editing the same KiCad file at the same time.** KiCad files merge poorly. Split work by file (for example,
  one person on layout `.kicad_pcb`, the other on records and simulations) or by branch, and merge often.
- **Records.** Add a new `*_RECORD.md` for each check, in the existing format (question, setup, result, verdict, what
  it changes, caveats), and add any decision to the log here and in the design file.
- **Tools needed:** KiCad 10, LTspice, Python 3 with NumPy, Excel (for the TI calculator), Git.

## 9. Key sources

- TI LM5155/LM51551 datasheet (SNVSB75E); LM51551 has hiccup protection, LM5155 does not.
- TI LM2940-N datasheet (SNVS769J).
- Coilcraft Document 510 (DA2032/2033/2034).
- Vishay TCMT1100 series datasheet (83510).
- TI TL431 datasheet (pin table, DBZ package).
- TI CSD19531Q5A datasheet.
- The analog-board owner's workspace: decisions D-A to D-H, tests A1, A7, A8, FMEA, ICD_J3, Rev 1 design definition.
