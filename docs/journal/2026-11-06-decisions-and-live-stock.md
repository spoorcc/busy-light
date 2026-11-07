# Decisions of 2026-11-06 and live JLCPCB stock (2026-11-06)

Records the owner's answers of 2026-11-06 in the working session, in the order asked, and the live stock read that
supports them. Nothing here is Approved. Only the owner approves documents. Stock is a snapshot of 2026-11-06,
read on the JLCPCB parts library in a browser (read-only; nothing was added to a cart or an account).
Corrects `2026-11-06-jlcpcb-stock-check.md` (see the note at its top).

## Live stock read

| Part | LCSC | Stock | Class |
|---|---|---|---|
| Yageo RT0603BRD0747KL, 47.0 kohm 0.1 % 0603 | C326725 | 17,621 | Extended |
| Yageo RT0603BRD0756K2L, 56.2 kohm 0.1 % 0603 | C705784 | 7,107 | Extended |
| Yageo RT0603BRD0727K4L, 27.4 kohm 0.1 % 0603 | C861274 | 14,937 | Extended |
| Panasonic ERA-3AEB3010V, 301 ohm 0.1 % 0603 | C2074494 | 5,222 | Extended |
| Murata GRM31C5C1H104JA01L, 100 nF C0G 5 % 50 V 1206 | C97946 | 96,458 | Extended |
| Murata GRM31C5C1H224JE02L, 220 nF C0G 5 % 50 V 1206 | C464977 | 54,761 | Extended |
| TDK C3216C0G1H683JT000N, 68 nF C0G 5 % 50 V 1206 | C361177 | 2,000 | Extended |
| TI TMUX1101DCKR | C2673506 | 2,258 | Extended |

Method note: a part number search returns the exact part with its stock. Value searches and the category filters
miss parts that sit under other dielectric labels (C0G, COG, NP0, C0G、NP0 are separate filter entries).
Not checked: stock of the fallback TS5A3166DBVR (C353035), the Yageo 301 ohm part C861310, and prices.

## Decisions (owner answers; recommendation in brackets)

1. Branch sync: rebase onto main (recommended: merge). Done on `docs/review-actions`; local `main` was 100 commits
   behind `origin/main`, so the rebase was repeated onto `origin/main`. A push needs a force-push; not done.
2. Stock check: done in this session (recommended).
3. Resistors: Yageo RT0603BRD07 family for 47.0 k, 56.2 k, 27.4 k plus Panasonic ERA-3AEB3010V for 301 ohm
   (recommended). Written into the HW-010 proposal, item (b).
4. Hold-off capacitor: **6 x 100 nF C0G 1206 (Murata C97946)**, not the recommended 220+220+100+68 nF set. Window
   203.2 to 553.2 ms (`holdoff_cap.py`, run 2026-11-06), margin 3.2 ms to the lower edge against 5.9 ms for the
   recommended set. Written into HW-010 item (c) with the thin margin stated.
5. ILIM switch: keep TMUX1101 with the bench check (recommended). DEV-001 and RISK-045 stay open. The BSS138 analysis
   in `hw/sim/` is the conditional fallback.
6. ADR record: draft an ADR-0016 amendment (recommended). **Not started.**
7. SYS-020 relaxed from 1 s to 2 s: goldfish review of the whole bundle first (recommended). **Not started.**
8. Approvals: after items 3 to 7 are done (recommended). Nothing approved.
9. SW-009 "[X] ms": placeholder now, bench measurement of the rail hold-up later (recommended).
10. Kconfig of the USB-Serial-JTAG console: verify by a build; `west` is not installed (cmake and ninja are).
    The owner runs the install commands. **Not started.**
11. Other open items (HW-006 text, ADR-0012, ADR-0010 points 3 to 6, legal review): after the gate approval pass.

## Next steps in order

ADR-0016 amendment draft (item 6); goldfish review of the HW-010, SW-005, SW-006, SW-007, SW-009 and SYS-020
bundle (item 7); the owner approves (item 8). Bench checks stay open: V_ILIM, the 3V3-off case (TC-210 (d)),
hold-off time, each limit step.
