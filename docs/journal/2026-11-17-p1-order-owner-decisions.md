# Owner decisions for the prototype board P1 and the overnight work (2026-11-17)

Records the owner's answers of 2026-11-17 in the working session (Ben Spoor). The assistant asked 20 questions, one at a time,
before an unattended overnight run. The answers are given as chosen. Where the owner wrote free text, it is quoted.
The journal does not approve anything. The approvals named below are recorded in the controlled documents
(HW-008, HW-016, HW-017, ADR-0021) with a link back here.

State at the start: branch `ccr-fff92b31-b7kqlu` equal to `main` at `1d2a1a6` (merge of PR #14). The stored board is
`hw/kicad/spike-gate/board/busy_light_spike.kicad_pcb` (two-sided: 41 footprints on F.Cu, 60 on B.Cu including 6 test points).

## Answers

| # | Question | Answer | Effect |
|---|---|---|---|
| 1 | Which board to order | **Re-place one-sided P1** (not the recommendation; the recommendation was the two-sided spike as P1) | New placement with all SMD parts on one side, re-route |
| 2 | Commit and push overnight | Commit and push to `ccr-fff92b31-b7kqlu`, draft PR at the end (recommended) | Small commits, pushed after each step |
| 3 | Approvals now | **HW-008 amended** approved. Free text: "Im aiming for the economic placement option of jlcpcb, use 0.15 traces of in not mistaken. Also see if you can simplify the circuit,.let software switch on 1" | HW-008 Approved with the amendment: through-hole parts (J1) allowed, hand-soldered. JLCPCB **Economic** PCBA. Track width **0.15 mm**, so ADR-0020 option B (0.1 mm) is **not** accepted; ADR-0020 stays Proposed and gets a revision. HW-014, HW-015 not selected here |
| 4 | Meaning of "let software switch on 1" | **Keep 3 steps, trim parts** | The three limit steps and the hardware gate (ADR-0016) stay. Only the part count is reduced (for example one ILIM resistor per step, fewer hold-off capacitors) |
| 5 | How to handle trims while the owner is away | **Pre-approve a rule** (recommended) | A trim goes on the board only if a recalculation (script and test) keeps every step window and the hold-off window inside the HW-010 limits, using JLCPCB basic parts where possible. Each trim is recorded as a HW-010 amendment marked "owner pre-approved by rule, 2026-11-17", for the owner to confirm or revert |
| - | Network change (JLCPCB, LCSC and datasheet hosts) | The owner declined the environment change | No live stock, price or Economic-PCBA rule check from this container. Shop numbers come only from the repository records; every such number is marked "not re-checked 2026-11-17" |
| 6 | Which side | **All SMD parts on top** (LED side), test points stay on the bottom as bare pads (recommended) | |
| 7 | Fallback if one-sided does not route | **Grow the board up to the housing limit** (recommended) | Outline grows in steps up to what MECH-001 (58 mm outside) allows minus wall and posts. FreeCAD fit re-run. Any MECH requirement that is touched is flagged for the owner |
| 8 | Freerouting jar | **Use the Maven Central jar, pin both hashes** (recommended) | `run_pcb.sh` accepts the GitHub release hash `f6f51bb0...` and the Maven Central `freerouting-2.5.0-executable.jar` hash `7f8c6247...`. Run logs record which one ran |
| 9 | Via-in-pad on U9 | **No via-in-pad** (recommended) | Vias next to pads; a test fails on any via inside an SMD pad |
| 10 | PCB spec | **4 layers, 1.6 mm, HASL lead-free** (not the recommendation; ENIG was recommended for the 0.4 mm pitch X2QFN-12 and the 2.0 mm LEDs) | Risk of bridges or opens on U1 (TUSB321, X2QFN-12) to be recorded |
| 11 | Quantity and budget | **5 PCBs, 2 assembled, at most EUR 100** | Keep extended part types few. Price not checked (no network) |
| 12 | Spare capacitors and damping footprint | **Approve both, spares within 10 mm** (recommended) | HW-016 Approved with [5] mm changed to [10] mm; HW-017 Approved; ADR-0021 (S1, measure first) Accepted |
| 13 | Designators | Free text "1+2" | Designators on the top silkscreen where they fit, an assembly drawing PDF with every reference, **and** designators on the bottom silkscreen |
| 14 | Panel | **Own panel with KiKit** (not the recommendation; JLCPCB panelising was recommended) | Scripted panel with rails, fiducials and mouse-bites |
| 15 | Part-swap authority | **Swap anything with an ADR** | IC swaps may be proposed as a Proposed ADR, implemented on a separate branch for the owner to accept |
| 16 | EGM | **Plan and goldfish, then build** (recommended) | Plan 08 and goldfish reviews tonight; if readiness says GO, implement under these answers, recorded as owner pre-approval in this session |
| 17 | Order files | Free text: "Script in repo and setup GitHub ci to always store latest release artifacts from master as draft release, on real release upload files there" | Export script in the repository; a CI job builds the order files on every push to `main` and keeps them in one draft release; on a published release the files are attached to that release. No generated files committed |
| 18 | Side work | Housing fit of the new board; firmware gate on target; bench test procedures; regulatory and technical file (all four) | |
| 19 | Owner decisions not covered | **Pick, log, only if reversible** (recommended) | Hard-to-reverse items (safety part, housing interface, Approved requirement text) are skipped and listed |
| 20 | Hand-off | **Journal, draft PR and a private review page** (recommended) | `docs/journal/2026-11-18-overnight.md`, draft PR, claude.ai page |

## Points the assistant raises (rule 3)

- **HW-008 against SYS-022.** HW-008 gives SYS-022 ("no hand soldering") as its rationale. The amendment allows a hand-soldered
  through-hole J1. SYS-022 is Draft. For the prototype this is accepted by the amendment; for a product, either an SMD
  USB-C receptacle or a SYS-022 change is needed. Listed as an open owner item.
- **JLCPCB Economic PCBA limits are not read.** The assistant's recollection is: one side only, no through-hole assembly,
  a limited part and board-size range. This is not verified (no network). The plan treats the board as one-sided SMD plus
  a hand-soldered J1, which fits that recollection, and lists "check the Economic PCBA rules" as an order-time step.
- **0.15 mm tracks against the fine-pitch parts.** The TUSB321 X2QFN-12 has 0.4 mm pitch. A 0.15 mm track between its pads
  does not fit, so a neck-down at that part may be needed. That is a local exception, to be shown in the DRC rules and the plan.
- **HASL on a 0.4 mm pitch QFN.** Higher risk of bridges or opens than ENIG. The owner chose HASL; it is recorded as a risk.
- **Budget.** Two assembled 4-layer boards with about 12 extended part types at EUR 100 is tight. No price was read.
- **One-sided density.** The two-sided board needed 0.1 mm rules (ADR-0020 option B) to route complete. One side with
  0.15 mm is harder. The fallback (grow the outline) is the owner's answer to that.

## Set-up facts of this container (2026-11-17)

- KiCad 10.0.8 runs from the `kicad/kicad:10.0` Docker image (the same image as CI). The stored board was made with 10.0.6.
- Freerouting v2.5.0 `freerouting-2.5.0-executable.jar` from Maven Central (`repo1.maven.org/maven2/app/freerouting/freerouting/2.5.0/`),
  sha256 `7f8c62471f46ccd165bd0e1d20096404602d56d0480af2da59f31b8c5224a976`. GitHub release downloads are blocked here (proxy 403).
- `git` access to `github.com` works (a Zephyr `ls-remote` answered). `jlcpcb.com` and `lcsc.com` are blocked (proxy 403).
