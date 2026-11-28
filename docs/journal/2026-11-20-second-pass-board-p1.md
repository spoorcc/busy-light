# Second router pass and the first stored P1 board (2026-11-20)

Continuation of `2026-11-18-simplification-owner-decisions.md` (batches p1b4 to p1b12, best 1 open connection). Owner
instruction: "Continue". The assistant tried the first of the levers listed there: a second Freerouting pass over the
cleaned-up board. Plan 08 section 5 steps 6 to 9; HW-008, HW-010, HW-016, HW-017.

## Second pass: what it does
`hw/kicad/spike-gate/run_repass.sh <run folder>`: every track and via of `final.kicad_pcb` locked, DSN export with the same
switches as stage 2 (`outer`, `branchwidth`), Freerouting 2.5.0 with 60 passes, import, post-route stitch, clean-up of
`pcb_fix.py`, strict DRC. It replaces `final.*` only when fewer connections stay open (the first-pass board stays as
`final_pass1.*`). `run_pcb.sh` runs it when the clean-up leaves an unconnected item (`REPASS=1`, the default).

The first scratch version exported the locked board without its project file. KiCad then knows no net classes: the DSN had
only `kicad_default`, and the branch-width step stopped with "substring not found". The repository script copies the project
files for every board name that a KiCad step reads; `tests/test_run_repass.py` fails when one is missing (checked by removing
the line).

## Results (same KiCad 10.0.8 and jar as the batches, one core per run)
| Board | Open before | Open after | Lock mode | Still open |
|---|---|---|---|---|
| p1b8 run 3 | 1 (`/ILIM`, R_ILIM2 pad 2) | **0** | all locked (scratch and repository script) | - |
| p1b8 run 3 | 1 | 0 | only stage-1 copper and plane vias locked (scratch) | - |
| p1b9 run 2 | 1 | 1 | stage-1 only (scratch) | D14 to D15 data link |
| p1b9 run 4 | 1 | 1 | stage-1 only (scratch) | D14 to D15 data link |
| p1b11 run 3 | 2 | 1 | all locked (repository script) | a +5V piece between In2 and B.Cu |

The p1b9 boards were routed before the ring fix of 2026-11-19 (data chain first); their open link is that defect, not a
limit of the pass. The router score of the scratch run and of the repository script on p1b8 run 3 was the same (882.84), and
so were every check result below; the board files differ in hash.

## The stored board
`hw/kicad/spike-gate/board-p1/` (README in the folder): p1b8 run 3 after the second pass, finished, sourcing fields checked.
Checks run on the stored files on 2026-11-20:
- Schematic regenerated from commit `5785f0e` with `run_full.sh`: byte-identical to the batch schematic, netlist equal apart
  from date and tool lines; strict ERC 0 findings.
- Strict DRC (`SPIKE_ALLOW_KNOWN_OPEN=0`): only `courtyards_overlap` 14 and `items_not_allowed` 1, both U9 (DEV-004).
- `pcb_fabcheck --no-via-in-pad`: PASS, 174 vias, none in an SMD pad, annular ring 0.15 mm on all (ADR-0020 Proposed).
- Power check: +3V3 7.3, +5V 10.0, VBUS 23.9, VBUS_IC 44.1 mV, all with full-width paths; In1 and In2 one piece each.
- `tests/test_board_p1.py` 6 passed; spike-gate suite 431 passed, 0 skipped; repository tests 117 passed.
- `scripts/fab_p1.sh`: exit 0, all gates passed. `scripts/ci_hw.sh`: exit 0 (regeneration check NOT RUN, no generator file).

## Defects found on the way (each with a test that fails before the fix)
- `pcb_finish.py` placed the fiducials after the designators and checked them against copper only; in each of three passes
  a designator (D4, R14, C26) sat on FID1 (`silk_over_copper`). Fiducials now come first and the texts avoid them.
- `scripts/ci_hw.sh` did not run `pcb_fabcheck --no-via-in-pad` on `board-p1/`, although plan 08 (section 4.2) says it does.
  It now runs it and the power check.
- The `kicad/kicad:10.0` image has no pip (`pip: not found`, `No module named pip`), and has no numpy or scipy. The
  `fab-release.yml` jobs called `pip install` directly, so they would have stopped at the first step. Both workflows now
  install `python3-pip` with apt first. **Not verified here:** apt in the container cannot reach a Debian mirror through
  this environment's proxy (plain HTTP refused with 405). The `ci.yml` change runs on the next push; `fab-release.yml` runs
  only on `main`. The first CI run with the change (44827760397) installed pip and then stopped: pip could not uninstall
  Debian's `typing_extensions` 4.13.2 for the pinned 4.16.0 (`uninstall-no-record-file`). The installs now use
  `--ignore-installed` (the pins go to `/usr/local`, first on the path); the same error would have hit `fab-release.yml`.
  CI run 44828060174: the `hardware` job passed; `ci_hw.sh` on GitHub ran the fab check and printed the same four power
  numbers as the local run. `fab-release.yml` is still not run (main only).

## Deviations and open points
- Plan 08 step 8 lists DRC and ERC JSON and `chosen_run.txt` in the stored folder. Not stored: the reports are build
  output that `ci_hw.sh` and `fab_p1.sh` write again; the README records the numbers and the chosen run. Owner to confirm.
- The board has one fiducial on the top (FID1) and three on the bottom; the KiKit panel adds three on the rails.
- 305 mm of signal track runs on In2 (the +5V plane). The plane stays one piece (26 % removed). The second lever of the
  earlier journal (a higher router cost for In2) was prepared and not run: Freerouting reads layer costs from the DSN
  (`autoroute_settings`, "Applied DSN autoroute settings" in the jar), but its defaults could not be read out.
- Open for the owner as before: U5 source, R22 part, the assistant's picks (spares, tab azimuths, 0.75 width rule, 50 mV
  target), DEV-007, ADR-0023 and its amendments, ADR-0022, plan 08 approval.
- Not run: housing fit, antenna range (TC-205), thermal, the workflows on GitHub, JLCPCB DFM upload and price, bench tests.
