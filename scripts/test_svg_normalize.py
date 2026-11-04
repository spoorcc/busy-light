# SPDX-License-Identifier: Apache-2.0
"""Tests for svg_normalize: tolerate coordinate jitter, detect content changes."""

from svg_normalize import normalize

BASE = (
    '<svg width="901px"><text x="12.5" textLength="298.353">ARCH-012 Source</text>'
    '<rect fill="#FEFECE" width="9"/></svg>'
)


def test_coordinate_jitter_is_ignored() -> None:
    jitter = BASE.replace("12.5", "12.4").replace("298.353", "299.613").replace("901px", "955px")
    assert normalize(BASE) == normalize(jitter)


def test_label_change_is_detected() -> None:
    assert normalize(BASE) != normalize(BASE.replace("ARCH-012", "ARCH-013"))


def test_colour_change_is_detected() -> None:
    assert normalize(BASE) != normalize(BASE.replace("#FEFECE", "#FFFFFF"))


def test_missing_element_is_detected() -> None:
    assert normalize(BASE) != normalize(BASE.replace('<rect fill="#FEFECE" width="9"/>', ""))
