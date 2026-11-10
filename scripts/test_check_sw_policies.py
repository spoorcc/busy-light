# SPDX-License-Identifier: Apache-2.0
"""Tests for check_kconfig_policy.py, check_secrets.py and check_ci_supply_chain.py."""

from __future__ import annotations

from pathlib import Path

import check_ci_supply_chain as sc
import check_kconfig_policy as kp
import check_secrets as cs

POLICY = {
    "product_configs": ["sw/app/prj.conf", "sw/app/*.conf"],
    "exclude": ["sw/app/tests/**", "**/*debug*.conf"],
    "forbidden": {"CONFIG_SHELL": "shell"},
    "required": {"CONFIG_STACK_CANARIES": "canaries"},
}


def test_parse_config_later_lines_win_and_not_set_is_n() -> None:
    v = kp.parse_config('CONFIG_A=y\n# CONFIG_B is not set\nCONFIG_C="x y"\nCONFIG_A=n\n')
    assert v == {"CONFIG_A": "n", "CONFIG_B": "n", "CONFIG_C": "x y"}


def test_scope() -> None:
    assert kp.in_scope("sw/app/prj.conf", POLICY)
    assert kp.in_scope("sw/app/wifi.conf", POLICY)
    assert not kp.in_scope("sw/app/tests/gate/prj.conf", POLICY)
    assert not kp.in_scope("sw/app/debug.conf", POLICY)


def test_forbidden_is_gate_required_only_on_full_config() -> None:
    v = {"CONFIG_SHELL": "y"}
    assert kp.check(v, "f", POLICY, full=False) == [
        "SWC-001 f: CONFIG_SHELL=y is forbidden (shell)"
    ]
    full = kp.check(v, "f", POLICY, full=True)
    assert any(x.startswith("SWC-002") for x in full)
    assert kp.check({"CONFIG_SHELL": "n", "CONFIG_STACK_CANARIES": "y"}, "f", POLICY, True) == []


def test_dotconfig_with_forbidden_option_fails(tmp_path: Path) -> None:
    dc = tmp_path / ".config"
    dc.write_text("CONFIG_ZTEST=y\n", encoding="utf-8")
    assert kp.main(["--dotconfig", str(dc)]) == 1


def test_repository_fragments_pass() -> None:
    assert kp.main([]) == 0


# Secret-like strings are built at run time so that this file itself does not match the scan.
KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"
GH_TOKEN = "ghp_" + "a" * 36


def test_secret_patterns() -> None:
    assert [n for _, n in cs.scan_text(KEY_HEADER, ".pem")] == ["private key block"]
    assert [n for _, n in cs.scan_text(f"token: {GH_TOKEN}", ".md")] == ["GitHub token"]
    pw = 'static const char wifi_password[] = "' + "hunter22" + '";'
    assert [n for _, n in cs.scan_text(pw, ".c")] == ["C string credential"]
    assert cs.scan_text(pw, ".md") == []  # C rule only in C-like files
    kc = "CONFIG_WIFI_PSK=" + '"' + "secret1" + '"'
    assert [n for _, n in cs.scan_text(kc, ".conf")] == ["Kconfig secret value"]
    assert cs.scan_text('CONFIG_WIFI_PSK=""', ".conf") == []


def test_secret_allow_marker_needs_a_deviation() -> None:
    line = KEY_HEADER + "  # secret-scan: allow DEV-099"
    assert cs.scan_text(line, ".pem") == []
    assert cs.scan_text(KEY_HEADER + "  # secret-scan: allow", ".pem") != []


def test_repository_has_no_secret_findings() -> None:
    assert cs.main([]) == 0


def test_actions_must_be_pinned(tmp_path: Path) -> None:
    sha = "a" * 40
    wf = tmp_path / "w.yml"
    wf.write_text(
        "jobs:\n  j:\n    steps:\n"
        f"      - uses: actions/checkout@{sha}\n"
        "      - uses: actions/setup-python@v5\n"
        "      - uses: ./local-action\n",
        encoding="utf-8",
    )
    found = sc.check_workflow(wf)
    assert len(found) == 1
    assert "setup-python@v5" in found[0]


def test_downloads_must_be_verified() -> None:
    assert sc.check_run_block("curl -fsSL -o a.jar https://x/a.jar\nsha256sum -c sums", "w") == []
    assert sc.check_run_block("curl -fsSL -o a.jar https://x/a.jar", "w")[0].startswith("SWC-005")
    piped = sc.check_run_block("curl -fsSL https://x/i.sh | sh\nsha256sum -c s", "w")
    assert any("piped" in f for f in piped)
    assert sc.check_run_block("# curl is not used here", "w") == []


def test_repository_ci_passes() -> None:
    assert sc.main() == 0
