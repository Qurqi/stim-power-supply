"""Generate the KiCad schematic for the +/-102 V flyback supply from the parts list.

Source of truth for parts, values and connections: FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md (repository root).
Every part is placed on one sheet, grouped by block, and every pin gets a net label, so connectivity is
exact even though the drawing is not yet tidied into wires. Run:

    python tools/gen_schematic.py          (from the pcb folder)

It writes power_supply.kicad_sch, lib/power_supply.kicad_sym, lib/power_supply.pretty/*, the library
tables and a minimal project file, and prints the intended netlist to tools/intended_netlist.json so the
check script can compare it with what KiCad exports.
"""
import copy
import json
import os
import re
import uuid

KLIB = r'C:\Users\Johnd\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols'
TOOLS = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(TOOLS)
NAME = 'power_supply'
ROOT_UUID = '6f0d1c2a-1b2c-4d3e-9f10-2a3b4c5d6e7f'   # fixed so regenerating keeps the same sheet identity


# ------------------------------------------------------------------ s-expressions
class Q(str):
    """A quoted string, stored already escaped."""


def esc(s):
    return Q(str(s).replace('\\', '\\\\').replace('"', '\\"'))


def tokenize(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n':
            i += 1
        elif c in '()':
            yield c
            i += 1
        elif c == '"':
            j = i + 1
            while s[j] != '"':
                j += 2 if s[j] == '\\' else 1
            yield Q(s[i + 1:j])
            i = j + 1
        else:
            j = i
            while j < n and s[j] not in ' \t\r\n()':
                j += 1
            yield s[i:j]
            i = j


def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]


def atom(e):
    if isinstance(e, Q):
        return '"%s"' % e
    if isinstance(e, float):
        return ('%.4f' % e).rstrip('0').rstrip('.')
    return str(e)


def ser(x, ind=0):
    if not isinstance(x, list):
        return atom(x)
    if not any(isinstance(e, list) for e in x):
        return '(' + ' '.join(atom(e) for e in x) + ')'
    head = []
    rest = []
    for e in x:
        if isinstance(e, list) or rest:
            rest.append(e)
        else:
            head.append(e)
    out = '(' + ' '.join(atom(e) for e in head)
    for e in rest:
        out += '\n' + '\t' * (ind + 1) + ser(e, ind + 1)
    return out + '\n' + '\t' * ind + ')'


def S(text):
    return parse(text)[0]


def uid():
    return str(uuid.uuid4())


# ------------------------------------------------------------------ custom library
LM51551 = '''
(symbol "LM51551" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 (property "Reference" "U" (at 0 17.78 0) (effects (font (size 1.27 1.27))))
 (property "Value" "LM51551" (at 0 -20.32 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" "https://www.ti.com/lit/ds/symlink/lm5155.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Description" "Wide-VIN boost/flyback/SEPIC controller with hiccup protection, WSON-12 (DSS)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (symbol "LM51551_0_1" (rectangle (start -7.62 15.24) (end 7.62 -15.24) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "LM51551_1_1"
  (pin power_in line (at -10.16 12.7 0) (length 2.54) (name "BIAS" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
  (pin input line (at -10.16 7.62 0) (length 2.54) (name "UVLO/EN/SYNC" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
  (pin input line (at -10.16 2.54 0) (length 2.54) (name "RT" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
  (pin input line (at -10.16 -2.54 0) (length 2.54) (name "SS" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
  (pin input line (at -10.16 -7.62 0) (length 2.54) (name "FB" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
  (pin output line (at -10.16 -12.7 0) (length 2.54) (name "COMP" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
  (pin power_out line (at 10.16 12.7 180) (length 2.54) (name "VCC" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
  (pin output line (at 10.16 7.62 180) (length 2.54) (name "GATE" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
  (pin input line (at 10.16 2.54 180) (length 2.54) (name "CS" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
  (pin power_in line (at 10.16 -2.54 180) (length 2.54) (name "PGND" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
  (pin power_in line (at 10.16 -7.62 180) (length 2.54) (name "AGND" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
  (pin open_collector line (at 10.16 -12.7 180) (length 2.54) (name "PGOOD" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
  (pin passive line (at 0 -17.78 90) (length 2.54) (name "EP" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
 )
 (embedded_fonts no))
'''

DA2034 = '''
(symbol "DA2034-ALD" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 (property "Reference" "T" (at 0 15.24 0) (effects (font (size 1.27 1.27))))
 (property "Value" "DA2034-ALD" (at 0 -15.24 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "power_supply:Coilcraft_DA2034" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" "https://www.coilcraft.com/getmedia/88ef6a9b-3558-4004-8c5f-af97c95c7e8c/da2032.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Description" "Flyback transformer 10 uH, 1:10, 10 A, four primary windings to be paralleled; dots on 7-10 and 1" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (symbol "DA2034-ALD_0_1"
  (rectangle (start -5.08 12.7) (end 5.08 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))
  (circle (center -3.81 10.16) (radius 0.381) (stroke (width 0) (type default)) (fill (type outline)))
  (circle (center 3.81 7.62) (radius 0.381) (stroke (width 0) (type default)) (fill (type outline)))
  (polyline (pts (xy 0 11.43) (xy 0 -11.43)) (stroke (width 0.254) (type default)) (fill (type none))))
 (symbol "DA2034-ALD_1_1"
  (pin passive line (at -7.62 10.16 0) (length 2.54) (name "P1S" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 7.62 0) (length 2.54) (name "P2S" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 5.08 0) (length 2.54) (name "P3S" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 2.54 0) (length 2.54) (name "P4S" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 -2.54 0) (length 2.54) (name "P4F" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 -5.08 0) (length 2.54) (name "P3F" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 -7.62 0) (length 2.54) (name "P2F" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
  (pin passive line (at -7.62 -10.16 0) (length 2.54) (name "P1F" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
  (pin passive line (at 7.62 7.62 180) (length 2.54) (name "SDOT" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
  (pin passive line (at 7.62 -7.62 180) (length 2.54) (name "S" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
  (pin no_connect line (at 7.62 2.54 180) (length 2.54) hide (name "NC" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
  (pin no_connect line (at 7.62 -2.54 180) (length 2.54) hide (name "NC" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
 )
 (embedded_fonts no))
'''

DA2034_FP = '''(footprint "Coilcraft_DA2034"
 (version 20241229) (generator "gen_schematic.py") (layer "F.Cu")
 (descr "Coilcraft DA2034-AL flyback transformer, 12 gull-wing leads, 3.0 mm pitch; pad geometry from LCSC/EasyEDA footprint C5354095, cross-check against Coilcraft Doc 510-2 before ordering")
 (tags "transformer flyback Coilcraft DA2034")
 (property "Reference" "REF**" (at 0 -12.2 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (property "Value" "Coilcraft_DA2034" (at 0 12.2 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (attr smd)
{pads}
 (fp_rect (start -10.5 -10.285) (end 10.5 10.285) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))
 (fp_circle (center -17.0 -7.5) (end -16.6 -7.5) (stroke (width 0.25) (type solid)) (fill yes) (layer "F.SilkS"))
 (fp_rect (start -10.5 -10.285) (end 10.5 10.285) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
 (fp_rect (start -15.7 -11.0) (end 15.7 11.0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
)
'''


def da2034_pads():
    lines = []
    for n in range(1, 13):
        if n <= 6:
            x, y = -13.46, -7.5 + 3.0 * (n - 1)
        else:
            x, y = 13.46, 7.5 - 3.0 * (n - 7)
        lines.append(' (pad "%d" smd rect (at %.2f %.2f) (size 3.3 1.27) (layers "F.Cu" "F.Paste" "F.Mask"))' % (n, x, y))
    return '\n'.join(lines)


# ------------------------------------------------------------------ library access
_trees = {}


def lib_tree(lib):
    if lib not in _trees:
        if lib == NAME:
            text = '(kicad_symbol_lib ' + LM51551 + DA2034 + ')'
        else:
            text = open(os.path.join(KLIB, lib + '.kicad_sym'), encoding='utf-8').read()
        _trees[lib] = parse(text)[0]
    return _trees[lib]


def find_sym(lib, name):
    for c in lib_tree(lib):
        if isinstance(c, list) and c and c[0] == 'symbol' and c[1] == name:
            return c
    raise KeyError('%s:%s not found' % (lib, name))


def flatten(lib, name):
    s = copy.deepcopy(find_sym(lib, name))
    ext = [c for c in s if isinstance(c, list) and c and c[0] == 'extends']
    if not ext:
        return s
    pname = ext[0][1]
    parent = flatten(lib, pname)
    child_props = {c[1]: c for c in s if isinstance(c, list) and c and c[0] == 'property'}
    # parent properties, overridden by the child's of the same name, then the child's new ones
    props = []
    for c in parent[2:]:
        if isinstance(c, list) and c and c[0] == 'property':
            props.append(child_props.pop(c[1], c))
    props += list(child_props.values())
    out = [parent[0], Q(name)]
    for c in parent[2:]:
        if isinstance(c, list) and c and c[0] == 'property':
            continue
        if isinstance(c, list) and c and c[0] == 'symbol':
            c = copy.deepcopy(c)
            c[1] = Q(name + c[1][len(pname):])
            out.append(c)
        else:
            out.append(c)
    # properties go before the unit sub-symbols
    first_sub = next(i for i, c in enumerate(out) if isinstance(c, list) and c and c[0] == 'symbol')
    return out[:first_sub] + props + out[first_sub:]


def pins_of(sym):
    """Pins of unit 1 (and common unit 0), body style 1: list of dicts."""
    name = sym[1]
    res = []
    for sub in sym:
        if not (isinstance(sub, list) and sub and sub[0] == 'symbol'):
            continue
        m = re.match(re.escape(name) + r'_(\d+)_(\d+)$', sub[1])
        if not m or m.group(1) not in ('0', '1') or m.group(2) not in ('0', '1'):
            continue
        for p in sub:
            if isinstance(p, list) and p and p[0] == 'pin':
                at = next(c for c in p if isinstance(c, list) and c[0] == 'at')
                nm = next(c for c in p if isinstance(c, list) and c[0] == 'name')
                no = next(c for c in p if isinstance(c, list) and c[0] == 'number')
                res.append({'type': p[1], 'x': float(at[1]), 'y': float(at[2]), 'a': int(float(at[3])) if len(at) > 3 else 0,
                            'name': str(nm[1]), 'number': str(no[1])})
    return res


# ------------------------------------------------------------------ parts list
R06, R12, R25 = 'Resistor_SMD:R_0603_1608Metric', 'Resistor_SMD:R_1206_3216Metric', 'Resistor_SMD:R_2512_6332Metric'
C06, C08, C12, C18, C22 = ('Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_0805_2012Metric', 'Capacitor_SMD:C_1206_3216Metric',
                           'Capacitor_SMD:C_1812_4532Metric', 'Capacitor_SMD:C_2220_5750Metric')
CP_THT = 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'
TP_FP = 'TestPoint:TestPoint_Keystone_5000-5004_Miniature'

BLOCKS = []


def block(title):
    BLOCKS.append({'title': title, 'parts': []})


def part(ref, lib_id, value, fp, nets, lcsc='', dnp=False, note=''):
    BLOCKS[-1]['parts'].append({'ref': ref, 'lib_id': lib_id, 'value': value, 'fp': fp, 'nets': nets,
                                'lcsc': lcsc, 'dnp': dnp, 'note': note})


def R(ref, val, fp, a, b, lcsc='', dnp=False, note=''):
    part(ref, 'Device:R', val, fp, {'1': a, '2': b}, lcsc, dnp, note)


def C(ref, val, fp, a, b, lcsc='', dnp=False, note=''):
    part(ref, 'Device:C', val, fp, {'1': a, '2': b}, lcsc, dnp, note)


def CP(ref, val, fp, plus, minus, lcsc='', note=''):
    part(ref, 'Device:C_Polarized', val, fp, {'1': plus, '2': minus}, lcsc, note=note)


def chain(prefix, val, fp, start, end, n, lcsc, ref0, tag):
    """n identical resistors in series from start to end; internal nets tag_1, tag_2..."""
    nodes = [start] + ['%s_%d' % (tag, i) for i in range(1, n)] + [end]
    for i in range(n):
        R('%s%d' % (prefix, ref0 + i), val, fp, nodes[i], nodes[i + 1], lcsc)


block('INPUT AND CONTROLLER')
part('J1', 'Connector_Generic:Conn_01x02', 'VIN_IN (placeholder)', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
     {'1': 'VIN', '2': 'GND'}, note='Rev 1 bench-supply input; connector to be chosen (P-23)')
part('#FLG01', 'power:PWR_FLAG', 'PWR_FLAG', '', {'1': 'VIN'})
part('#FLG02', 'power:PWR_FLAG', 'PWR_FLAG', '', {'1': 'GND'})
CP('C1', '330uF 25V', 'Capacitor_SMD:CP_Elec_8x10', 'VIN', 'GND', 'C74593', 'damping bulk')
for i in range(8):
    C('C%d' % (2 + i), '10uF 25V X7R', C12, 'VIN', 'GND', 'C70462')
part('U1', NAME + ':LM51551', 'LM51551DSSR', 'Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65',
     {'1': 'VIN', '2': 'VCC', '3': 'GATE_U1', '4': 'GND', '5': 'CS', '6': 'COMP', '7': 'GND', '8': 'GND',
      '9': 'SS', '10': 'RT', '11': None, '12': 'UVLO', '13': 'GND'}, 'C778612')
C('C10', '100nF 25V', C08, 'VIN', 'GND', note='BIAS decoupling')
C('C11', '4.7uF 25V', C08, 'VCC', 'GND')
R('R1', '86.6k 1%', R06, 'RT', 'GND', note='252 kHz')
C('C12', '680nF 16V X7R', C06, 'SS', 'GND', note='soft start, P-20')
R('R2', '49.9k 1%', R06, 'VIN', 'UVLO', note='UVLO on 7.5 V')
R('R3', '12.4k 1%', R06, 'UVLO', 'GND', note='UVLO off 7.0 V')
C('C13', '220pF', C06, 'UVLO', 'GND')
R('R4', '5.11k 1%', R06, 'VCC', 'COMP')
R('R5', '249k', R06, 'COMP', 'RCOMP_MID', dnp=True, note='footprint only')
C('C14', '4.7nF', C08, 'RCOMP_MID', 'GND', dnp=True, note='footprint only')
part('Q1', 'Transistor_BJT:MMBT3906', 'MMBT3906', 'Package_TO_SOT_SMD:SOT-23', {'E': 'COMP', 'B': 'SS', 'C': 'GND'}, 'C364311',
     note='primary-side soft start')

block('POWER STAGE')
for t in ('T1', 'T2'):
    sec = {'1': 'GND', '12': 'SEC_P'} if t == 'T1' else {'1': '-HV_RAW', '12': 'SEC_N'}
    nets = {'7': 'VIN', '8': 'VIN', '9': 'VIN', '10': 'VIN', '3': 'SW', '4': 'SW', '5': 'SW', '6': 'SW', '2': None, '11': None}
    nets.update(sec)
    part(t, NAME + ':DA2034-ALD', 'DA2034-ALD', 'power_supply:Coilcraft_DA2034', nets, 'C5354095',
         note='buy outside JLCPCB, hand-solder (P-24)')
part('Q2', 'Transistor_FET:CSD19502Q5B', 'CSD19531Q5A', 'Package_SON:VSONP-8-1EP_5x6_P1.27mm',
     {'D': 'SW', 'G': 'GATE_FET', 'S': 'SNS'}, 'C2760462', note='symbol is CSD19502Q5B (same pinout)')
R('R6', '3.3R', R06, 'GATE_U1', 'GATE_FET', note='start value, bench-tune')
R('R7', '6mR 1% 3W', R25, 'SNS', 'GND', 'C429335', note='Kelvin-sense to R8')
R('R8', '200R 1%', R06, 'SNS', 'CS', note='slope compensation')
C('C15', '2.2nF', C06, 'CS', 'GND', note='P-16; place at U1')
part('D1', 'Device:D_Schottky', 'SS510C', 'Diode_SMD:D_SMC', {'1': 'SNUB', '2': 'SW'}, 'C123944')
for i in range(3):
    R('R%d' % (9 + i), '300R 2W', R25, 'SNUB', 'VIN', 'C91264')
C('C16', '100nF 100V', C12, 'SNUB', 'VIN')

block('+HV OUTPUT')
part('D2', 'Device:D', 'ES1J', 'Diode_SMD:D_SMA', {'1': '+HV_RAW', '2': 'SEC_P'}, 'C86560')
R('R12', '220R', R12, 'SEC_P', 'SN1', note='start value, bench-tune')
C('C17', '22pF 630V', C12, 'SN1', '+HV_RAW')
for i in range(3):
    CP('C%d' % (18 + i), '10uF 200V', CP_THT, '+HV_RAW', 'GND', 'C106302')
C('C21', '1uF 250V X7R', C18, '+HV_RAW', 'GND', 'C381468')
part('D3', 'Device:D_Zener', 'SMBJ130A', 'Diode_SMD:D_SMB', {'1': '+HV_RAW', '2': 'GND'}, 'C224006', note='TVS, unidirectional')
part('L1', 'Device:L', '100uH', 'Inductor_SMD:L_Sunlord_SWPA8040S', {'1': '+HV_RAW', '2': 'HVP_F'}, 'C83468')
part('FB1', 'Device:FerriteBead', '600R@100MHz', 'Inductor_SMD:L_1206_3216Metric', {'1': 'HVP_F', '2': '+HV'}, 'C16902')
C('C22', '1uF 250V X7R', C18, '+HV', 'GND', 'C381468')
CP('C23', '10uF 200V', CP_THT, '+HV', 'HVP_D', 'C106302', note='damping')
R('R13', '10R', R12, 'HVP_D', 'GND')
part('J2', 'Connector_Generic:Conn_01x03', 'HV_OUT (placeholder)', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
     {'1': '+HV', '2': 'GND', '3': '-HV'}, note='connector to the analog boards to be agreed (P-22)')

block('-HV OUTPUT')
part('D4', 'Device:D', 'ES1J', 'Diode_SMD:D_SMA', {'1': 'GND', '2': 'SEC_N'}, 'C86560')
R('R14', '220R', R12, 'SEC_N', 'SN2', note='start value, bench-tune')
C('C24', '22pF 630V', C12, 'SN2', 'GND')
for i in range(3):
    CP('C%d' % (25 + i), '10uF 200V', CP_THT, 'GND', '-HV_RAW', 'C106302')
C('C28', '1uF 250V X7R', C18, 'GND', '-HV_RAW', 'C381468')
part('D5', 'Device:D_Zener', 'SMBJ130A', 'Diode_SMD:D_SMB', {'1': 'GND', '2': '-HV_RAW'}, 'C224006', note='TVS, unidirectional')
part('L2', 'Device:L', '100uH', 'Inductor_SMD:L_Sunlord_SWPA8040S', {'1': '-HV_RAW', '2': 'HVN_F'}, 'C83468')
part('FB2', 'Device:FerriteBead', '600R@100MHz', 'Inductor_SMD:L_1206_3216Metric', {'1': 'HVN_F', '2': '-HV'}, 'C16902')
C('C29', '1uF 250V X7R', C18, 'GND', '-HV', 'C381468')
R('R15', '10R', R12, 'GND', 'HVN_D')
CP('C30', '10uF 200V', CP_THT, 'HVN_D', '-HV', 'C106302', note='damping')

block('MAIN FEEDBACK (+HV_RAW, 102.5 V)')
chain('R', '33.2k 0.1%', R12, '+HV_RAW', 'FB_REF', 3, 'C2984513', 16, 'FB_T')
R('R19', '2.49k 0.1%', R06, 'FB_REF', 'GND', 'C861299')
part('U2', 'Reference_Voltage:TL431DBZ', 'TL431BIDBZR', 'Package_TO_SOT_SMD:SOT-23', {'REF': 'FB_REF', 'A': 'GND', 'K': 'FB_K1'}, 'C41283')
part('Q3', 'Transistor_BJT:MMBTA42', 'MMBTA42', 'Package_TO_SOT_SMD:SOT-23', {'E': 'FB_K1', 'B': 'FB_B', 'C': 'FB_KC'}, 'C8515')
chain('R', '110k 1%', R12, '+HV_RAW', 'FB_B', 3, 'C17904', 20, 'FB_RB')
part('D6', 'Device:D_Zener', 'BZT52C12', 'Diode_SMD:D_SOD-123', {'1': 'FB_B', '2': 'GND'}, 'C19077410')
chain('R', '14.7k 1%', R12, '+HV_RAW', 'FB_LA', 3, 'C488648', 23, 'FB_RL')
part('U3', 'Isolator:TCMT1108', 'TCMT1108', 'Package_SO:SOP-4_4.4x2.6mm_P1.27mm', {'1': 'FB_LA', '2': 'FB_KC', '3': 'GND', '4': 'COMP'}, 'C3014154')
R('R26', '2k', R06, 'FB_LA', 'FB_KC')
C('C31', '68nF 250V X7R', C12, 'FB_KC', 'FB_CM', 'C513585')
R('R27', '12.7k 1%', R06, 'FB_CM', 'FB_REF')
chain('R', '499k', R12, '+HV_RAW', 'NSS', 2, '', 28, 'NSS_R')
C('C32', '2.2uF 250V X7R', C22, 'NSS', 'GND', 'C153032', note='start-up network, required')
part('D7', 'Diode:BAS21', 'BAS21', 'Package_TO_SOT_SMD:SOT-23', {'A': 'FB_KC', 'K': 'NSS'}, 'C7502725')
part('D8', 'Diode:BAS21', 'BAS21', 'Package_TO_SOT_SMD:SOT-23', {'A': 'NSS', 'K': '+HV_RAW'}, 'C7502725', note='resets C32')


def trip(tag, hi, lo, r0, u_ref, q_ref, d_ref, u_opto, c_ref):
    chain('R', '33.2k 0.1%', R12, hi, tag + '_REF', 3, 'C2984513', r0, tag + '_T')
    R('R%d' % (r0 + 3), '2.32k 0.1%', R06, tag + '_REF', lo, 'C861296', note='109.8 V')
    C(c_ref, '4.7nF', C06, tag + '_REF', lo)
    part(u_ref, 'Reference_Voltage:TL431DBZ', 'TL431BIDBZR', 'Package_TO_SOT_SMD:SOT-23', {'REF': tag + '_REF', 'A': lo, 'K': tag + '_K1'}, 'C41283')
    part(q_ref, 'Transistor_BJT:MMBTA42', 'MMBTA42', 'Package_TO_SOT_SMD:SOT-23', {'E': tag + '_K1', 'B': tag + '_B', 'C': tag + '_KC'}, 'C8515')
    chain('R', '110k 1%', R12, hi, tag + '_B', 3, 'C17904', r0 + 4, tag + '_RB')
    part(d_ref, 'Device:D_Zener', 'BZT52C12', 'Diode_SMD:D_SOD-123', {'1': tag + '_B', '2': lo}, 'C19077410')
    chain('R', '7.32k 1%', R12, hi, tag + '_LA', 3, 'C247199', r0 + 7, tag + '_RL')
    part(u_opto, 'Isolator:TCMT1108', 'TCMT1108', 'Package_SO:SOP-4_4.4x2.6mm_P1.27mm', {'1': tag + '_LA', '2': tag + '_KC', '3': 'LATCH_G', '4': 'COMP'}, 'C3014154')
    R('R%d' % (r0 + 10), '2k', R06, tag + '_LA', tag + '_KC')


block('TRIP +HV (109.8 V)')
trip('TP', '+HV_RAW', 'GND', 30, 'U4', 'Q4', 'D9', 'U5', 'C33')
block('TRIP -HV (109.8 V)')
trip('TN', 'GND', '-HV_RAW', 41, 'U6', 'Q5', 'D10', 'U7', 'C34')

block('LATCH')
part('Q6', 'Transistor_BJT:MMBT3904', 'MMBT3904', 'Package_TO_SOT_SMD:SOT-23', {'E': 'GND', 'B': 'LATCH_G', 'C': 'LQ_B'}, 'C916374')
part('Q7', 'Transistor_BJT:MMBT3906', 'MMBT3906', 'Package_TO_SOT_SMD:SOT-23', {'E': 'UVLO', 'B': 'LQ_B', 'C': 'LATCH_G'}, 'C364311')
R('R52', '100k', R06, 'UVLO', 'LQ_B')
R('R53', '10k', R06, 'LATCH_G', 'GND')
C('C35', '10nF', C06, 'LATCH_G', 'GND')

block('TEST POINTS')
for i, n in enumerate(['+HV_RAW', '-HV_RAW', '+HV', '-HV', 'SW', 'SNS', 'COMP', 'UVLO', 'LATCH_G', 'VCC', 'SS', 'GND']):
    part('TP%d' % (i + 1), 'Connector:TestPoint', n, TP_FP, {'1': n})


# ------------------------------------------------------------------ build
def lib_sym(lib_id):
    lib, name = lib_id.split(':')
    s = flatten(lib, name)
    return s


def main():
    # write custom library and footprint
    os.makedirs(os.path.join(PRJ, 'lib', NAME + '.pretty'), exist_ok=True)
    with open(os.path.join(PRJ, 'lib', NAME + '.kicad_sym'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(ser(S('(kicad_symbol_lib (version 20251024) (generator "gen_schematic.py") (generator_version "10.0") '
                      + LM51551 + DA2034 + ')')) + '\n')
    with open(os.path.join(PRJ, 'lib', NAME + '.pretty', 'Coilcraft_DA2034.kicad_mod'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(DA2034_FP.replace('{pads}', da2034_pads()))
    with open(os.path.join(PRJ, 'sym-lib-table'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "%s") (type "KiCad") (uri "${KIPRJMOD}/lib/%s.kicad_sym") (options "") (descr "Project symbols"))\n)\n' % (NAME, NAME))
    with open(os.path.join(PRJ, 'fp-lib-table'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "%s") (type "KiCad") (uri "${KIPRJMOD}/lib/%s.pretty") (options "") (descr "Project footprints"))\n)\n' % (NAME, NAME))
    pro = os.path.join(PRJ, NAME + '.kicad_pro')
    if not os.path.exists(pro):
        with open(pro, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {'filename': NAME + '.kicad_pro', 'version': 3}}, f, indent=2)

    lib_syms = {}
    items = []
    intended = {}
    x0, y0, page_w = 25.4, 38.1, 1150.0
    y = y0
    for blk in BLOCKS:
        items.append(S('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size 2.54 2.54) (thickness 0.508) (bold yes)) (justify left bottom)) (uuid "%s"))'
                       % ('"' + esc(blk['title']) + '"', x0, y, uid())))
        y += 7.62
        x = x0
        row_h = 0.0
        for p in blk['parts']:
            if p['lib_id'] not in lib_syms:
                lib_syms[p['lib_id']] = lib_sym(p['lib_id'])
            sym = lib_syms[p['lib_id']]
            pins = pins_of(sym)
            xs = [q['x'] for q in pins] + [0]
            ys = [q['y'] for q in pins] + [0]
            minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
            lw = 15.24 if any(q['a'] in (0, 180) for q in pins) else 5.08
            w = (maxx - minx) + 2 * lw + 7.62
            h = (maxy - miny) + (15.24 if any(q['a'] in (90, 270) for q in pins) else 7.62) + 7.62
            w = max(w, 22.86)
            if x + w > x0 + page_w:
                x = x0
                y += row_h
                row_h = 0.0
            sx = round((x + lw - minx + 3.81) / 2.54) * 2.54
            sy = round((y + (maxy) + (7.62 if any(q['a'] in (90, 270) for q in pins) else 2.54) + 2.54) / 2.54) * 2.54
            items.append(place(p, sx, sy, sym, pins, intended))
            for it in labels_for(p, sx, sy, pins):
                items.append(it)
            x += w
            row_h = max(row_h, h)
        y += row_h + 7.62

    paper_h = y + 25
    sch = [ 'kicad_sch', ['version', '20250610'], ['generator', Q('eeschema')], ['generator_version', Q('9.99')],
            ['uuid', Q(ROOT_UUID)], ['paper', Q('User'), '%.2f' % (x0 + page_w + 25.4), '%.2f' % max(paper_h, 420.0)],
            S('(title_block (title "+/-102 V isolated flyback supply") (date "2026-11-16") (rev "1.0") '
              '(comment 1 "Generated by pcb/tools/gen_schematic.py from FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md") '
              '(comment 2 "Every pin carries a net label; tidy into wires during review"))'),
            ['lib_symbols'] + [embed(lib_id, s) for lib_id, s in sorted(lib_syms.items())] ]
    sch += items
    sch += [S('(sheet_instances (path "/" (page "1")))'), S('(embedded_fonts no)')]
    with open(os.path.join(PRJ, NAME + '.kicad_sch'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(ser(sch) + '\n')
    with open(os.path.join(TOOLS, 'intended_netlist.json'), 'w', encoding='utf-8') as f:
        json.dump(intended, f, indent=1, sort_keys=True)
    n_parts = sum(len(b['parts']) for b in BLOCKS)
    print('wrote %s.kicad_sch: %d parts (%d real), %d nets' % (NAME, n_parts,
          sum(1 for b in BLOCKS for p in b['parts'] if not p['ref'].startswith('#')),
          len(set(n for r in intended.values() for n in r.values() if n))))


def embed(lib_id, s):
    e = copy.deepcopy(s)
    e[1] = Q(lib_id)
    return e


def prop(name, value, x, y, hide=False, justify=None):
    eff = '(effects (font (size 1.27 1.27))%s%s)' % (' (justify %s)' % justify if justify else '', ' (hide yes)' if hide else '')
    return S('(property "%s" "%s" (at %.2f %.2f 0) %s)' % (name, esc(value), x, y, eff))


def place(p, sx, sy, sym, pins, intended):
    is_flag = p['ref'].startswith('#')
    ys = [q['y'] for q in pins] + [0]
    top, bot = sy - max(ys) - 2.54, sy - min(ys) + 3.81
    vertical = any(q['a'] in (90, 270) for q in pins) and not any(q['a'] in (0, 180) for q in pins)
    rx = sx + (2.54 if vertical else 0)
    node = ['symbol', ['lib_id', Q(p['lib_id'])], ['at', '%.2f' % sx, '%.2f' % sy, '0'], ['unit', '1'],
            ['exclude_from_sim', 'no'], ['in_bom', 'no' if is_flag else 'yes'], ['on_board', 'no' if is_flag else 'yes'],
            ['dnp', 'yes' if p['dnp'] else 'no'], ['uuid', Q(uid())],
            prop('Reference', p['ref'], rx, top if not vertical else sy - 1.27, hide=is_flag, justify='left' if vertical else None),
            prop('Value', p['value'], rx, bot if not vertical else sy + 1.27, justify='left' if vertical else None),
            prop('Footprint', p['fp'], sx, sy, hide=True),
            prop('Datasheet', '~', sx, sy, hide=True)]
    if p['lcsc']:
        node.append(prop('LCSC', p['lcsc'], sx, sy, hide=True))
    if p['note']:
        node.append(prop('Note', p['note'], sx, sy, hide=True))
    seen = set()
    for q in pins:
        if q['number'] in seen:
            continue
        seen.add(q['number'])
        node.append(['pin', Q(q['number']), ['uuid', Q(uid())]])
    node.append(S('(instances (project "%s" (path "/%s" (reference "%s") (unit 1))))' % (NAME, ROOT_UUID, p['ref'])))
    # intended connectivity per pin number
    if not is_flag:
        intended[p['ref']] = {q['number']: net_for(p, q) for q in pins if q['type'] != 'no_connect'}
    return node


def net_for(p, q):
    nets = p['nets']
    if q['number'] in nets:
        return nets[q['number']]
    if q['name'] in nets:
        return nets[q['name']]
    raise KeyError('%s pin %s (%s) has no net' % (p['ref'], q['number'], q['name']))


def labels_for(p, sx, sy, pins):
    out = []
    done = {}
    for q in pins:
        if q['type'] == 'no_connect':
            continue
        px, py = round(sx + q['x'], 2), round(sy - q['y'], 2)
        net = net_for(p, q)
        key = (px, py)
        if key in done:
            if done[key] != net:
                raise ValueError('%s: stacked pins at %s want %s and %s' % (p['ref'], key, done[key], net))
            continue
        done[key] = net
        if net is None:
            out.append(S('(no_connect (at %.2f %.2f) (uuid "%s"))' % (px, py, uid())))
            continue
        outward = (q['a'] + 180) % 360
        just = 'left' if outward in (0, 90) else 'right'
        out.append(S('(label "%s" (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s bottom)) (uuid "%s"))'
                     % (esc(net), px, py, outward, just, uid())))
    return out


if __name__ == '__main__':
    main()
