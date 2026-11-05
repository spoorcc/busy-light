# Part evidence

Status: Draft (HW-012, ADR-0017, both Proposed or Draft; nothing here is Approved).

This folder holds the facts that the hardware analyses take from vendor documents. Each fact is a **claim**:
a value, its unit, the conditions, and where it was read (document hash, page, short quote).
A script checks the files. A claim is trusted only when its status is `verified`.

## Why this exists

Earlier analyses copied datasheet numbers by hand into reports and scripts. A reader could not see
which page a number came from, who read it, or whether a second person checked it.
One wrong digit in a current-limit equation or a threshold can break a safety function.
This format makes each number traceable and checkable by machine.

## Layout

| Path | Content |
|------|---------|
| `schema/part-evidence.schema.json` | JSON Schema, draft 2020-12, for one part file |
| `parts/<key>.yaml` | One file per part, or per family of passive parts. `<key>` is the lower-case `part.key` |
| `../../scripts/check_part_evidence.py` | The checker |
| `../../scripts/part_evidence.py` | Library: `load_claim()` for scripts |

## Vendor documents stay outside the repository

ADR-0015 item 8 says vendor datasheets are linked, not committed. Therefore:

- The PDFs live in the datasheets folder, default `/home/ben/Programming/busy-light-datasheets/`.
  Set the environment variable `BUSY_LIGHT_DATASHEETS` to use another folder.
- A claim file may hold the **SHA-256 of the document**, the **page**, and a **short quote**.
- A quote is **one sentence or one table row, at most 300 characters**. Never copy a table, a figure or a page.
  The checker refuses a quote with a line break, with more than one sentence, or longer than 300 characters.
- Do not commit the PDFs, page images or long extracts. Do not put vendor figures in this folder.

## Data format and the standards behind it

| Choice | Decision |
|--------|----------|
| File format | YAML 1.2 (read with `yaml.safe_load`), validated by JSON Schema draft 2020-12 |
| Unit strings | `pint` syntax (see below) |
| `source` object | Modelled on the W3C Web Annotation selectors |
| Provenance fields | Modelled on W3C PROV |

The fields are *modelled on* these standards. They are not JSON-LD and do not carry an `@context`
(see ADR-0017 for the alternatives that were rejected).

### `source`: W3C Web Annotation selectors

| Field | Web Annotation concept |
|-------|------------------------|
| `document` | The annotation target (a document id from `documents`, which holds the file name and the hash) |
| `page` | `FragmentSelector` with `page=N` (RFC 3778). N counts physical PDF pages from 1 |
| `printed_page` | The number printed on the page, only when it differs |
| `locator` | Free text: table, figure or section name |
| `quote` | `TextQuoteSelector.exact` |
| `bbox` | Optional box `[x0, y0, x1, y1]` in PDF points, origin at the bottom-left of the page |

### Provenance: W3C PROV

| Field | PROV concept |
|-------|--------------|
| `extracted_by`, `verified_by` | `prov:Agent` (`kind`: `ai`, `human` or `tool`; `name`; optional `session`) |
| `method` | The `prov:Activity` type: `extracted`, `human-read`, `computed-from` |
| `extracted_on`, `verified_on` | `prov:atTime` of the activity |
| `derived_from` | `prov:wasDerivedFrom` (claim ids), required for `computed-from` |
| `documents[].sha256` | The identity of the `prov:Entity` that was read |

### Units: pint, not UCUM

Units are strings that the Python package `pint` parses (`pint.UnitRegistry().Unit(text)`).
The checker refuses a string that pint cannot parse.

Why pint: the consumers are Python scripts (`hw/sim/`), and pint reads the strings with no extra table.
UCUM would be more neutral between languages, but it needs a separate parser and has no Python
unit conversion in the repository tooling. If a UCUM export is needed later, the mapping is mechanical.

| Quantity | Write | UCUM (for reference) |
|----------|-------|----------------------|
| Volt, millivolt | `V`, `mV` | `V`, `mV` |
| Ampere, milliampere, microampere, nanoampere | `A`, `mA`, `uA`, `nA` | `A`, `mA`, `uA`, `nA` |
| Ohm | `ohm`, `kohm`, `Mohm`, `mohm` | `Ohm`, `kOhm`, `MOhm`, `mOhm` |
| Farad | `pF`, `nF`, `uF` | `pF`, `nF`, `uF` |
| Time | `ns`, `us`, `ms`, `second` | `ns`, `us`, `ms`, `s` |
| Temperature | `degC` | `Cel` |
| Thermal resistance | `K/W` | `K/W` |
| Percent, ratio | `percent`, `dimensionless` | `%`, `1` |

Write ASCII only (`uA`, not the micro sign; `ohm`, not the ohm sign).
A rating that the datasheet gives as a factor of the supply (for example `0.7 x VCC`) is stored as
`unit: dimensionless` with the factor, and the claim `notes` say "times VCC".

## Anatomy of a part file

```yaml
schema_version: 1
part:
  key: TPS2553                 # prefix of every id; file name is tps2553.yaml
  mpn: TPS2553
  manufacturer: Texas Instruments
  selection: chosen            # chosen | candidate | placeholder | family
  package: {code: DBV, name: SOT-23-6, pin_count: 6}
  used_in: [U7]                # reference designators of the board
  ids: []                      # LCSC or other ids; only when read from a cited source
documents:                     # the vendor documents that claims cite
  - {id: tps2553-ds, title: ..., doc_number: SLVS841G, origin: manufacturer,
     file: tps2553.pdf, sha256: <64 hex>, pages: 46, ...}
defaults:                      # inherited by every pin and claim that does not set it
  source_document: tps2553-ds
  method: extracted
  extracted_by: {kind: ai, name: claude-sonnet-5.5/extractor}
  extracted_on: "2026-11-05"
  status: unverified
  package: DBV
pins:                          # the pin table, for schematic and PCB checks
  - {id: TPS2553.pin.4, pin: "4", name: FAULT, pin_type: open_drain,
     source: {page: 4, locator: Table 5-1, quote: "FAULT 4 3 4 3 O Active-low open-drain output, asserted during"}}
claims:
  - id: TPS2553.rec_vin
    parameter: Input voltage, IN
    category: recommended      # abs_max | recommended | electrical | timing | thermal | function | mechanical | other
    min: 2.5
    max: 6.5
    unit: V
    source: {page: 5, locator: Section 6.3, quote: "VIN Input voltage, IN 2.5 6.5 V"}
```

### Claim fields

| Field | Rule |
|-------|------|
| `id` | `<PART>.<param>[.<cond>]`, unique over all files. `<PART>` equals `part.key`. Pins use `<PART>.pin.<n>` |
| `parameter` | Name and symbol as the document uses it |
| `category` | See the list above. `abs_max` and `recommended` are the limits that analyses check against |
| `condition` | Structured keys: `supply_voltage`, `temperature`, `load`, `load_current`, `input`, `test` or any key the table uses. A value is text, a number, or `{value\|min\|typ\|max, unit}` |
| `min`, `typ`, `max` | Numbers in `unit`. Each stored number must occur in the quote. `min <= typ <= max` |
| `unit` | A pint string. Required with a number |
| `formula` | For an equation: `expression` (arithmetic and `ln`, `log`, `exp`, `sqrt` only), `variables` (name to unit) and `unit` of the result |
| `statement` | A qualitative fact in your own words, for example "EN is active high" |
| `source` | `document`, `page`, `quote`, optional `printed_page`, `locator`, `bbox`. Required unless the status is `source-missing` |
| `method` | `extracted`, `human-read` or `computed-from` |
| `extracted_by`, `extracted_on` | Who read the value and when |
| `verified_by`, `verified_on` | Who checked it and when. Only with status `verified` |
| `status` | `unverified`, `verified`, `disputed`, `source-missing` |
| `notes` | Anything a reviewer needs: column choice, ambiguity, a conflict inside the document |

A claim is either quantitative (a unit with `min`, `typ` or `max`, or a `formula`) or qualitative (`statement`).

### Pin table

A `pins` entry holds the pin number as printed (`"4"`, `"A2"`, or a list text such as `"1,2,11,14,36-53"`),
the `name`, the `pin_type` (`input`, `output`, `io`, `power`, `ground`, `open_drain`, `nc`, `passive`, `other`),
the `package` code and a source. `aliases` lists other names that the schematic symbol may use.
The checker compares the pin table with the netlist (see "Run the checker").

## How to add a claim

1. Find the value in the vendor document. Note the physical PDF page (count from 1) and the table or section.
2. Check the part has a `documents` entry with the right file and `sha256`:
   `sha256sum <file>` in the datasheets folder. Add `origin`. Use `manufacturer` only when you took the file from the manufacturer.
   Use `distributor`, `owner-supplied`, `third-party` or `unknown` otherwise, and say why in `notes`.
3. Add the claim. Copy **one** sentence or table row as the `quote`. Take it from the text of that page,
   with spaces as in the page. The checker ignores differences in spaces, line breaks, dashes and the micro sign.
4. Set `min`, `typ`, `max` from the **column** of the table. Text extraction can lose the column. When the row has
   fewer numbers than columns, check the column (for example by the x position of the number) and write that in `notes`.
5. Leave `status` as `unverified` (the default). Do not set `verified` yourself.
6. Run `python3 -I scripts/check_part_evidence.py`. Fix every error.
7. If the document is not in the datasheets folder, write the claim with `status: source-missing`, **no number**,
   and `notes` that say what is missing. Never enter a number from memory.

## The verified rule

- A value that a tool or an AI agent extracted starts as `unverified`.
- Only a **human**, or an **agent other than the extractor**, may set `status: verified`.
  The checker compares `verified_by` and `extracted_by`: an AI verifier must have a different `name`
  (model and role, for example `claude-opus/goldfish-1`). A new session of the same agent name is the same extractor.
- A human who read the value from the document may verify it (`method: human-read`).
- `verified` needs `verified_by` and `verified_on`.
- The verifier reads the document page again, not only the claim. The checker proves that the quote occurs on the page
  and that each stored number occurs in the quote. It does **not** prove that the number belongs to the right column,
  the right variant or the right condition. That is the verifier's job.
- `disputed` means a check found a difference. Put the difference in `notes`.
- `source-missing` means no document is in hand. A `source-missing` claim holds no number, no source and no formula.
- Only the project owner approves documents. Changing a claim to `verified` does not approve anything else.

## Run the checker

```
pip install --group dev          # pyyaml, jsonschema, pint, pytest, ruff, mypy (once)
python3 -I scripts/check_part_evidence.py
python3 -I scripts/check_part_evidence.py --netlist <path>/full.net
```

Always run: schema validation; unique ids; id prefix equals `part.key`; document references; pint unit parse;
`min <= typ <= max`; the verified rule; quote shape; each number occurs in the quote; formula syntax;
`derived_from` ids exist.

Run only when the datasheets folder exists: SHA-256 of every document, page count, and that each quote occurs on its page
(`pdftotext` from poppler, layout text and reading-order text, spaces normalised).
Without the folder these checks print `NOT RUN` and the exit status stays 0. A missing check is never reported as passed.

Run only with `--netlist`: every `used_in` reference exists in the netlist (use `--subset-netlist` for a netlist that
holds only part of the board, such as `gate.net`); the pin table of each part is compared with the pins of each of its references.
The pin report lists netlist pins that the table does not know (a mismatch), pins that match by name but not by number
(the symbol has no pad numbers, so the pad number is not checked), and table pins that the netlist does not use.
`--fail-on-pin-mismatch` makes a mismatch an error.

Exit status: 0 no errors, 1 errors, 2 a required package is missing (`NOT RUN`).
The pytest suite (`scripts/test_check_part_evidence.py`) also validates the committed files, so the existing CI step `pytest` covers the format.
The repository CI does not run the checker with the datasheets folder, because the PDFs are not in the repository.

## Using a value in a script

```python
from part_evidence import load_claim, UnverifiedClaimError

rilim = load_claim("TPS2553.rec_rilim")                       # raises UnverifiedClaimError today
rilim = load_claim("TPS2553.rec_rilim", allow_unverified=True)  # allowed, the caller must print it
r_min_k, r_max_k = rilim.min, rilim.max                        # 15.0, 232.0 and rilim.unit == "kohm"
```

`load_claim(id)` returns a `ClaimValue` (`min`, `typ`, `max`, `unit`, `status`, `statement`; `quantity("max")` gives a pint
`Quantity`). It refuses a claim whose status is not `verified`, and always refuses `source-missing`.
A script that passes `allow_unverified=True` shall print the status next to the result.

How the spike scripts (`hw/kicad/spike-gate/sim/` on branch `spike/hw-gate`) would use it. Nothing is changed there yet.

| Script | Constant now | Claim to load | Today |
|--------|--------------|---------------|-------|
| `ilim_steps.py` | `ios_max/ios_nom/ios_min` (22980, 23950, 25230 and the exponents) | `TPS2553.ios_max_eq`, `TPS2553.ios_nom_eq`, `TPS2553.ios_min_eq` (`formula`) | present, unverified |
| `ilim_steps.py` | `R_MIN_K, R_MAX_K` | `TPS2553.rec_rilim` | present, unverified |
| `ilim_steps.py` | `RDS_ON_MAX_OHM` (assumed 15 ohm at 3.3 V) | `2N7002.rds_on.vgs_3v3` | `source-missing`: the datasheet gives 7.5 ohm max only at 5 V and 10 V (`2N7002.rds_on.vgs_5v`). The assumption stays labelled |
| `ilim_steps.py` | `I_LEAK_A` (1 uA) | `2N7002.idss.25c`, `2N7002.idss.125c` | present, unverified (1 uA at 25 degC, 500 uA at 125 degC) |
| `ilim_steps.py` | `V_ILIM_V` (assumed 1.0 V) | none | not in the claims: not found in the text read |
| `readback_margin.py` | `VTH_MIN`, `VTH_MAX_COLD` (pin thresholds) | `ESP32-C3-MINI-1.vih`, `ESP32-C3-MINI-1.vil` (factors of VDD) | present, unverified |
| `readback_margin.py` | `rpu` (30k, 45k, 70k) | `ESP32-C3-MINI-1.rpu` | typ 45 kohm only; the 30k and 70k bounds are not in the document |
| `holdoff_cap.py` | `TC_PPM` and the capacitor tolerance | `CAPACITORS.c1_tolerance` | `source-missing` (no Murata datasheet) |
| `holdoff_cap.py` | RCT, tD equations | `TPS3840DL40.rct`, `TPS3840DL40.t_d_min_eq6`, `TPS3840DL40.t_d_max_eq7` | present, unverified |

Because every claim is `unverified` today, a script that calls `load_claim()` without `allow_unverified=True` fails.
That is the intended state: the analysis results are not backed by a second reading yet.

## Current state

Every entry is `unverified` or `source-missing`. No claim is `verified`.
`docs/verification/reports/part-evidence-fill-report.md` lists counts per part, what was not found and what was not run.

## Limits of this format

- It records what a document says. It does not decide whether the part is suitable.
- A quote that occurs on the page can still belong to another variant or column. A human check is required for `verified`.
- Values in graphs and figures are not extracted (the text layer has no curve values).
- Documents that have no text layer (scans, font-encoded files) cannot be quoted. Mark the claims `source-missing`.
- Page numbers are physical PDF pages. A newer revision of the same file changes the hash and needs a new check.
