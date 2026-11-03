---
name: design-review
description: Perform a critical, adversarial review of requirements, architecture, an ADR, a schematic/PCB, a mechanical design, or code against this project's process. Use when asked to review or before approving anything.
---

# Design review

Your job is to find problems, not to confirm. Review against `docs/process/README.md` and the PR checklist.

Check: traceability (parent/verification present), requirement quality (ambiguous, untestable, compound),
missing NFRs, failure modes and fail-safe state, single points of failure, unstated assumptions,
interface mismatches (voltage levels, pinouts, tolerances, protocol versions), margins (power, RAM/flash,
thermal, timing), testability/test access, auditability (versioning, reproducibility, logs),
security, manufacturability and supply chain, strawman alternatives, scope creep.

For domain reviews also apply the checklist in `docs/standards/` (coding-sw s.3-5, design-hw s.8, design-mech s.8).

Output a findings table (severity Critical/High/Medium/Low, finding, evidence, recommendation) and an
outcome. For formal reviews write it to `docs/reviews/` from `docs/templates/review-record.md`.
Do not soften findings; do not approve on behalf of the user.
