# Owner decisions of 2026-11-24: ADR-0024, ADR-0025, R_ILIM3 (in the working session; recorded by the assistant)

Asked by the owner: "I agree with your recommendations also fix ci". The red check on PR #16 is `fab-release` / `build` (the `ci` workflow is green). It fails because the stored board-p1 is behind the schematic and the placement rules.
Making it pass needs the re-placement, which waited for three decisions; the assistant put them to the owner with recommendations and the owner chose the recommended option each time:
1. **ADR-0024 (gate rework): Accepted.**
2. **ADR-0025 (U5): option B, TPS3808G01DBVR** (Accepted).
3. **R_ILIM3: option A,** 54.9 k Yageo AT0603BRD0754K9L with the bench check of the three ILIM resistances.
Implementation findings the owner should see: no 931 k 1 % 0402 resistor is stocked, so the divider is 910 k / 100 k (release maximum 4.399 V instead of 4.491 V, better against the 4.5 V of HW-010); TPS3808G01DBVR stock is 0 at LCSC and 4 on the JLCPCB
overseas count (30 on 2026-11-22); the HOLD_OK high level with the pull-up on VDD_U1 is 2.03 V at the release maximum with worst-case input leakage (thin, as before); the HW-010 amendment text and the DEV record for the unproven R_ILIM1 and R_ILIM2
drift are for the owner to confirm.
