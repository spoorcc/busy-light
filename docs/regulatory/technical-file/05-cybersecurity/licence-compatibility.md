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
| F3 | NonCommercial: the FAQ says the condition prohibits commercial use. The detailed NC section is on the unread part of the page (characters 100000 to 178882). | same page | Partly |
| F4 | KiCad official libraries are CC-BY-SA 4.0 with an exception: the copyright holder waives article 3 (the Share-Alike and attribution conditions) for electronic designs and generated files that use the library data. The page shows no date or version of the exception. | https://www.kicad.org/libraries/license/ | Yes |
| F5 | Mbed TLS files are offered "under a dual Apache-2.0 OR GPL-2.0-or-later license". The user chooses. Same text in the Zephyr-pinned commit c43f34b9 (`LICENSE`). | Pinned commit read 2026-11-04 | Yes |
| F6 | Noto Sans is under the SIL Open Font License 1.1 (26 February 2007). The font may not be sold by itself. A modified version must not use a Reserved Font Name. No Reserved Font Name was shown. | https://github.com/notofonts/latin-greek-cyrillic/blob/main/OFL.txt | Yes |
| F7 | The `LICENSE` files of Zephyr (tag v4.5.0) and MCUboot (main branch) contain the Apache-2.0 text. The MCUboot file adds: "This product bundles tinycrypt, which is available under the 3-clause BSD license." Per-file licences inside both trees were not checked. | raw.githubusercontent.com `zephyrproject-rtos/zephyr/v4.5.0/LICENSE`, `mcu-tools/mcuboot/main/LICENSE` | Yes, top-level file only |
| F8 | In the pinned `hal_espressif` (commit cc81db00, from the Zephyr v4.5.0 manifest) the Wi-Fi and RF binary libraries are declared in `zephyr/module.yml` with `license-path: zephyr/blobs/license.txt`; that file is the Apache-2.0 text and `REUSE.toml` labels `zephyr/blobs/**` Apache-2.0, copyright Espressif Systems. This is the module's declaration: it was not checked against Espressif's own terms or the blob contents. | git clone of the pinned commit, read 2026-11-04 | Yes, module declaration only |

## Compatibility table

| Component | Role | Licence (see fact) | Used how | Obligation or conflict with ADR-0015 (code Apache-2.0, files CC BY-NC-SA 4.0) | Status |
|-----------|------|--------------------|----------|-------------------------------------------------------------------------------|--------|
| Zephyr RTOS (v4.5.0 pin) | Firmware base | Apache-2.0 (F7, top-level file) | Linked into the image | Compatible with Apache-2.0 code. Keep NOTICE and licence texts. | Open: per-file licences unchecked |
| MCUboot | Bootloader | Apache-2.0, bundles tinycrypt under BSD-3-Clause (F7) | Linked, separate image | Same; add the BSD-3-Clause notice for tinycrypt to NOTICE if it is built in | Open |
| Mbed TLS | TLS | Apache-2.0 OR GPL-2.0-or-later (F5) | Linked | Choose Apache-2.0 and record the choice in the SBOM. The GPL branch is not used. | Open: record the choice and the pinned release |
| Espressif Wi-Fi binaries | Radio | Apache-2.0 as declared by the module (F8) | Linked binary | Compatible with Apache-2.0 code if the declaration is right. Keep the licence text and notices. Espressif's own terms and the supplier declaration for RED and CRA are still to get. | Open: declaration only |
| KiCad symbols, footprints, 3D models | Hardware | CC BY-SA 4.0 with exception (F4) | Used in the design | The exception covers designs and generated files. Copying a library part into `hw/` as a file is not covered and keeps CC BY-SA 4.0. CC BY-NC-SA and CC BY-SA do not combine into one work: a BY-SA part stays BY-SA (SA compatibility is a lawyer question). | Open (LAWYER) |
| Noto Sans | Diagram font | SIL OFL 1.1 (F6) | Installed in CI, not committed; embedded in rendered diagrams only as drawn text | The font is not distributed in this repository. Rendered diagrams carry glyph shapes only (author's reading, to check). | Open |
| `scripts/diagrams/package-lock.json` and its dependencies | Diagram tooling | Mixed, not read | Dev tool only | The lock file is third-party data labelled Apache-2.0 today (P10 of RV-008). List each dependency licence in the SBOM. | Open |
| Vendor datasheets | Reference | Vendor terms | Linked, not committed | None while not committed (ADR-0015 item 8) | Open |

## Actions

- Get Espressif's own licence statement for the binaries (F8 is the module declaration only) and the supplier declaration for RED and CRA. Check per-file licences of Zephyr and MCUboot (F7).
- Read F3 (the detailed NC text) and the CC BY-SA compatibility list.
- Produce the SBOM, then replace this table by rows generated from it.
- Lawyer: the KiCad BY-SA rows and the Wi-Fi binary row.
