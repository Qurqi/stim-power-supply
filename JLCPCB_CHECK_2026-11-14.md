# JLCPCB library check — option C bill of materials

Status 2026-11-14. Source: jlcsearch.tscircuit.com, a third-party mirror of JLCPCB's in-stock assembly library, queried by part number. Stock figures are as of that mirror's last sync. Confirm each part on jlcpcb.com/parts before ordering. The mirror's basic / extended flags looked unreliable and are not reported here.

## Found
| Part | Use | LCSC number | Stock | Note |
|---|---|---|---|---|
| LM51551DSSR | controller | C778612 | 1,517 | — |
| TL431BIDBZR | reference, 3 per board | C41283 | 135,261 | 0.5 % grade |
| MMBTA42 | shielding transistor, 3 per board | C8515 | 65,430 | 300 V |
| BZT52C12 | 12 V Zener, 3 per board | C19077410 | 339,093 | — |
| BAS21 | start-up network diode | C7502725 | 154,583 | 200 V in this listing, not 250 V |
| ES1J (ES1J-LTP, SMA) | output diode, 2 per board | C86560 | 13,843 | 600 V, 1 A, 35 ns |
| MMBT3904 / MMBT3906 | latch | C916374 / C364311 | 892,440 / 170,295 | — |
| 33.2 kΩ 0.1 % 1206 (ARG06BTC3322) | dividers, 9 per board | C2984513 | 1,692 | 200 V rated |
| SMBJ130A | transient suppressor, 2 per board | C224006 | 124 | low stock; 130 V standoff instead of 120 V |

## Not found, with the nearest library part
| Part | Use | Nearest in library | Consequence |
|---|---|---|---|
| **Coilcraft DA2034-AL** | transformer, 2 per board | DA2032-ALD (C7938441, 58 in stock): the 3 A member of the same family | DA2032 is too small (8.9 A reaches one transformer at the current limit [H]). DA2034 must be bought from Coilcraft or a distributor and hand-soldered or consigned |
| CSD19502Q5B | switch | CSD19531Q5A (C2760462, 12,420): 100 V, 5.3 mΩ at 10 V. CSD18563Q5A (C77239): 60 V, 5.7 mΩ, only 46 in stock | CSD19531Q5A fits on voltage and current; its on-resistance at the controller's gate-drive voltage (about 6.8 V) must be read from the datasheet |
| TCMT1107 | optocoupler, 3 per board | same family: TCMT1103 (C553971, 2,084), TCMT1106 (C145341, 2,812), TCMT1108 (C3014154, 2,239), TCMT1109 (C118299, 3,622). Also TLP291 in several grades (for example C248929, listed as 100–200 %, 11,876) | a different transfer-ratio grade changes the loop gain and the LED resistor limit; the calculator must be re-run with the chosen grade |
| SMBJ120A | transient suppressor | SMBJ130A (above) | acceptable: it is a backstop for spikes only |
| 16SVPF82M | input capacitor | not searched further | the input capacitors were to be re-chosen anyway (4.6 A RMS ripple, 20–25 V) |

## Second pass: passives, checked on jlcpcb.com itself (2026-11-14, later)
Searched on JLCPCB's own parts pages (in-stock view). Stock counts were captured only for the first group; for the rest the part's presence in the in-stock listing is what was confirmed. Ratings marked "not read" need opening the part page.

| Item | Use | JLCPCB part | Stock | Note |
|---|---|---|---|---|
| 1 µF, 250 V, X7R | output and filter ceramics | C381468 (FS43X105K251EGG), **1812** | 92,947 | no 1 µF 250 V part showed in 1210; use the 1812 footprint |
| 68 nF, 250 V, X7R, 1206 | main compensation | C513585 (CC1206KKX7RYBB683) | 8,870 | — |
| 10 µF, 200 V electrolytic | filter damping; output bulk option | C112474 (EGW2DM100F12OT), **through-hole** 8 × 12 mm | 57,166 | ripple rating not read |
| 33 µF, 200 V electrolytic | output bulk | C159830 (Rubycon 200BXC33MEFC10X20), **through-hole** 10 × 20 mm, 650 mA at 100 kHz; C371317 | 352; 485 | through-hole only, low stock |
| 2.2 µF, 250 V, X7R, 2220 | optional start-up network | C153032 (FS55X225K251EGG) | 15,587 | — |
| 6 mΩ, 2512 | current sense | C76239 (MRF6432(2512)LR006FTS); C323799; C429335 | not captured | power rating not read |
| 100 µH shielded, 8040 size | LC filter | C83468 (Sunlord SWPA8040S101MT); C780190 (Bourns SRN8040-101M); C223045 (Taiyo Yuden NRS8040T101MJGK) | not captured | current rating and resistance not read |
| Ferrite bead, 600 Ω, 1206 | LC filter | C16902 (Murata BLM31PG601SN1L) | not captured | current rating not read |
| 2.49 kΩ, 0.1 % | main divider bottom | C861299 (Yageo RT0603BRD072K49L, 0603); C351475 (1206) | not captured | — |
| 2.32 kΩ, 0.1 % | trip divider bottom | C861296 (Yageo RT0603BRD072K32L, 0603); C870622 (1206) | not captured | — |
| 7.32 kΩ, 1 %, 1206 | trip LED resistor | C488946 (Yageo RC1206FR-077K32L) | not captured | — |
| 14.7 kΩ, 1 %, 1206 | main LED resistor | C488648 (Yageo RC1206FR-0714K7L) | not captured | — |
| 110 kΩ, 1 %, 1206 | cascode bias | C246043 (Yageo RC1206FR-07110KL) | not captured | — |
| 100 µF, 25 V polymer | input | C3274630 (Panasonic 25SVT100M) and others | not captured | ripple rating not read; need about 4.6 A RMS in total [H] |
| 10 µF, 25 V, X7R, 1206 | input | C70462 (Yageo CC1206KKX7R8BB106) | not captured | — |

**Consequence for the output bulk capacitor.** The only 33 µF, 200 V parts are through-hole and in low stock. Three 10 µF, 200 V parts (C112474) per rail give 30 µF plus the ceramics, which still meets the calculator's 27.5 µF per rail, from a part with 57,000 in stock. Either way the bulk capacitors are through-hole, so they need JLCPCB's through-hole assembly or hand-soldering.

**Decided 2026-11-14 (P-15):** three 10 µF, 200 V (C112474) per rail, plus the 1 µF, 250 V ceramic. The 33 µF part is not used.

## Correction and third pass (2026-11-15)
**Correction.** The second pass above treated a part's appearance in JLCPCB's search listing as proof of stock. It is not: the listing includes parts with zero stock. Each part page was opened this time. Three of the second-pass choices were effectively unavailable, and the 100 µF polymer capacitor is out of stock in every variant found.

| Second-pass choice | Stock found | Replacement | Stock |
|---|---|---|---|
| Sense resistor C76239 | 5 | C429335, 6 mΩ, 3 W | 3,872 |
| 110 kΩ 1206 C246043 | 3 | C17904, 200 V, 250 mW | 11,469 |
| 7.32 kΩ 1206 C488946 | 10 | C247199 | 4,878 |
| 100 µF 25 V polymer C3274630 | 0 (also C1020104, C2919878, C723101, C5129328) | 8 × 10 µF ceramic C70462 plus one 330 µF 25 V electrolytic C74593 | 205,388 / 8,924 |
| Bulk electrolytic C112474 | 57,166, but no ripple rating shown | C106302, 180 mA at 100 kHz | 8,083 |

Confirmed with stock: C861299 (7,739), C861296 (5,277), C488648 (3,211), C83468 (8,057), C16902 (12,645).
Newly chosen: clamp diode SS510C C123944 (22,339) and clamp resistor 300 Ω 2 W 2512 C91264 (1,911), three in parallel.
The consolidated list is `FINAL_DESIGN_FOR_LAYOUT_2026-11-15.md`.

## Still not checked
Standard-value parts not looked up individually: 499 kΩ, 12.7 kΩ, 44.2 kΩ, 9.53 kΩ, 86.6 kΩ, 5.11 kΩ, 2 kΩ, 100 kΩ, 10 kΩ and 200 Ω resistors; 4.7 nF, 10 nF, 220 nF, 470 pF and 100 nF 100 V capacitors; the primary clamp resistor (100 Ω, multi-watt) and diode.

## Substitutes adopted (2026-11-14, later)
- Switch: **CSD19531Q5A** (C2760462). 6.0 mΩ typical, 7.8 mΩ maximum at 6 V gate drive [DS].
- Optocoupler, all three: **TCMT1108** (C3014154, 2,239 in stock). 130–260 % at 5 mA [DS]. Chosen over TCMT1103 because TCMT1103 is graded at 10 mA and this design runs the LED at 1–2 mA.
- Transient suppressor: **SMBJ130A** (C224006).
- Calculator re-run with these: `calc/CALC_RECORD_2026-11-14.md`, revision section.

## What it changes
- The transformer is the one part that cannot come from the library. Order DA2034-AL separately and plan for hand-fitting or consignment.
- Choose the switch and optocoupler from the library alternatives, then re-run the calculator for the optocoupler grade.
