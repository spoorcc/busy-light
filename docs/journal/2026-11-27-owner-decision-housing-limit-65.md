# Owner decision of 2026-11-27: raise the housing limit to 65 mm (in the working session; recorded by the assistant)

Context: the owner asked for a droplet-shaped board nose with more room around the USB-C connector (the 22 placement rules cannot all be met on
the 12 mm tab, `docs/verification/reports/p1-placement-feasibility.md`). The assistant sized a 20 mm wide nose and said that the largest housing dimension would stay
at 57.43 mm along the nose, under the 60 mm of MECH-001. Owner answer, in full: **"Raise to 65mm"**.

## What was recorded
- MECH-001 (Approved): upper limit 65 mm (was 60 mm since 2026-11-22, 58 mm before), as an approved amendment in the owner's words.
- SYS-028 (Draft, parent of MECH-001): the acceptance range now says 48 mm to 65 mm. It still said 58 mm while MECH-001 had 60 mm: an existing mismatch between parent and child, now closed.
  SYS-028 stays Draft; only the owner approves it.
- Code: `mech_outline.MAX_DIM_MECH001` is 65.0; the generator guard `MAX_DIM_SPIKE_MM` (plan 06 D2, 59.8 mm) was a second, separate limit that would have stopped any longer nose with a `ValueError`; it now follows the requirement
  limit minus 0.2 mm (`MAX_DIM_GUARD_MM`, print tolerance). Tests: `test_housing_limit_is_65_mm_since_2026_11_27`, `test_housing_size_within_mech001`, `test_t12_largest_dim_is_computed_and_limited`.

## Points for the owner
- The smallest ITF tennis ball is 65.4 mm (the rationale of SYS-028 says "about 67 mm"). A housing at 65.0 mm leaves 0.4 mm to "smaller than a tennis ball"; the limit is a ceiling, not a target.
- The round body stays 53 mm (D_out); only the nose at the connector grows. The working value [53] mm of SYS-028 is unchanged.
- The cable and its plug stay outside the measurement (MECH-001 rationale).
- Not done in this entry: the housing nose (plan 05, `mech/freecad`), the Edge.Cuts outline, the panel tabs and the hook keep-outs; they follow the ADR and plan 08 revision 7.
