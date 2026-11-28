# Centre-of-ring button: owner interview and first-order checks (2026-11-23)

Asked by the owner on 2026-11-22 (decision 9): the whole centre of the ring becomes the button. The assistant interviewed
the owner on 2026-11-23 (EGM planning); answers are in `docs/plans/09-centre-button.md` section 0 (in the working session;
recorded by the assistant). Nothing was set to Approved.

## Answers
1. Pressed part: a separate centre disc inside the LED ring (recommended option).
2. Switch place: "study both in the plan" (switch off the centre, or the module moved so that the switch is at the centre).
3. Feel and look: a clear click, translucent disc like the lid, centre not lit on its own.
4. Timing: concept first, then plan 08 revision 6 and the re-placement of P1; P1 is not ordered before that.

## First-order checks (assistant's scratch scripts, not in the repository, so not evidence)
- Module ESP32-C3-MINI-1 at its stored board-p1 place: nearest LED centre to the antenna area 7.6 mm.
- Switch (4.5 x 3.5 mm) at the exact centre: the module fits inside the ring at 320 grid positions (0.5 mm and 3 degree steps,
  0.5 mm to LEDs, 1.0 mm to the switch); the best distance antenna area to nearest LED centre is 3.6 mm.
- Rigid disc on three equal supports: plunger travel is the same for every press point if the support centroid lies under the
  plunger. Supports centred on the disc with an off-centre switch: the plunger can lift on a far-side press.
- Compliant bridges (0.2 N/mm each), switch at the centre, edge press: the press point moves 7.9 mm at the click force of 1.75 N.
  The disc needs a tilt guide, or three switches under a rigid disc.

## Not done
No model, no datasheet read (TL3342 force and travel are assumptions), no coupon, no goldfish review of plan 09 yet. The
scratch numbers use E = 1.5 GPa for PETG (assumption) and a switch of 1.6 N over 0.25 mm (assumption).

## Correction (same day, after the goldfish review RV-018)
- The module body is not centred on its footprint origin: the stored board gives 5.06 mm from the antenna strip to the nearest LED centre, not 7.6 mm.
- The TL3342 body is 6.4 x 5.2 mm (courtyard 8.5 x 6.0 mm), not 4.5 x 3.5 mm. With the real switch at the centre the module fits at only 10 poses
  (2.51 mm, 50 % of the margin) or 58 poses (3.04 mm, 60 %) in the assistant's search.
- A press-position sweep restricted to the usable radius shows that one off-centre switch on soft supports fails, a centred switch with three bridges
  passes only in a narrow stiffness band, and three switches work mechanically. Plan 09 revision 3 carries all of this.

## Step 0 (same day, after "Continue")
The owner said "Continue" after the status report; the assistant read that as a go-ahead for step 0 of plan 09 only (reading datasheets and stock; no requirement, ADR, CAD or board change).
The other questions of plan 09 section 7 are still open and were not answered by "Continue".
- Result: `docs/verification/reports/stock-check-button-switches.md`. No listed part meets all criteria of plan 09 section 4.9; none publishes a force-travel curve.
- Omron B3U-1000P (3.0 x 2.5 mm, 1.50 +- 0.49 N, pre-travel 0.15 mm, LCSC stock 49,545, Extended) is the best small-body candidate; with its body S2 keeps 3.90 mm of the antenna margin (77 %) in the assistant's search.
- The TL3342F160QG has LCSC stock 1 and publishes no travel; the 0.25 mm in the plan is still an assumption.
- The WebFetch helper agents could not resolve lcsc.com and jlcpcb.com (DNS error); `curl` from the container worked, both hosts are allowed in the environment. The JLCPCB page holds the class but not the part's own stock.

## Owner decisions of 2026-11-24 (in the working session; recorded by the assistant)
After the step 0 report the owner said "Do your recommendations". Recorded as decisions D1 to D3 of plan 09 section 0 and nothing else:
- D1: direction S2 (module moved, switch at the centre) with the Omron B3U-1000P; S3 stays as fallback; no scissor-linkage study.
- D2: steps 0 and 1 run as analysis under the Approved requirements.
- D3: the extended-part class of the B3U-1000P is noted; the order-day part and stock check stays in the gate.
Light, hand over the antenna, stuck press, life and force window, disc size and ingress had no recommendation in the report and stay open. Plan 09 is at revision 6; a third readiness pass is running.

## Step 1 (2026-11-24)
Third readiness pass: NO-GO (RV-018 rows R13 to R27, all resolved in plan 09 revision 7). Step 1 built: `button_disc.py`, `button_light.py`, `button_zone.py`, tolerance chains, tests, report, ADR-0026 (Proposed).
The B3U pre-travel tolerance was read on the rendered catalogue page: 0.15 +0.2/-0.1 mm. A goldfish reviews plan and code together before the pair is called ready.

## Review of step 1 (2026-11-24)
A fresh goldfish reviewed plan 09 revision 7 against the built files: NOT READY on reasoning and test strength, all headline numbers reproduced. Resolved in revision 8 (RV-018 rows R29 to R45).
Result worth the owner's attention: the first ADR scored S2 with the B3U at 96 against 89 for S3; the corrected scores are 84 and 87 (within noise), because the best S2 pose puts the metal switch 1.35 mm from the antenna strip, no bridge stiffness holds the force window over the B3U pre-travel tolerance, and three switches miss the window at both ends. The assistant now recommends taking both to the coupon gate; the owner's direction D1 stays the working direction until the owner decides.

## Owner answers, second set (2026-11-24)
Answers to the open questions after revision 8, recorded in plan 09 section 0 as D4 to D8: "Both" (S2 and S3 to the coupon gate); the force window is "good enough to start"; "Button is only used very rarely";
"Light should come from the ring/rim not the center"; "Product should look like a really designed apple grade product". The assistant derived working values (life [2 000] presses, a separate opaque disc with a [0.4] mm gap, flush or
designed dish, MECH-014 appearance proposal) and opened two questions: the process for an Apple-grade surface (FDM tolerance is wider than the gap tolerance) and the disc material and finish.
Process note: the revision 8 commit had damaged ADR-0026 (a slicing error in an edit script removed three sections); found and restored the same day.

## Third answer (2026-11-24)
"I agree with your recommendations also fix ci": recorded as D9 in plan 09 (questions 10 and 11). "Fix ci": the only red check on PR #16 is `fab-release` / `build` (the `ci` workflow and the `fab-release` test job pass). It fails because the stored board-p1 does not
meet the current placement rules and is behind the schematic. Making it pass honestly needs the re-placement (plan 08 revision 6), which waits for three owner decisions (ADR-0024, ADR-0025, R_ILIM3).
