"""Start-up check for the soft-start runs (P-20).

Reads an LTspice transient .raw file and reports:
  - peak switch and transformer currents after the first 0.3 ms
  - rail extremes, and when +HV first reaches 100 V
  - whether the trip latch fired
  - the longest stretch of switching cycles spent at the current limit,
    which is what triggers the LM51551's hiccup protection (64 cycles, then 32,768 cycles off)

Usage:  python -I softstart_check.py P9_run_S470.raw [P9_run_S1u.raw ...]
"""
import sys

import numpy as np

PERIOD = 4e-6          # switching period, 250 kHz
LIMIT_V = 0.100        # current-limit threshold at the CS pin (100 mV)
HICCUP_CYCLES = 64     # LM51551: cycles at the limit before hiccup


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
    dt = np.dtype([('t', '<f8'), ('v', '<f4', (nv - 1,))])
    n = (len(data) - off) // dt.itemsize
    rec = np.frombuffer(data, dtype=dt, count=n, offset=off)
    t = np.abs(rec['t'])
    sig = {names[k]: rec['v'][:, k - 1] for k in range(1, nv)}
    return t, sig


def cycle_peaks(t, x, t0, t1):
    """Peak of x in each switching cycle between t0 and t1."""
    edges = np.arange(t0, t1, PERIOD)
    idx = np.searchsorted(t, edges)
    return edges[:-1], np.maximum.reduceat(x, idx)[:-1] if len(idx) > 1 else np.array([])


COUNT_V = 0.098        # a cycle counts as 'at the limit' at 98 mV or more (filter rounds the peak)
RESET_CYCLES = 8       # normal cycles in a row that clear the count [ASSUME: the datasheet figure shows
                       # 60 limit cycles + 7 normal + 4 limit reaching hiccup, so 7 do not reset it]


def longest_limit_run(peaks, limit=COUNT_V, reset=RESET_CYCLES):
    """Return (longest_count, start_index) for the longest stretch of cycles counted as 'at the current limit'.

    Tolerant rule: limit cycles accumulate, and a run of fewer than `reset` normal cycles does not
    clear the count; only limit cycles are counted, so 60 + (7 normal) + 4 gives 64.
    peaks: per-cycle peak of the CS-pin voltage, one value per switching cycle, in time order.
    """
    best, best_start = 0, 0
    count, start, gap = 0, 0, 0
    for i, p in enumerate(peaks):
        if p >= limit:
            if count == 0:
                start = i
            count += 1
            gap = 0
            if count > best:
                best, best_start = count, start
        elif count:
            gap += 1
            if gap >= reset:
                count, gap = 0, 0
    return best, best_start


def report(path):
    t, s = load(path)
    tend = t[-1]
    after = t > 0.3e-3
    print('=== %s  (simulated to %.2f ms)' % (path, tend * 1e3))
    print('switch peak %.2f A; transformer peaks %.2f / %.2f A'
          % (s['id(m1)'][after].max(), s['i(l1p)'][after].max(), s['i(l2p)'][after].max()))
    hvp, hvn = s['v(hvp)'], s['v(hvn)']
    print('+HV max %.2f V; -HV min %.2f V' % (hvp.max(), hvn.min()))
    k = np.argmax(hvp >= 100.0)
    print('+HV reaches 100 V at: %s' % ('%.2f ms' % (t[k] * 1e3) if hvp[k] >= 100.0 else 'not reached'))
    print('latch gate max %.3f V (fires near 0.6 V); UVLO pin min %.3f V after 1 ms'
          % (s['v(g)'].max(), s['v(uvlo)'][t > 1e-3].min()))
    starts, pk = cycle_peaks(t, s['v(cs_pin)'], 0.3e-3, tend)
    n, i0 = longest_limit_run(pk)
    where = ('starting at %.2f ms' % (starts[i0] * 1e3)) if n else ''
    verdict = 'HICCUP would trigger' if n >= HICCUP_CYCLES else 'no hiccup'
    print('longest run at the current limit: %d cycles %s -> %s' % (n, where, verdict))
    print('t(ms)    +HV      -HV     SS    COMP  switch pk')
    for ms in np.arange(5, tend * 1e3, 5):
        a, b = np.searchsorted(t, [ms * 1e-3, ms * 1e-3 + 8e-6])
        print('%5.0f  %7.2f %8.2f %6.3f %6.2f %8.2f'
              % (ms, hvp[a:b].mean(), hvn[a:b].mean(), s['v(ss)'][a:b].mean(),
                 s['v(comp_pin)'][a:b].mean(), s['id(m1)'][a:b].max()))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        report(p)
