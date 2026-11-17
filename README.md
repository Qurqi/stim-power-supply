# ±102 V isolated flyback supply (STIM power board)

Power board for the 16-channel electrical vestibular stimulator: one LM51551 controller and one switch driving two
Coilcraft DA2034-ALD transformers with primaries in parallel, giving +102.5 V regulated and a following −HV rail,
171 mA per rail from a 9–12.6 V supply. Each rail has a latching over-voltage trip at 109.8 V.

Status: Rev 1 schematic generated and checked; layout not started. Nothing has been built or bench-tested.

## Where things are

| Path | What |
|---|---|
| `FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md` | **The design**: every part, value, connection and JLCPCB number, layout notes, bench checklist |
| `pcb/` | KiCad 10 project. `power_supply.kicad_sch` is generated; see below |
| `pcb/lib/` | Project symbols (LM51551, DA2034-ALD) and the DA2034 footprint |
| `SCHEMATIC_CHANGES_2026-11-14.md` | History: every change from the WEBENCH design and the evidence for it |
| `sim_ladder/` | LTspice netlists (`*.net`), records (`*_RECORD.md`) and analysis scripts |
| `calc/` | TI LM5155 calculator copy and its record |
| `JLCPCB_CHECK_2026-11-14.md`, `DA2034_DATASHEET_CHECK_2026-11-14.md` | Part availability and transformer datasheet checks |

The design rationale (why each choice was made, and the decision log P-1 to P-24) is a shared Claude doc.

## Schematic workflow

The schematic is generated from the parts list so its connectivity can be checked mechanically:

```
cd pcb
python tools/gen_schematic.py      # writes power_supply.kicad_sch and the project libraries
python tools/check_netlist.py      # exports KiCad's netlist and compares it pin by pin with the parts list
kicad-cli sch erc power_supply.kicad_sch
```

Every pin carries a net label, so the drawing is correct but not yet tidy. Once you start editing the schematic by
hand in KiCad, stop regenerating it (the generator overwrites the file) and keep the parts list in step manually.

## Conventions

Numbers in the records are tagged by source: [DS] datasheet, [calc] TI calculator, [L] LTspice, [H] hand
calculation, [B] bench, [ASSUME] assumption. LTspice waveform files (`*.raw`) are not committed; running a
netlist regenerates them.
