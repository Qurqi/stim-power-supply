# Per-sheet simulation benches (ngspice 42), 2026-11-26

One bench per schematic sheet, using the current schematic values and the device models of `../P9_final.net`
(ported to ngspice in `models.lib`). Results are in the Simulation Test and Validation Report.

Run any bench with `ngspice -b <file>.cir`; each prints its `.meas` results and writes a `.dat` file.

| File | Sheet | What it checks |
| --- | --- | --- |
| b1_uvlo.cir | INPUT AND CONTROLLER | UVLO divider: start / stop battery voltage |
| b2_0.12.cir, b2_0.03.cir | INPUT AND CONTROLLER | Battery connection surge through F2, peak and I^2t |
| b3_ss.cir | INPUT AND CONTROLLER | Soft-start ramp of COMP (C12 680 nF, 10 uA) |
| b4_conv.cir, b4l_conv.cir | POWER STAGE + outputs | Closed-loop converter, 9 V, 171 mA per rail, 6 ms / 16 ms |
| b5_filt.cir | +HV / -HV OUTPUT | LC output filter attenuation (AC) |
| b6_fb.cir | MAIN FEEDBACK | COMP versus rail voltage (DC sweep) |
| b7_trip.cir, b7n_trip.cir | TRIP +HV / TRIP -HV | Rail ramp through the trip level; latch fires |
| b7b_hold.cir | LATCH | Latch holds after the rail falls |
| b8_conn.cir | LATCH | No false trip on battery connection |
| b9_startup.cir, b9i_startup.cir | Full converter | Start-up from 0 V at 9 V, full load: rise time, overshoot; b9i saves transformer and switch currents |
| b10_600 … b10_10000.cir | Full converter | Load sweep, 600 ohm to 10 kohm per rail, 20 ms (preset near the operating point) |
| b11_5000_lo.cir, b11_10000_lo.cir | Full converter | 60 ms runs at 5 k / 10 k so the -HV rail settles at light load |
| f1_rect_p.cir | Full converter | Fault: +HV rectifier opens at 2 ms |
| f2_rect_n.cir | Full converter | Fault: -HV rectifier opens at 2 ms |
| f3_opto.cir | Full converter | Fault: main feedback optocoupler opens at 2 ms |
| f4_short.cir | Full converter | Fault: +HV output shorted at 2 ms |

Note: the full-converter benches take 1-20 minutes each in ngspice 42. Runs started with -HV preset above the
model's trip level (107.2 V) trip immediately; start light-load runs at or below 100 V.

## Rev 1: 4 Howland-pump channels (balanced loads: current sourced = current sunk)
Each channel idles at about 5.2 mA per rail; output current appears equally on both rails (0-20 mA for 4 channels).

| File | Load per rail |
| --- | --- |
| c_noload.cir, d_noload_long.cir | pumps disconnected (80 ms / 200 ms) |
| c_idle.cir | 20.8 mA (4 channels idle) |
| e_9.cir | 29.8 mA (1 sources 9 mA, 3 sink 3 mA) |
| c_op.cir | 30.8 mA (operating point, 2 x 5 mA) |
| e_max.cir | 40.8 mA (maximum, 2 x 10 mA) |
| e_step.cir | step 20.8 -> 40.8 -> 20.8 mA at 20 / 40 ms |
| g_bleed_20000.cir, g_bleed_50000.cir | pumps disconnected, 20 k / 50 k bleeder per rail, 200 ms |

## Start-up transformer current vs inductance mismatch (h_match_*), 2026-11-26
Window 55.4-57 ms of the B9 start-up. Magnetizing current = i(Lp) + 10 i(Ls), which is what saturates the core (10 A rating).

| T1 / T2 primary | Winding peak T1 / T2 | Magnetizing peak | Switch peak |
|---|---|---|---|
| 11 / 9 uH (+/-10 %) | 17.5 (-38) / 12.4 A | 8.2 / 8.4 A | 25.6 A |
| 10.5 / 9.5 uH (+/-5 %) | 17.1 (-41) / 10.3 A | 7.6 / 7.3 A | 23.6 A |
| 10.2 / 9.8 uH (+/-2 %) | 9.2 / 9.1 A | 6.5 / 6.5 A | 17.5 A |
| 10 / 10 uH | 9.1 / 9.1 A | 6.5 / 6.5 A | 17.7 A |

The large winding peaks are ~3 MHz leakage ringing between the paralleled primaries, excited by the mismatch; the model has
almost no HF loss, so their size is overstated. Pair transformers within 2 % primary inductance.
