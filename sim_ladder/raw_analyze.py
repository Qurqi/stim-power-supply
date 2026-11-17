"""Read an LTspice transient .raw file (time float64, values float32) and print summaries.
Usage: python raw_analyze.py <file.raw> startup | ripple
"""
import struct
import sys


def load(path):
    data = open(path, 'rb').read()
    head = data[:65536].decode('utf-16-le', errors='ignore')
    i = head.index('Binary:')
    off = (head.index('\n', i) + 1) * 2
    hdr = head[:i]
    nv = int(hdr.split('No. Variables:')[1].split()[0])
    names = []
    for line in hdr.split('Variables:')[-1].splitlines():
        parts = line.strip().split('\t')
        if len(parts) >= 3 and parts[0].isdigit():
            names.append(parts[1].lower())
    rec = 8 + 4 * (nv - 1)
    cnt = (len(data) - off) // rec
    return data, off, rec, cnt, names


class Raw:
    def __init__(self, path):
        self.data, self.off, self.rec, self.cnt, self.names = load(path)

    def t(self, k):
        return abs(struct.unpack_from('<d', self.data, self.off + k * self.rec)[0])

    def v(self, k, name):
        j = self.names.index(name.lower())
        return struct.unpack_from('<f', self.data, self.off + k * self.rec + 8 + 4 * (j - 1))[0]

    def index_at(self, t):
        lo, hi = 0, self.cnt - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.t(mid) < t:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def stats(self, name, t0, t1):
        a, b = self.index_at(t0), self.index_at(t1)
        j = self.names.index(name.lower())
        mn, mx, s, tw = 1e30, -1e30, 0.0, 0.0
        base = self.off + 8 + 4 * (j - 1)
        prev_t = self.t(a)
        for k in range(a, b):
            val = struct.unpack_from('<f', self.data, base + k * self.rec)[0]
            nt = self.t(k + 1)
            dt = nt - prev_t
            prev_t = nt
            mn = min(mn, val)
            mx = max(mx, val)
            s += val * dt
            tw += dt
        return mn, mx, (s / tw if tw > 0 else 0.0)


def startup(r):
    print('t(ms)    HVP     HVN      IN    UVLOmin  COMP    KCM   Id(M1)max')
    tend = r.t(r.cnt - 1)
    for t in [0.3, 0.6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13.9]:
        t0 = t * 1e-3
        if t0 + 8e-6 > tend:
            break
        row = [r.stats(n, t0, t0 + 8e-6) for n in ('V(hvp)', 'V(hvn)', 'V(in)', 'V(uvlo)', 'V(comp_pin)', 'V(kcm)', 'Id(M1)')]
        print('%5.1f  %7.2f %7.2f %7.2f %7.3f %6.2f %6.1f %7.1f' % (t, row[0][2], row[1][2], row[2][2], row[3][0], row[4][2], row[5][2], row[6][1]))
    mn = r.stats('V(uvlo)', 1e-3, tend - 1e-6)
    print('UVLO pin min %.4f V, max %.4f V after 1 ms (falling threshold 1.45 V)' % (mn[0], mn[1]))
    mn = r.stats('V(in)', 1e-3, tend - 1e-6)
    print('V(IN) min %.3f V after 1 ms' % mn[0])


def ripple(r, t_start, t_stop):
    period = 4e-6
    n = int((t_stop - t_start) / period)
    for name in ('V(hvp)', 'V(hvn)', 'V(outp)', 'V(outn)'):
        pps, means = [], []
        for c in range(n):
            a = t_start + c * period
            mn, mx, mean = r.stats(name, a, a + period)
            pps.append(mx - mn)
            means.append(mean)
        whole = r.stats(name, t_start, t_stop)
        print('%-8s switching ripple per cycle: mean %.1f mV, max %.1f mV | cycle-average wander %.1f mV | overall p-p %.1f mV'
              % (name, 1e3 * sum(pps) / len(pps), 1e3 * max(pps), 1e3 * (max(means) - min(means)), 1e3 * (whole[1] - whole[0])))
    # on-times from the switch node
    a, b = r.index_at(t_stop - 14 * period), r.index_at(t_stop)
    j = r.names.index('v(drain)')
    ons, state, t_on = [], None, None
    for k in range(a, b):
        low = r.v(k, 'V(drain)') < 3.0
        if state is None:
            state = low
            continue
        if low and not state:
            t_on = r.t(k)
        if (not low) and state and t_on is not None:
            ons.append((r.t(k) - t_on) * 1e6)
        state = low
    print('last on-times (us): ' + ' '.join('%.2f' % x for x in ons[-12:]))
    for name in ('I(L1p)', 'I(L2p)', 'Id(M1)'):
        mn, mx, mean = r.stats(name, t_stop - 25 * period, t_stop)
        print('%-8s min %.2f  max %.2f  mean %.2f A' % (name, mn, mx, mean))
    mn, mx, mean = r.stats('V(in)', t_stop - 25 * period, t_stop)
    print('V(IN) mean %.3f V' % mean)


if __name__ == '__main__':
    raw = Raw(sys.argv[1])
    mode = sys.argv[2]
    if mode == 'startup':
        startup(raw)
    else:
        t1 = float(sys.argv[3]) if len(sys.argv) > 3 else raw.t(raw.cnt - 1) - 2e-6
        ripple(raw, t1 - 0.2e-3, t1)
