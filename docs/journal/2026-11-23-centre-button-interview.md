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
