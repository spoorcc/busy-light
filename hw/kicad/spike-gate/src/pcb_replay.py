# SPDX-License-Identifier: Apache-2.0
"""Spike (plan 06): run metadata of a routing run. Pure Python (no pcbnew). The replay and stale-session parts of G6
are not written yet."""
import datetime
import hashlib
import json

META_KEYS = ("placed_board_sha256", "dsn_sha256", "kicad_version", "jar_sha256", "fr_passes", "fr_threads",
             "java_version", "wall_time_s", "planes", "created")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_meta(path, **fields):
    """Write run_meta.json / routed.meta.json. All META_KEYS must be given (`created` defaults to now, UTC)."""
    fields.setdefault("created", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    missing = [k for k in META_KEYS if k not in fields]
    if missing:
        raise ValueError("missing meta keys: " + ", ".join(missing))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({k: fields[k] for k in META_KEYS}, f, indent=1, sort_keys=True)
        f.write("\n")
