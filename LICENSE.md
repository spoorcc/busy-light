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
  for **non-commercial** purposes. Copying, adapting or sharing these **files** for commercial purposes needs a separate licence from the owner. The licence covers the files as copyright works: it does not stop anyone who re-implements a design independently or builds from their own drawings.
- **If you bought a unit:** the owner (Ben Spoor) grants you the right to use it, to repair it, to run and reflash the firmware that the owner publishes on it, and to print the user manual for internal use of that unit. This applies to units sold by the owner or an authorised seller. It is not revoked for units already sold. It does not allow copying a board, and unsigned or modified firmware is allowed only where secure boot allows it (ADR-0007, not decided yet). Modified firmware ends any conformity claim of the owner.
- The hardware and mechanical files are **source-available, not open source hardware**, because commercial use is excluded.
- Creative Commons licences do not grant patent rights, and Creative Commons does not recommend them for hardware.
- Third-party parts (Zephyr, MCUboot, Mbed TLS, KiCad libraries, Wi-Fi binaries) keep their own licences.

## What "non-commercial" means here (the owner's non-binding reading, not legal advice)

- **Allowed without asking:** a person builds one unit for their own use; a school, club or charity builds units for teaching or its own use; a researcher builds units for a study; you share your changes under the same licence.
- **Needs a licence from the owner:** selling units, kits or services built from the files; a company building units from the files for its own business (including an internal build room); a distributor or contract manufacturer building units for others.
- **Unclear, ask the owner first:** a hobbyist selling a single unit at cost; an employee building one unit at home with company help.

The licence texts rule if this reading and a text differ. This list is guidance, not an extra grant. Not decided: a school that charges tuition, a charity that sells units for fundraising, and a hobbyist who uses a commercial PCB or assembly house.

## Other points

- **Generated files:** files made by an Apache-2.0 generator (KiCad or FreeCAD files, rendered images) belong to the design and are CC BY-NC-SA 4.0. Code snippets inside documents are Apache-2.0.
- **Name:** none of these licences grants any right to the name "busy-light" or its logo (the name is descriptive and not registered). Units built by others carry no CE claim of the owner, and whoever builds and sells a unit becomes its manufacturer with their own conformity duties (for example under the RED and the CRA).
- **Commercial licence:** none exists yet, and there is no template or price. Ask through the GitHub account `spoorcc`.
- **Patents:** no patent is held or claimed by the owner today. The designs have been public since 2026-11-04, which probably ended patentability of what they disclose (to check with a patent attorney). The Creative Commons licences grant no patent rights; the Apache-2.0 patent grant covers the code.
- **Authorship:** the repository is written with an AI assistant. The licences apply to the extent that copyright exists.
- **Contributions:** outside contributions are paused until the contributor terms have a legal check (see `CONTRIBUTING.md`).

This is not legal advice. A lawyer should read the texts, the FAQ above and `CONTRIBUTING.md` before the first outside contribution or the first commercial sale (items marked LAWYER in ADR-0015).
