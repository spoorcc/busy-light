# Licensing

Decision: [ADR-0013](docs/decisions/ADR-0013-licensing.md). Machine-readable map: [`REUSE.toml`](REUSE.toml).
Check with `reuse lint`.

| Part | Licence | Text |
|------|---------|------|
| Code: firmware (`sw/`), scripts, generators, build configuration, CI | Apache License 2.0 | [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) |
| Documentation, hardware files (`hw/`), mechanical files (`mech/`), images | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International | [`LICENSES/CC-BY-NC-SA-4.0.txt`](LICENSES/CC-BY-NC-SA-4.0.txt) |

Copyright 2026 Ben Spoor.

In plain words (this summary is not the licence, the texts above are):

- **Code** may be used, changed and sold by anyone under the Apache-2.0 terms.
- **Documentation, hardware and mechanical files** may be copied, changed and shared with credit, under the same licence,
  for **non-commercial** purposes. Selling devices or services built from them needs a separate licence from the owner.
- Using a unit that you bought is not restricted.
- The hardware and mechanical files are **source-available, not open source hardware**, because commercial use is excluded.
- Creative Commons licences do not grant patent rights, and Creative Commons does not recommend them for hardware.
- Third-party parts (Zephyr, MCUboot, Mbed TLS, KiCad libraries, Wi-Fi binaries) keep their own licences.

This is not legal advice. A lawyer should read the texts before the first commercial sale.
