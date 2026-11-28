# Owner decision of 2026-11-28: round 58.5 mm board without a nose (in the working session; recorded by the assistant)

Context: after the droplet nose (2026-11-27) and the 65 mm limit, the owner asked: "Could we enlarge the entire design to 70mm disc to solve more issues? I think the disc size is causing more trouble then it solves".
The assistant pointed out that the 70 mm disc gives a housing of about 77 mm, larger than the largest tennis ball (68.6 mm) and in conflict with NEED-014 (about 53 mm, between a table-tennis ball and a tennis ball).
The assistant also found that the trouble comes from the LED ring (40 mm) on a 46 mm disc: only 3 mm remain to the rim, so J1 cannot sit on the board and needs the tab or nose.
It offered a round disc of about 58.5 mm without a nose, housing about 65.5 mm, MECH-001 limit 65 mm to 66 mm. Owner answer, in full: **"Yes scale up to 58.5, give me visual mock up of led placement I'm considering more LEDs on larger size"**.

## What was recorded
- Direction: round board of 58.5 mm diameter, J1 on the board, no tab and no droplet nose. This replaces the droplet nose chosen on 2026-11-27 (commit 949c418) before any outline, hook or housing change was made for it.
- Not changed yet: MECH-001 (65 mm), SYS-028, `mech_outline.py` and the generator. The housing figure 65.5 mm holds only while the LED ring is at most 40 mm in diameter (J1 behind the ring) or while the ring is opened at J1.
  The amendment of MECH-001 to 66 mm is made with the ADR, after the owner has chosen the LED count and ring diameter.
- Mock-up of the LED placement (artifact, not a repository file): https://claude.ai/artifact/DZPYe64pzByRHY9mYfr2Mp. Numbers come from `mech_outline.py`, the generator and the paper power budget; the connector keep-out and the light model are estimates.

## Findings from the mock-up (not verified by a placement run)
- A ring larger than 40 mm in diameter overlaps the J1 pads (pad edge at R 22.76 mm). It needs a gap of about 12 mm at J1 (one LED fewer). Without the gap the housing grows by the ring growth.
- Every ring variant puts 2 to 4 LEDs in the 15 mm antenna keep-out of the module (today's 40 mm ring has 2). A second ring opening at the antenna end clears it.
- 24 LEDs on a 52 mm ring: pitch 6.6 mm, 360 mA at full white (15 mA per LED, 5 mA per channel part). The current budget stays 500 mA, so the per-LED ceiling falls to 2/3 of today's. 16 LEDs on a 52 mm ring would have a pitch of 10.2 mm, above the 8 mm diffuser distance.
- The level display (SYS-032) needs a count divisible by 4 for even quarter steps.
- Free board area (estimate, minus LED band, module and J1) is about 1400 mm² against about 650 mm² on the 46 mm disc.

## Points for the owner
- LED count and ring diameter (the mock-up shows the trade-offs); whether the ring opens at J1 and at the antenna.
- A change of LED count touches SYS-001, SYS-032, SYS-028 acceptance, HW-001, the schematic (LEDs and bypass capacitors), the firmware and the simulation (16 LED values).
- The mechanical model (D_out 53, the bayonet accessory, posts, hooks, plan 09 button zone) scales with the disc and is redone with the ADR.
