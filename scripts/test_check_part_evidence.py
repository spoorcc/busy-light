"""Regression tests for scripts/check_part_evidence.py and scripts/part_evidence.py."""

from __future__ import annotations

import copy
import io
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import check_part_evidence as cpe
import part_evidence as pe
import pint
import pytest
import yaml

AGENT_AI = {"kind": "ai", "name": "model-a/extractor"}
AGENT_AI_2 = {"kind": "ai", "name": "model-b/reviewer"}
AGENT_HUMAN = {"kind": "human", "name": "owner"}


def base_file() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "part": {
            "key": "XPART",
            "mpn": "XPART",
            "manufacturer": "Acme",
            "selection": "chosen",
            "package": {"code": "DBV"},
            "used_in": ["U1"],
        },
        "documents": [
            {
                "id": "ds",
                "title": "t",
                "origin": "manufacturer",
                "file": "x.pdf",
                "sha256": "0" * 64,
            }
        ],
        "defaults": {
            "source_document": "ds",
            "method": "extracted",
            "extracted_by": AGENT_AI,
            "extracted_on": "2026-11-05",
            "status": "unverified",
            "package": "DBV",
        },
        "pins": [
            {
                "id": "XPART.pin.1",
                "pin": "1",
                "name": "IN",
                "pin_type": "power",
                "source": {"page": 1, "quote": "IN 1 power"},
            }
        ],
        "claims": [
            {
                "id": "XPART.vin.max",
                "parameter": "Input voltage",
                "min": 1,
                "typ": 2,
                "max": 3,
                "unit": "V",
                "source": {"page": 1, "quote": "VIN 1 2 3 V"},
            }
        ],
    }


def write_dir(tmp_path: Path, *files: dict[str, Any]) -> Path:
    folder = tmp_path / "parts"
    folder.mkdir()
    for n, data in enumerate(files):
        (folder / f"{data['part']['key'].lower()}{'' if n == 0 else n}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )
    return folder


def run(
    folder: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *extra: str
) -> tuple[int, str]:
    monkeypatch.setenv("BUSY_LIGHT_DATASHEETS", str(tmp_path / "no-such-folder"))
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cpe.main(["--evidence-dir", str(folder), *extra])
    return code, buf.getvalue()


def check(data: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[int, str]:
    return run(write_dir(tmp_path, data), monkeypatch, tmp_path)


def test_valid_file_passes_and_skips_datasheet_checks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    code, out = check(base_file(), monkeypatch, tmp_path)
    assert code == 0, out
    assert "NOT RUN: sha256 and quote-on-page checks" in out


def test_missing_required_field_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    del data["claims"][0]["parameter"]
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "'parameter' is a required property" in out


def test_quantity_claim_needs_a_unit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    del data["claims"][0]["unit"]
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "XPART.vin.max" in out


def test_duplicate_id_is_reported(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"].append(copy.deepcopy(data["claims"][0]))
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "duplicate id XPART.vin.max" in out


def test_duplicate_id_across_files_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    one = base_file()
    two = base_file()
    two["part"]["key"] = "XPART"
    code, out = run(write_dir(tmp_path, one, two), monkeypatch, tmp_path)
    assert code == 1 and "duplicate id" in out


def test_id_prefix_must_match_part_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["id"] = "OTHER.vin.max"
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "must start with 'XPART.'" in out


def test_unparseable_unit_is_reported(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["unit"] = "furlongs_per_fortnight_x"
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "not parseable by pint" in out


@pytest.mark.parametrize(
    "unit", ["V", "mA", "kohm", "uF", "ns", "degC", "K/W", "percent", "dimensionless"]
)
def test_units_used_in_the_repository_parse(unit: str) -> None:
    assert cpe.check_unit(pint.UnitRegistry(), unit) is None


def test_min_typ_max_order_is_checked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0].update({"min": 5, "typ": 2, "max": 3})
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "min <= typ <= max violated" in out


def test_verified_needs_verifier_and_date(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["status"] = "verified"
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "'verified_by' is a required property" in out


def test_verified_by_the_extractor_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    data["claims"][0].update(
        {"status": "verified", "verified_by": AGENT_AI, "verified_on": "2026-11-06"}
    )
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "verified_by equals extracted_by" in out


def test_verified_by_a_different_ai_name_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    data["claims"][0].update(
        {"status": "verified", "verified_by": AGENT_AI_2, "verified_on": "2026-11-06"}
    )
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 0, out


def test_a_human_may_verify_their_own_extraction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    data["claims"][0].update(
        {
            "method": "human-read",
            "extracted_by": AGENT_HUMAN,
            "status": "verified",
            "verified_by": AGENT_HUMAN,
            "verified_on": "2026-11-06",
        }
    )
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 0, out


def test_same_ai_name_with_other_session_is_still_the_extractor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    other = {**AGENT_AI, "session": "later"}
    data["claims"][0].update(
        {"status": "verified", "verified_by": other, "verified_on": "2026-11-06"}
    )
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "different name" in out


def test_source_missing_must_not_hold_a_number(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    data["claims"] = [
        {
            "id": "XPART.vin.max",
            "parameter": "p",
            "status": "source-missing",
            "notes": "n",
            "max": 5,
        }
    ]
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1


def test_source_missing_needs_notes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"] = [{"id": "XPART.vin.max", "parameter": "p", "status": "source-missing"}]
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "'notes' is a required property" in out


def test_long_quote_is_refused(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["source"]["quote"] = "word " * 80
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "quote" in out


def test_two_sentence_quote_is_refused(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["source"]["quote"] = "The first sentence. The second sentence."
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "more than one sentence" in out


def test_value_must_occur_in_the_quote(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["max"] = 30
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "max 30 does not occur as a number in the quote" in out


def test_unknown_document_is_reported(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["source"]["document"] = "other"
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "is not in documents" in out


def test_computed_from_needs_derived_from(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0]["method"] = "computed-from"
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "derived_from" in out


def test_derived_from_must_exist(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["claims"][0].update({"method": "computed-from", "derived_from": ["XPART.nothing.here"]})
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "does not exist" in out


def test_formula_with_undeclared_variable_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    claim = data["claims"][0]
    for key in ("min", "typ", "max", "unit"):
        del claim[key]
    claim["formula"] = {"expression": "2 * R + q", "variables": {"R": "ohm"}, "unit": "V"}
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "undeclared variable 'q'" in out


def test_formula_with_a_call_is_refused(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    claim = data["claims"][0]
    for key in ("min", "typ", "max", "unit"):
        del claim[key]
    claim["formula"] = {"expression": "__import__('os')", "variables": {}, "unit": "V"}
    code, out = check(data, monkeypatch, tmp_path)
    assert code == 1 and "only ln, log, exp and sqrt" in out


NETLIST = """(export (components
 (comp (ref "U1") (value "X"))
 (comp (ref "U2") (value "Y")))
 (nets
  (net (code "1") (name "A")
   (node (ref "U1") (pin "1") (pinfunction "IN") (pintype "passive"))
   (node (ref "U1") (pin "7") (pinfunction "OOPS") (pintype "passive"))
   (node (ref "U2") (pin "1") (pintype "passive")))))
"""


def test_used_in_must_exist_in_the_netlist(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = base_file()
    data["part"]["used_in"] = ["U1", "U9"]
    net = tmp_path / "x.net"
    net.write_text(NETLIST, encoding="utf-8")
    code, out = run(write_dir(tmp_path, data), monkeypatch, tmp_path, "--netlist", str(net))
    assert code == 1 and "used_in 'U9' is not in the netlist" in out


def test_subset_netlist_turns_absent_refs_into_a_note(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    data["part"]["used_in"] = ["U1", "U9"]
    net = tmp_path / "x.net"
    net.write_text(NETLIST, encoding="utf-8")
    code, out = run(
        write_dir(tmp_path, data), monkeypatch, tmp_path, "--netlist", str(net), "--subset-netlist"
    )
    assert code == 0 and "not in the subset netlist" in out


def test_pin_mismatch_is_reported_and_can_fail(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = base_file()
    net = tmp_path / "x.net"
    net.write_text(NETLIST, encoding="utf-8")
    folder = write_dir(tmp_path, data)
    code, out = run(folder, monkeypatch, tmp_path, "--netlist", str(net))
    assert code == 0 and "netlist pin '7' (OOPS) is not in the XPART table" in out
    code, out = run(folder, monkeypatch, tmp_path, "--netlist", str(net), "--fail-on-pin-mismatch")
    assert code == 1


def test_parse_netlist_reads_refs_and_pins(tmp_path: Path) -> None:
    net = tmp_path / "x.net"
    net.write_text(NETLIST, encoding="utf-8")
    pins = cpe.parse_netlist(net)
    assert set(pins) == {"U1", "U2"} and ("1", "IN") in pins["U1"]


def test_normalise_unifies_dashes_spaces_and_micro() -> None:
    assert cpe.normalise("–0.3  µA\n x") == cpe.normalise("-0.3 μA x")


# -- the consumer function -------------------------------------------------------------------


def consumer_dir(tmp_path: Path, status: str) -> Path:
    data = base_file()
    if status == "verified":
        data["claims"][0].update(
            {"status": "verified", "verified_by": AGENT_AI_2, "verified_on": "x"}
        )
    elif status == "source-missing":
        data["claims"] = [{"id": "XPART.vin.max", "parameter": "p", "status": status, "notes": "n"}]
    return write_dir(tmp_path, data)


def test_load_claim_returns_a_verified_value(tmp_path: Path) -> None:
    value = pe.load_claim("XPART.vin.max", evidence_dir=consumer_dir(tmp_path, "verified"))
    assert (value.min, value.typ, value.max, value.unit) == (1, 2, 3, "V")
    assert value.quantity("max").to("mV").magnitude == pytest.approx(3000)


def test_load_claim_refuses_an_unverified_value(tmp_path: Path) -> None:
    folder = consumer_dir(tmp_path, "unverified")
    with pytest.raises(pe.UnverifiedClaimError):
        pe.load_claim("XPART.vin.max", evidence_dir=folder)
    assert (
        pe.load_claim("XPART.vin.max", allow_unverified=True, evidence_dir=folder).status
        == "unverified"
    )


def test_load_claim_never_returns_a_source_missing_claim(tmp_path: Path) -> None:
    folder = consumer_dir(tmp_path, "source-missing")
    with pytest.raises(pe.UnverifiedClaimError):
        pe.load_claim("XPART.vin.max", allow_unverified=True, evidence_dir=folder)


def test_load_claim_unknown_id(tmp_path: Path) -> None:
    with pytest.raises(pe.ClaimNotFoundError):
        pe.load_claim("XPART.nope", evidence_dir=consumer_dir(tmp_path, "verified"))


def test_load_claim_applies_file_defaults(tmp_path: Path) -> None:
    folder = consumer_dir(tmp_path, "unverified")
    item = pe.load_claim("XPART.vin.max", allow_unverified=True, evidence_dir=folder)
    assert item.status == "unverified"


# -- the committed evidence ------------------------------------------------------------------


def test_committed_evidence_files_pass_the_schema_checks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    code, out = run(pe.PARTS_DIR, monkeypatch, tmp_path)
    assert code == 0, out
