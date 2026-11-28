# Reviews of the P1 board and of ADR-0023, and the gates that follow (2026-11-22)

Owner instructions: "What is next step" (answer: a readiness re-review of plan 08), "Yes", then "Go work" (the work that
needs no owner decision). Plan 08 revision 5, reviews RV-016 and RV-017; HW-008, HW-010, HW-016, HW-017, ADR-0023.

## What was done
- Plan 08 revision 5 (`db3d0e0`): section 0 records the state after the build. Writing it found that the four input-path
  placement rules of section 4.2 were never implemented (all four missed on board-p1).
- RV-016 (`7358ced`): four goldfish on plan 08 and board-p1, 45 findings, **not ready to order**. RV-017 (`933eb0f`): three
  goldfish on ADR-0023, 30 findings, **rejected as written**. The two antagonistic ADR-0023 goldfish stopped at a usage
  limit at about 04:40 UTC and were resumed at 05:25 UTC from their saved state.
- Gates and tests (`64dfa63`, `b91bb05`, and the commit of this entry): `pcb_layout_check.py` (placement rules on a board
  file), `fab_check.py` (exact ILIM values, must-place parts, empty bottom paste), full BOM with the DNP parts, the release
  notes list, the release workflow on pull requests and red on a failed gate, the spike-gate tests in the `ci.yml` hardware
  job, no paste on the DNP spares in the generator, RISK-047 to RISK-053, DEV-008.

## Results, with sources
- Placement rules on board-p1 (`pcb_layout_check.py`, pcbnew in `kicad/kicad:10.0`, part-extent centres): missed R19 to U15
  6.71 mm (rule 6.0), C1 to U5 9.49 (8.0), C27 to U5 17.26 (12.0), C30 to U5 21.95 (14.0), C31 to U5 26.93 (14.0), TVS1 to the
  nearest J1 VBUS pad 7.55 (6.0), U6 13.75 (8.0), R22 10.68 (8.0), R22 to U7 12.53 (6.0).
- Main path widths (pcbnew track list): `VBUS` has two 0.451 mm F.Cu and two 0.450 mm B.Cu segments, `VBUS_IC` two 0.450 mm
  B.Cu segments and two 0.6/0.3 mm vias.
- Full BOM of the board-p1 schematic with kicad-cli 10.0.8: 33 lines, no C4 or C32 (symbols excluded from the BOM are left
  out); with `fab_package.py full-bom --schematic`: 40 lines on GitHub (run below).
- U9 front courtyard on board-p1: 31.94 x 43.29 mm (plan 08 said 43 x 20 mm, the vendor keep-out zone).
- Spike-gate suite in the KiCad image (local, 2026-11-22): 430 passed, 1 skipped (`FREEROUTING_JAR` not set) in 149 s; after
  the new tests 437 passed, 2 expected failures (the known board-p1 defects), 1 skipped, and one test that still expected the
  old 7.5 mm rule (fixed).
- CI run 44989607281 (`64dfa63`): hardware job with the spike-gate tests passed (first run on GitHub); python-tools failed
  on one test that counted the lazy kiutils import of `lib_tables.py` as a pin gap (`ModuleNotFoundError` is not raised at
  run time: `pcb_layout_check.py` ran in the image without kiutils). Fixed in `b91bb05`.
- fab-release run 44989926250 (`b91bb05`, the first run of this workflow on GitHub, on the pull request): test job passed;
  build job made the package and then failed on purpose: `FAILED: placement rules fab_check` (9 rules missed;
  `lcsc_numbers` R22 and U5 not allowed as must-place parts; `bottom_paste_empty` 4 operations from the C4 and C32 pads);
  publish skipped. ILIM values passed: 47.0k, 56.2k, 56.2k 0.1 %.

## Not done or not run
- No owner decision was taken by the assistant: the open rows of RV-016 and RV-017 wait for the owner (gate fixes after
  ADR-0023, CC-pin protection, U5 source, R22 and the drop budget, MECH-001, SW1, the input-path rules).
- No re-placement or re-routing; board-p1 is unchanged and stays not ready to order.
- Not written yet: the HW-003 rating calculation of the input path, the J1-to-U7 drop case in `pcb_power_check.py`, the
  bottom silkscreen map (owner answer 13), the board identification text, the gate truth-table test on `full.net`
  (RV-017 row 8), the TC-210 and TC-217 text updates, O7 and O8, the fail-direction table, the regulatory re-check.
- Not run: housing fit, antenna, thermal, JLCPCB DFM and price, bench.
- The measurement scripts of this day are in the session scratchpad, not stored; `pcb_layout_check.py` replaces the
  placement-rule script and is stored.
