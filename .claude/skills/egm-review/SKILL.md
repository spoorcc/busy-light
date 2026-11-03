---
name: egm-review
description: Run the Goldfish protocol on a design doc - stateless subagent reviews (comprehension, antagonistic, implementation readiness) and record the result.
---

# Goldfish protocol

Goldfish must be **stateless**: spawn each as a fresh subagent (Agent tool, default type, no fork) and pass **only** the
design doc path plus the instruction below. Do not summarise or explain the doc to them, and do not share this conversation.

1. **Comprehension check** -- prompt: "Read <doc> and the files it references. Explain back the architecture, intent and
   scope in your own words, and list anything you could not understand. Do not review yet."
   Compare with the intended design. Mismatch => the document is ambiguous: redraft, repeat.
2. **Antagonistic review** -- spawn 2-3 goldfish in parallel with different lenses (e.g. failure modes/safety;
   testability/auditability/NFRs; hidden dependencies/integration/manufacturability). Prompt: "You are a skeptical reviewer.
   Find edge cases, hidden dependencies, logical gaps, ambiguous requirements, missing tests/verification, unstated assumptions.
   Output a table: severity, finding, evidence (quote), recommendation."
3. **Resolve** -- as Elephant, address each finding: change the doc or reject with reasoning. Do not apply goldfish
   suggestions blindly; verify claims against the repo.
4. **Implementation readiness** -- fresh goldfish: "Could you implement this exactly, without asking questions? Verify
   file paths, data structures, signatures/nets/dimensions, and that every deliverable has a test or verification. Answer GO or NO-GO
   with reasons." NO-GO => back to drafting.
5. Record in `docs/reviews/RV-nnn.md` (`docs/templates/review-record.md`): findings, resolutions, verdict. Link it from the plan.
