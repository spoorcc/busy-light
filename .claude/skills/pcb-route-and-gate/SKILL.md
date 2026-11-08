---
name: pcb-route-and-gate
description: Run or change placement, Freerouting runs (best-of-N), the strict DRC/ERC gate or the power check in hw/kicad/spike-gate, and report the result. Not for schematic capture, the mechanical outline or a final production board.
---

# Route and gate the spike board

Scope: `hw/kicad/spike-gate` (the generated 4-layer spike board). The scripts are the source of truth; this skill gives
the order of work and the lessons. It does not repeat switches or numbers - read `run_pcb.sh` (env docs),
`src/pcb_rules.py`, ADR-0020 and the newest sections of `docs/verification/reports/spike-pcb-placement-routing.md`.
Rule 12 of CLAUDE.md applies: change boards only through the scripts (pcbnew, kicad-cli); never hand-edit `.kicad_*`.
If the spike is replaced by a production board, review this skill again.

All commands run from `hw/kicad/spike-gate`.

## Order of work
0. **Trace.** The work must trace to an `Approved` requirement (HW-010 for the spike board; CLAUDE.md rule 1). If a
   change needs a new rule or decision, draft the requirement or ADR and ask the user. Cite the ID in the report
   and the CHANGELOG.
1. **Inputs.** Footprints come from datasheets or manufacturer drawings (`src/custom_fp.py`); record the source in the
   report. Schematic and netlist come from `SPIKE_ALLOW_KNOWN_OPEN=0 sh run_full.sh python3 <scratch>/fullN` (argument order: python first,
   then the output directory; it also runs the ERC with profile `full`). Step 3 needs `kicad.net` and `full.kicad_sch` in that
   directory. Regenerate it when `layout_full.py`, `lib_tables.py` or the netlist export changed; otherwise reuse the last one
   named in the report.
2. **Placement rules.** Weights, pin ties and proximity rules live in `src/pcb_rules.py` (`NET_WEIGHT`, `PIN_TIES`)
   and `src/pcb_full.py` (`LAYOUT_RULES`). Change one thing at a time.
3. **Route.** `SPIKE_ALLOW_KNOWN_OPEN=0 sh run_best.sh <input dir> <out dir> <N>`. Set the variable to 0 here:
   the run scripts default to 1 (known-open list accepted), so the result would not be a strict result.
   Required: Java, `FREEROUTING_JAR` and `PCB_PYTHON` (KiCad 10 `pcbnew`; the system `python3` works). They are not set by
   default. The pinned 2.5.0 jar was at `~/Programming/busy-light-tools/freerouting-2.5.0.jar` (sha256 pinned in
   `run_pcb.sh`). Each run starts a Freerouting job of `FR_THREADS` (default 4) threads: 12 runs load the whole machine
   and take tens of minutes. Start from a clean tree or record `git status` in the report; see `run_pcb.sh`.
   Without the jar the board is built but not routed and the picker says "no run finished".
   N is a convention: the 2026-11 batches used 12 (the script default is 6); the router varies from run to run.
   The winner is `<out dir>/best/final.kicad_pcb`, chosen only by (unconnected items, strict FAIL lines, hard findings).
   Exit 0 means all three are 0. Exit 1 also covers "no run finished".
4. **Gate, separate check.** `SPIKE_ALLOW_KNOWN_OPEN=0 python3 src/kicad_strict.py drc <out dir>/best/final.kicad_pcb stitched-4l`
   and `python3 src/kicad_strict.py erc <input dir>/full.kicad_sch full`. The counts per class are in the
   output of the gate (and in `drc_final.json`). If `best/` exited 0 but this gate fails, report the gate result, not the exit code. Run it on `best/`, which holds the libraries
   (the copy by `pcb_pick.py` is conditional on the files existing). Strict mode allows only the profile's `strict_allow`
   entries in `known-open-violations.json`: entries with a maximum of 0 are limits, entries above 0 each carry a `DEV-nnn`
   in `docs/standards/deviations.md`. A pass is therefore not zero findings: it still tolerates the DEV classes; list
   them with their counts in the report. Do not add a waiver yourself; ask the user.
5. **Power check.** `python3 src/pcb_power_check.py <out dir>/best/final.kicad_pcb`: drops of the power paths and plane
   cuts. Compare the drops with the 50 mV analyst target of the report. The currents and the target are assumptions, not
   requirements; say so when you quote them. There is no pass/fail: report the numbers.
6. **Record.** Append a dated section to the report (copy the last batch table in the file, by position; keep its columns; name the batch `ringN` with the next free N), add a CHANGELOG
   entry, run `python3 -I scripts/check_traceability.py` from the repo root, and run the touched tests from `hw/kicad/spike-gate`:
   `../../../.venv/bin/python -m pytest tests/<file>` (the system python has no pytest). Count skipped tests as not run.
   Heading format of the report: `## Update YYYY-MM-DD (tag): topic`. Log exploratory batches
   in `docs/journal/YYYY-MM-DD-topic.md` if they are not in the report.

## If it fails
- No run reaches exit 0: report the best partial result with its counts. Change one thing and run a new batch. Do not
  loosen the gate, add a waiver or invent a `DEV-nnn` to get a pass.
- A tool is missing (Freerouting jar, KiCad, venv): say so and stop. Do not substitute another router silently.
- Power check over target: report it; the target is an assumption, so propose a change (a placement tie, a wider
  track) and test it in a separate batch.

## Lessons (each cost time once)
- Freerouting is not deterministic. One batch is one batch; compare batches, and say so.
- Do not edit sources while a batch runs: each run re-reads them, so the batch mixes two versions.
- Change one thing per batch. Otherwise a result cannot be attributed.
- `lib_footprint_issues` with about 100 false findings means the board is not next to `*.pretty` and `fp-lib-table`.
- Fab limits come only from a fab page that was read; name the fab and the date.
- Shell: `pkill -f <pattern>` can match your own shell (use `run_be[s]t.sh`); start long jobs from a script file;
  use `\cp -f`, never plain `cp` (aliased to `-i`, it hangs agents); a killed background waiter of the agent's shell tool reports exit 144 (check the process list first).
- Keep batch output in the session scratchpad, not in the repo.

## Worked once, not proven (2026-11-08, one 12-run batch each)
Soft placement ties on the current paths: lighter weights kept routing completion and cut the voltage drops; heavier
weights cut them more but no run passed the gate. Values and results: report sections "ring5" and "ring6". The fine
fab rules and the rule "signals stay off the ground plane" are ADR-0020 (Proposed); the report has the experiment and
its limits. Treat these as starting points. Tie keys: `PIN_TIES` (`tie:J1A4-U7` and the others), not `NET_WEIGHT`.

## Placer options and checks (all off by default; one change per batch)
Env knobs of `run_best.sh`: `PLACE_GRID` (mm grid), `PLACE_ANT_KEEPOUT=1`, `PLACE_BLOCKS` (pull of the 7 functional blocks in
`pcb_rules.BLOCKS`), `PLACE_ORIENT` (like parts on one axis; twins in `pcb_rules.TWINS`), `PLACE_ROWS` (test-point row),
`PLACE_STRICT=1` (ICs match rotation and side), `SEED_OFFSET`. Used so far: grid 1.0, keep-out 1, blocks 3, orient 1.5,
rows 0.5 (ring15: 3 of 12 gate-clean, no better board)
The picker ranks: unconnected, strict FAIL, hard, power-check FAIL (nets over 50 mV or without a path), then tidiness. `PLACE_STRICT=1` and rows 3 gave no fully routed run (ring13): do not repeat.
Fab minimum: `python3 src/pcb_fabcheck.py <pcb>` (exit 0 pass, 1 fail, 2 not run; JLCPCB numbers of ADR-0020, which is
Proposed). Tidiness: `python3 src/pcb_quality.py <pcb>`. Tests: `GATE_NET` is needed for `tests/test_gate_logic.py` only.

## Reporting and approvals
- Report counts exactly as the logs show them. List what was not run (antenna/RF, thermal, fab DFM check, other fabs).
- Owner decisions (deviations, ADR acceptance, waivers) are the user's. Never set `Approved` or `Accepted` yourself;
  ask with short, plain choices.
- Commit only when asked. Do not commit build output or scratchpad runs.
