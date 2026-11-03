# NN -- Title (design doc)

- **Status:** Draft | In Review | Approved | Done | Abandoned
- **Date:**  **Owner:**
- **Area:** sw | hw | mech | project
- **Requirements addressed:** SW-000, ...
- **EGM review record:** RV-000 (comprehension / antagonistic / readiness)

## 1. Problem definition
What problem, for whom, why now. Out of scope.

## 2. Constraints and assumptions
Mark every assumption explicitly -- goldfish reviewers will challenge them.

## 3. Alternatives considered
At least two real options plus "do nothing"; link ADR if the choice is significant.

## 4. Technical plan
Architecture, interfaces, data flow, failure behaviour, NFRs (testability, auditability, safety, security, resources).

## 5. Detailed implementation plan
Unambiguous and complete enough for implementation without further questions:
- **Files to create/change** (exact paths):
- **Data structures / signatures / Kconfig / devicetree:** (sw)
- **Nets, parts, footprints, values:** (hw)
- **Features, dimensions, tolerances, materials:** (mech)
- **Order of work / increments:**

## 6. Test and verification plan
For every new function/block/feature: test case(s) (`TC-nnn`), level, tooling, pass criteria.
Hardware: which simulations/analyses (SPICE, worst-case, thermal...) and expected results.
Mechanical: fit/interference/tolerance/FEM checks.

## 7. Risks and open questions

## 8. Rollout / rollback and traceability
IDs created or changed; what is reverted if it fails.
