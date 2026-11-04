"""Spike: every real part must carry a HW_REQ field (ADR-0012 item 2). usage: <dump.json>"""
import json
import sys

d = json.load(open(sys.argv[1]))
bad = [r for r, p in d["parts"].items() if not r.startswith("#") and not p["HW_REQ"]]
print("parts without HW_REQ:", bad or "none")
sys.exit(1 if bad else 0)
