"""Compare component values in the schematic with the final LTspice netlist.

The schematic values come from KiCad's own BOM export (tools/bom_actual.csv, written by
`kicad-cli sch export bom`). The simulated values are read from ../sim_ladder/P9_final.net.
MAP below says which schematic parts realise which simulation element, and how they combine:
'one' (single part), 'series' (resistors in series), 'parallel' (resistors in parallel) or
'sum' (capacitors in parallel). Where the simulation models a capacitor at its DC-bias-derated
value, 'derate' gives the factor used in the model so the rated part can be compared.

Run from the pcb folder after exporting the BOM:
    python tools/check_values.py
"""
import csv
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(TOOLS, '..', '..', 'sim_ladder', 'P9_final.net')
BOM = os.path.join(TOOLS, 'bom_actual.csv')

# sim element (as it appears in the netlist, subcircuit elements as SUBCKT.NAME) -> (schematic refs, rule, derate)
MAP = {
    'Cin1': (['C1'], 'one', 1), 'Cinx': (['C%d' % i for i in range(2, 10)], 'sum', 0.5),
    'Rent': (['R2'], 'one', 1), 'Renb': (['R3'], 'one', 1), 'Cbyp': (['C13'], 'one', 1),
    'Css': (['C12'], 'one', 1), 'Rpullup': (['R4'], 'one', 1),
    'Rgate': (['R6'], 'one', 1), 'Rsns': (['R7'], 'one', 1), 'Rcs': (['R8'], 'one', 1), 'Ccs': (['C15'], 'one', 1),
    'Rsnub': (['R9', 'R10', 'R11'], 'parallel', 1), 'Csnub': (['C16'], 'one', 1),
    'Rsn1': (['R12'], 'one', 1), 'Csn1': (['C17'], 'one', 1), 'Rsn2': (['R14'], 'one', 1), 'Csn2': (['C24'], 'one', 1),
    'Coutp': (['C18', 'C19', 'C20'], 'sum', 1), 'Coutpx': (['C21'], 'one', 0.45),
    'Coutn': (['C25', 'C26', 'C27'], 'sum', 1), 'Coutnx': (['C28'], 'one', 0.45),
    'Lfp': (['L1'], 'one', 1), 'Lfn': (['L2'], 'one', 1),
    'Cfp': (['C22'], 'one', 0.45), 'Cfn': (['C29'], 'one', 0.45),
    'Cdp': (['C23'], 'one', 1), 'Rdp': (['R13'], 'one', 1), 'Cdn': (['C30'], 'one', 1), 'Rdn': (['R15'], 'one', 1),
    'R21': (['R28', 'R29'], 'series', 1), 'C21': (['C32'], 'one', 0.59),
    'Rpb': (['R52'], 'one', 1), 'Rg': (['R53'], 'one', 1), 'Cg': (['C35'], 'one', 1),
    'FBB.Rt1': (['R16', 'R17', 'R18'], 'series', 1), 'FBB.Rb1': (['R19'], 'one', 1),
    'FBB.Rbb': (['R20', 'R21', 'R22'], 'series', 1), 'FBB.Rled': (['R23', 'R24', 'R25'], 'series', 1),
    'FBB.Rsh': (['R26'], 'one', 1), 'FBB.Cc': (['C31'], 'one', 1), 'FBB.Rc': (['R27'], 'one', 1),
    'TRB.Rt1': (['R30', 'R31', 'R32'], 'series', 1), 'TRB.Rb1': (['R33'], 'one', 1), 'TRB.Cf': (['C33'], 'one', 1),
    'TRB.Rbb': (['R34', 'R35', 'R36'], 'series', 1), 'TRB.Rled': (['R37', 'R38', 'R39'], 'series', 1),
    'TRB.Rsh': (['R40'], 'one', 1),
}
SI = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'meg': 1e6, 'g': 1e9}


def num(s):
    """'2.2n', '6m', '33.2k', '10uF', '6mR', '3.3R', '600R' -> float."""
    m = re.match(r'\s*([-\d.]+)\s*(meg|[fpnuµmkg])?', s, re.I)
    if not m:
        raise ValueError(s)
    v = float(m.group(1))
    return v * SI[m.group(2).lower()] if m.group(2) else v


def sim_values():
    vals, sub = {}, None
    for line in open(NET, encoding='utf-8'):
        t = line.split()
        if not t or t[0].startswith('*'):
            continue
        if t[0].lower() == '.subckt':
            sub = t[1]
            continue
        if t[0].lower() == '.ends':
            sub = None
            continue
        if t[0][0].upper() in 'RCL' and len(t) >= 4:
            key = (sub + '.' if sub else '') + t[0]
            try:
                vals[key] = num(t[3])
            except ValueError:
                pass
    return vals


def main():
    bom = {r['Ref']: r for r in csv.DictReader(open(BOM, encoding='utf-8'))}
    sim = sim_values()
    bad = 0
    print('%-10s %-22s %-12s %-12s %s' % ('sim', 'schematic', 'simulated', 'schematic', 'result'))
    for key, (refs, rule, derate) in MAP.items():
        if key not in sim:
            print('%-10s not found in P9_final.net' % key)
            bad += 1
            continue
        parts = [num(bom[r]['Value']) for r in refs]
        if rule == 'series':
            v = sum(parts)
        elif rule == 'parallel':
            v = 1 / sum(1 / p for p in parts)
        elif rule == 'sum':
            v = sum(parts)
        else:
            v = parts[0]
        v_model = v * derate
        ok = abs(v_model - sim[key]) <= 0.02 * abs(sim[key])
        bad += 0 if ok else 1
        print('%-10s %-22s %-12.4g %-12.4g %s%s' % (key, '+'.join(refs) if len(refs) < 4 else refs[0] + '..' + refs[-1],
                                                 sim[key], v_model, 'OK' if ok else 'MISMATCH',
                                                 '' if derate == 1 else '  (rated %.3g, model derates x%.2f)' % (v, derate)))
    print('%d elements compared: %s' % (len(MAP), 'all match' if not bad else '%d mismatches' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
