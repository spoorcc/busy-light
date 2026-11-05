# SPDX-License-Identifier: Apache-2.0
"""Read part-evidence files (hw/evidence/parts/*.yaml) and look claims up.

This is the small library behind scripts/check_part_evidence.py. It also holds the example
consumer ``load_claim`` (see hw/evidence/README.md, section "Using a value in a script").

Rules enforced here for consumers: a claim whose status is not ``verified`` is refused unless the
caller asks for it with ``allow_unverified=True``. A claim with status ``source-missing`` has no
number and is always refused.
"""

from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "hw" / "evidence"
PARTS_DIR = EVIDENCE_DIR / "parts"
SCHEMA_PATH = EVIDENCE_DIR / "schema" / "part-evidence.schema.json"
DEFAULT_DATASHEETS = Path("/home/ben/Programming/busy-light-datasheets")


class EvidenceError(Exception):
    """Base class for lookup errors."""


class ClaimNotFoundError(EvidenceError):
    """No claim with this id."""


class UnverifiedClaimError(EvidenceError):
    """The claim exists but is not verified (or has no number)."""


def datasheets_dir() -> Path:
    """Folder with the vendor documents (outside the repository)."""
    return Path(os.environ.get("BUSY_LIGHT_DATASHEETS", str(DEFAULT_DATASHEETS)))


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one evidence file. Raises ValueError when the top level is not a mapping."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    return data


def resolve_entry(
    entry: dict[str, Any], defaults: dict[str, Any], *, is_pin: bool = False
) -> dict[str, Any]:
    """Return a copy of a pin or claim with the file defaults merged in."""
    out = copy.deepcopy(entry)
    for key in ("method", "extracted_by", "extracted_on", "status"):
        if key not in out and key in defaults:
            out[key] = copy.deepcopy(defaults[key])
    if is_pin and "package" not in out and "package" in defaults:
        out["package"] = defaults["package"]
    src = out.get("source")
    if isinstance(src, dict) and "document" not in src and "source_document" in defaults:
        src["document"] = defaults["source_document"]
    return out


def resolved_items(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """All pins and claims of a file as (kind, resolved entry), kind 'pin' or 'claim'."""
    defaults = data.get("defaults") or {}
    items: list[tuple[str, dict[str, Any]]] = []
    for pin in data.get("pins") or []:
        items.append(("pin", resolve_entry(pin, defaults, is_pin=True)))
    for claim in data.get("claims") or []:
        items.append(("claim", resolve_entry(claim, defaults)))
    return items


def evidence_files(evidence_dir: Path | None = None) -> list[Path]:
    """The part files, sorted."""
    return sorted((evidence_dir or PARTS_DIR).glob("*.yaml"))


@dataclass(frozen=True)
class ClaimValue:
    """A claim as a consumer sees it."""

    id: str
    status: str
    unit: str | None
    min: float | None
    typ: float | None
    max: float | None
    statement: str | None

    def quantity(self, field: str = "typ") -> Any:
        """Return min, typ or max as a pint Quantity (pint is imported on first use)."""
        import pint  # noqa: PLC0415

        value = getattr(self, field)
        if value is None or self.unit is None:
            raise EvidenceError(f"{self.id}: no '{field}' value with a unit")
        return pint.UnitRegistry().Quantity(value, self.unit)


def load_claim(
    claim_id: str,
    *,
    allow_unverified: bool = False,
    evidence_dir: Path | None = None,
) -> ClaimValue:
    """Return the claim with this id. Refuse it unless it is verified.

    ``allow_unverified=True`` also returns ``unverified`` and ``disputed`` claims; callers that do
    this must say so in their output. A ``source-missing`` claim is always refused.
    """
    for path in evidence_files(evidence_dir):
        data = load_yaml(path)
        for _kind, item in resolved_items(data):
            if item.get("id") != claim_id:
                continue
            status = str(item.get("status"))
            if status == "source-missing":
                raise UnverifiedClaimError(f"{claim_id}: source-missing, it has no value")
            if status != "verified" and not allow_unverified:
                raise UnverifiedClaimError(
                    f"{claim_id}: status is '{status}', not 'verified' "
                    "(pass allow_unverified=True to use it)"
                )
            return ClaimValue(
                id=claim_id,
                status=status,
                unit=item.get("unit"),
                min=item.get("min"),
                typ=item.get("typ"),
                max=item.get("max"),
                statement=item.get("statement"),
            )
    raise ClaimNotFoundError(claim_id)
