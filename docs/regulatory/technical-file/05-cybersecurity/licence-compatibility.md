<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
# Licence compatibility of third-party components and record of licence facts

- **Status:** Draft (planned by ADR-0015 item 8 and P14 of RV-008)
- **Date of the checks:** 2026-11-04
- **Guidance, not legal advice.** A lawyer reads this before the first outside contribution or the first sale (ADR-0015, items marked LAWYER).
- **Rule:** a row marked "checked" has a source that was read on the date above. A row marked "not verified" is from the author's memory and must not be relied on. The table is incomplete until the SBOM exists (`05-cybersecurity/sbom/`, not yet produced).

## Record of facts

| # | Fact | Source (read 2026-11-04) | Checked |
|---|------|--------------------------|---------|
| F1 | Creative Commons does not recommend its licences for software or hardware. | https://creativecommons.org/faq/ (summary by the fetch tool, wording not quoted) | Yes, paraphrase |
| F2 | Creative Commons licences do not grant trademark or patent rights. | same page, same limit | Yes, paraphrase |
| F3 | NonCommercial, as defined in the licence text in `LICENSES/CC-BY-NC-SA-4.0.txt` section 1(k): "not primarily intended for or directed towards commercial advantage or monetary compensation"; exchanging material by file sharing is NonCommercial. The licence text defines it, not the FAQ. Whether a given use is commercial is a lawyer question (ADR-0015 open cases). Section 1(c) names "BY-NC-SA Compatible License": a list kept by Creative Commons, not read | local licence text, read 2026-11-04 | Yes |
| F4 | KiCad official libraries are CC-BY-SA 4.0 with an exception: the copyright holder waives article 3 (the Share-Alike and attribution conditions) for electronic designs and generated files that use the library data. The page shows no date or version of the exception. | https://www.kicad.org/libraries/license/ | Yes |
| F5 | Mbed TLS files are offered "under a dual Apache-2.0 OR GPL-2.0-or-later license". The user chooses. Same text in the Zephyr-pinned commit c43f34b9 (`LICENSE`). | Pinned commit read 2026-11-04 | Yes |
| F6 | Noto Sans is under the SIL Open Font License 1.1 (26 February 2007). The font may not be sold by itself. A modified version must not use a Reserved Font Name. No Reserved Font Name was shown. | https://github.com/notofonts/latin-greek-cyrillic/blob/main/OFL.txt | Yes |
| F7 | The `LICENSE` files of Zephyr (tag v4.5.0) and MCUboot (main branch) contain the Apache-2.0 text. The MCUboot file adds: "This product bundles tinycrypt, which is available under the 3-clause BSD license." Count of SPDX tags in the pinned trees (a clone of Zephyr v4.5.0, `hal_espressif` cc81db00, MCUboot 725d63c9, Mbed TLS c43f34b9; counts of files with a tag, 2026-11-04): Zephyr: Apache-2.0 about 53000, BSD-3-Clause 135, MIT 28, ISC 4, CC-BY-3.0 4 (documentation theme files), BSD-2-Clause 3, GPL-2.0 2 (`scripts/checkpatch.pl`, `scripts/coccicheck`: developer scripts), SHL-0.51 1 (`include/zephyr/arch/riscv/csr.h`: a RISC-V header, may be built into the ESP32-C3 image, Solderpad licence, not read). MCUboot: Apache-2.0 425 (tinycrypt is a separate module, not fetched). hal_espressif: Apache-2.0 about 4300, Apache-2.0 OR MIT about 2100, BSD-3-Clause 16, MIT 12, CC0-1.0, BSD-2-Clause, Unlicense OR CC0-1.0 a few. Mbed TLS: Apache-2.0 OR GPL-2.0-or-later 183. Files without a tag were not counted; which files end up in the image is decided by the build and not checked | git clones, grep | Partly: tag counts only |
| F8 | In the pinned `hal_espressif` (commit cc81db00, from the Zephyr v4.5.0 manifest) the Wi-Fi and RF binary libraries are declared in `zephyr/module.yml` with `license-path: zephyr/blobs/license.txt`; that file is the Apache-2.0 text and `REUSE.toml` labels `zephyr/blobs/**` Apache-2.0, copyright Espressif Systems. This is the module's declaration: it was not checked against Espressif's own terms or the blob contents. | git clone of the pinned commit, read 2026-11-04 | Yes, module declaration only |

## Compatibility table

| Component | Role | Licence (see fact) | Used how | Obligation or conflict with ADR-0015 (code Apache-2.0, files CC BY-NC-SA 4.0) | Status |
|-----------|------|--------------------|----------|-------------------------------------------------------------------------------|--------|
| Zephyr RTOS (v4.5.0 pin) | Firmware base | Apache-2.0 (F7); some files BSD, MIT, ISC, SHL-0.51 | Linked into the image | Permissive mix. Compatible with Apache-2.0 code. Keep NOTICE and licence texts. Check `csr.h` (SHL-0.51) once the image is built. The two GPL-2.0 files are developer scripts and not part of the image (author's reading from the file names) | Open: image file list needed |
| MCUboot | Bootloader | Apache-2.0, bundles tinycrypt under BSD-3-Clause (F7) | Linked, separate image | Same; add the BSD-3-Clause notice for tinycrypt to NOTICE if it is built in | Open |
| Mbed TLS | TLS | Apache-2.0 OR GPL-2.0-or-later (F5) | Linked | Choose Apache-2.0 and record the choice in the SBOM. The GPL branch is not used. | Open: record the choice and the pinned release |
| Espressif Wi-Fi binaries | Radio | Apache-2.0 as declared by the module (F8) | Linked binary | Compatible with Apache-2.0 code if the declaration is right. Keep the licence text and notices. Espressif's own terms and the supplier declaration for RED and CRA are still to get. | Open: declaration only |
| KiCad symbols, footprints, 3D models | Hardware | CC BY-SA 4.0 with exception (F4) | Used in the design | The exception covers designs and generated files. Copying a library part into `hw/` as a file is not covered and keeps CC BY-SA 4.0. CC BY-NC-SA and CC BY-SA do not combine into one work: a BY-SA part stays BY-SA (SA compatibility is a lawyer question). | Open (LAWYER) |
| Noto Sans | Diagram font | SIL OFL 1.1 (F6) | Installed in CI, not committed; embedded in rendered diagrams only as drawn text | The font is not distributed in this repository. Rendered diagrams carry glyph shapes only (author's reading, to check). | Open |
| `scripts/diagrams/package-lock.json` and its dependencies | Diagram tooling | Mixed, not read | Dev tool only | The lock file is third-party data labelled Apache-2.0 today (P10 of RV-008). List each dependency licence in the SBOM. | Open |
| Vendor datasheets | Reference | Vendor terms | Linked, not committed | None while not committed (ADR-0015 item 8) | Open |

## Actions

- Get Espressif's own licence statement for the binaries (F8 is the module declaration only) and the supplier declaration for RED and CRA. Check which tagged files go into the built image (F7) once a build exists, including the SHL-0.51 header.
- Read the Creative Commons list of BY-NC-SA compatible licences (F3).
- Produce the SBOM, then replace this table by rows generated from it.
- Lawyer: the KiCad BY-SA rows and the Wi-Fi binary row.
