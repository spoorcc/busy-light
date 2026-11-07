# 2026-11-07: spike generator brought to the approved HW-010 values

Branch `spike/hw010-regenerate`. Traces to HW-010 (revision approved 2026-11-07), ADR-0016, ADR-0012.

## What changed
- ILIM resistors back to the E96 set (47.0 k, 56.2 k, 27.4 k + 301 ohm); this reverses the spike part of the E192 revert of PR #8 (the source and test changes of commit 98d564d, reverse-applied).
- Hold-off capacitor: six 100 nF C0G 5 % 1206 (C1, C1B to C1F); `sim/holdoff_cap.py` has the set `6x100 (6 parts)` (203.2 to 553.2 ms).
- TMUX1101 VDD pins and their 100 nF capacitors C24, C25 on VBUS_IC (was 3V3).
- CC_OK_3A path deleted: U12 and R7 removed, TUSB321 OUT2_N pin left open (no-connect), ESP32 GPIO1 no-connect.
- `tests/data/gate.net` (SKiDL 3.0.0) and `tests/data/full.net` regenerated from the generators; nets 54 to 52, components still 93.

## Evidence
- Spike tests: 185 passed (baseline before the change: 184 passed). ERC of the drawn full-board sheet: 0 errors, 52 intent nets = 52 drawn nets, output deterministic. The 4 tolerated ERC findings equal the allow-list maximum.
- `ruff check`, `ruff format --check`: clean.

## Not done / not run
- No routing: no Freerouting jar here, so no routed DRC. The unrouted placed 4-layer board builds from the new netlist and is identical on two builds. DRC (placed, 4 layers, planes inner) reports unconnected_items 256 against an allow-list maximum of 241; the same run on `main` gives 257, so the allow-list does not match this invocation and was not changed. Not analysed further.
- Placement seeds and the routed/stitched DRC fixtures (`tests/data/drc_*.json`) are not regenerated.
- Open question on HW-010 text: the revision names "100 kohm pull-downs on the select control pins, 10 kohm on the gate enable nets"; the spike has both (10 k R2/R3 and 100 k R18/R19) on the enable nets. Not changed; the owner decides which network is meant.
- `gen_gate.py` needs `skidl==3.0.0`, which is not in `pyproject.toml`.
