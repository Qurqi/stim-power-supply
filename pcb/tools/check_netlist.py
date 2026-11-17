"""Compare the netlist KiCad exports from the schematic with the intended connectivity.

The generator writes tools/intended_netlist.json (part -> pin -> net, from the parts list).
This script asks kicad-cli for the real netlist and reports every pin whose net differs,
plus any net KiCad joined that the parts list keeps apart. Run from the pcb folder:

    python tools/check_netlist.py
"""
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(TOOLS)
CLI = r'C:\Users\Johnd\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe'


def main():
    out = os.path.join(TOOLS, 'exported.net')
    subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', out,
                    os.path.join(PRJ, 'power_supply.kicad_sch')], check=True, capture_output=True)
    sys.path.insert(0, TOOLS)
    from gen_schematic import parse   # same s-expression reader the generator uses
    tree = parse(open(out, encoding='utf-8').read())[0]
    nets = next(c for c in tree if isinstance(c, list) and c[0] == 'nets')
    actual = {}   # (ref, pin) -> net name
    for net in nets[1:]:
        name = str(next(c for c in net if isinstance(c, list) and c[0] == 'name')[1]).lstrip('/')
        for node in (c for c in net if isinstance(c, list) and c[0] == 'node'):
            ref = str(next(c for c in node if isinstance(c, list) and c[0] == 'ref')[1])
            pin = str(next(c for c in node if isinstance(c, list) and c[0] == 'pin')[1])
            actual[(ref, pin)] = name
    intended = json.load(open(os.path.join(TOOLS, 'intended_netlist.json')))
    bad = 0
    # 1. every intended pin is on a net whose members match
    want_groups = {}
    for ref, pins in intended.items():
        for pin, net in pins.items():
            if net is None:
                got = actual.get((ref, pin), '')
                if got and not got.startswith('unconnected'):
                    print('NC pin connected: %s.%s on %s' % (ref, pin, got)); bad += 1
                continue
            want_groups.setdefault(net, set()).add((ref, pin))
            got = actual.get((ref, pin))
            if got != net:
                print('MISMATCH %s.%s: want %s, got %s' % (ref, pin, net, got)); bad += 1
    # 2. KiCad nets must not merge two intended nets
    got_groups = {}
    for key, net in actual.items():
        got_groups.setdefault(net, set()).add(key)
    for net, members in want_groups.items():
        if got_groups.get(net, set()) - {k for k in got_groups.get(net, set()) if k[0].startswith('#')} != members:
            extra = got_groups.get(net, set()) - members
            missing = members - got_groups.get(net, set())
            extra = {e for e in extra if not e[0].startswith('#')}
            if extra or missing:
                print('NET %s: extra %s missing %s' % (net, sorted(extra), sorted(missing))); bad += 1
    print('checked %d parts, %d pins, %d nets: %s' % (len(intended), sum(len(p) for p in intended.values()),
                                                     len(want_groups), 'OK' if not bad else '%d problems' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
