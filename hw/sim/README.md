# Hardware simulation and analysis

- `spice/` -- ngspice netlists/models (with provenance and assumptions in a header comment). Empty: the power-up
  netlist of the gate is in `hw/kicad/spike-gate/sim/powerup.cir`.
- `scripts/` -- Python analyses, each with a unit test (`test_<name>.py`). The default `pytest` run includes them
  (`pyproject.toml` testpaths, since 2026-11-21), so `ci.yml` runs them on every push and pull request:

| Script | Question | Requirement, decision |
|--------|----------|-----------------------|
| `amendment2_numbers.py` | Reproduce the numbers of ADR-0016 Amendment 2 with the spike's own models | HW-010, ADR-0016 |
| `bulk_cap_bounds.py` | Lower and upper bound of the +5V rail capacitance | HW-014 |
| `dc_bias_caps.py` | Effective capacitance of the board capacitors under DC bias | HW-014, HW-015 |
| `ilim_switch_leakage.py` | Error of the TPS2553 current limit from switch off-state leakage | HW-010, ADR-0010, ADR-0016 |
| `regulator_heat.py` | Heat of the 3.3 V linear regulator for realistic Wi-Fi use | HW-010, HW-013 |
| `surge_supply_pin.py` | Surge at the supply pin of a 6 V part on VBUS_IC | HW-010, ADR-0016 |

- `analysis-ilim-switch-leakage.md` -- the write-up of `ilim_switch_leakage.py`. The other write-ups are in
  `docs/verification/reports/analysis-*.md`.

The gate analyses of the generated board (hold-off capacitor, current-limit steps, read-back margin, power-up) are in
`hw/kicad/spike-gate/sim/`. The board checks (strict ERC and DRC, fab minimums, supply drops) are in
`hw/kicad/spike-gate/src/` and run in `scripts/ci_hw.sh`.

Results are referenced by `TC-nnn` and archived per `docs/process/verification-strategy.md`. All analyses use vendor
values that are not yet verified claims in `hw/evidence/` (HW-012, Draft).
