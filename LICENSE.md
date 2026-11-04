# Licensing

Decision: [ADR-0015](docs/decisions/ADR-0015-licensing-corrections.md) (supersedes [ADR-0013](docs/decisions/ADR-0013-licensing.md)). Machine-readable map: [`REUSE.toml`](REUSE.toml).
Check with `reuse lint`.

| Part | Licence | Text |
|------|---------|------|
| Code: firmware (`sw/`), scripts, generators, build configuration, CI, and the assistant instructions in `.claude/` | Apache License 2.0 | [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) |
| Documentation, hardware files (`hw/`), mechanical files (`mech/`), images | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International | [`LICENSES/CC-BY-NC-SA-4.0.txt`](LICENSES/CC-BY-NC-SA-4.0.txt) |

Copyright 2026 Ben Spoor.

In plain words (this summary is not the licence, the texts above are):

- **Code** may be used, changed and sold by anyone under the Apache-2.0 terms.
- **Documentation, hardware and mechanical files** may be copied, changed and shared with credit, under the same licence,
  for **non-commercial** purposes. Selling devices or services built from them needs a separate licence from the owner.
- **If you bought a unit:** you may use it, repair it, run and reflash the published firmware on it, and print the user manual for internal use of that unit. This is a written grant by the owner.
- The hardware and mechanical files are **source-available, not open source hardware**, because commercial use is excluded.
- Creative Commons licences do not grant patent rights, and Creative Commons does not recommend them for hardware.
- Third-party parts (Zephyr, MCUboot, Mbed TLS, KiCad libraries, Wi-Fi binaries) keep their own licences.

## What "non-commercial" means here (the owner's reading, not legal advice)

- **Allowed without asking:** a person builds one unit for their own use; a school, club or charity builds units for teaching or its own use; a researcher builds units for a study; you share your changes under the same licence.
- **Needs a licence from the owner:** selling units, kits or services built from the files; a company building units from the files for its own business (including an internal build room); a distributor or contract manufacturer building units for others.
- **Unclear, ask the owner first:** a hobbyist selling a single unit at cost; an employee building one unit at home with company help.

The licence texts rule if this reading and a text differ.

## Other points

- **Generated files:** files made by an Apache-2.0 generator (KiCad or FreeCAD files, rendered images) belong to the design and are CC BY-NC-SA 4.0. Code snippets inside documents are Apache-2.0.
- **Name:** the name "busy-light" and its logo are not licensed by any of these licences; the owner reserves them. Units built by others carry no CE claim of the owner.
- **Patents:** no patent is held or claimed by the owner today. The Creative Commons licences grant no patent rights; the Apache-2.0 patent grant covers the code.
- **Authorship:** the repository is written with an AI assistant. The licences apply to the extent that copyright exists.
- **Contributions:** outside contributions are paused until the contributor terms have a legal check (see `CONTRIBUTING.md`).

This is not legal advice. A lawyer should read the texts, the FAQ above and `CONTRIBUTING.md` before the first outside contribution or the first commercial sale (items marked LAWYER in ADR-0015).
