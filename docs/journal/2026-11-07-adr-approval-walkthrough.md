# ADR approval walkthrough (2026-11-07)

The owner went through the ADRs one by one in the working session. Only the owner sets Accepted. Each answer is recorded in the ADR itself.

| ADR | Result | Basis and open conditions |
|---|---|---|
| ADR-0001 coding standard | Accepted | gaps fixed first (criteria linked to NEED-011, SYS-025, SYS-043 to SYS-045; scores added) |
| ADR-0002 Wi-Fi platform | Accepted | ESP32-C3 as prototype platform; spike 7.1 measurements still open |
| ADR-0003 antenna | **Not accepted** | rim placement shown not to clear a full 16-LED ring (assistant's first-order geometry); owner excluded B (SYS-022 read as no manual steps); direction A first decided by spike 7.2, text revised, owner chose not to accept yet |
| ADR-0004 LED and drive | Accepted | update block: item 4 closed by ADR-0010/0016, spikes 7.3/7.5 not run, LED part is a stand-in, SYS-011 hang gap stays |
| ADR-0005 mapping model | Accepted | push accepts the neutral body only |
| ADR-0006 provisioning | Accepted | web login password chosen by the user at first setup |
| ADR-0007 update and boot security | Accepted | staged C, E fallback; pinned ESP-IDF bootloader build acceptable in principle; flash fit open |
| ADR-0008 transport protection | Accepted | HTTPS pinned on the LAN, HTTP in the AP; RAM check open |
| ADR-0009 | (Superseded, no action) | |
| ADR-0010 current limit | Accepted, **point 6 (extended-part fee) open** | update block; TPS2553 kept; Basic-part search inconclusive (the library's Basic filter could not be applied) |
| ADR-0011 housing | **Not accepted** | owner answers recorded: FDM PETG only, wide glow, snap hooks; dimensions and thermal case must be redone |
| ADR-0012 hardware design flow | Accepted | rule 12 wording aligned to CLAUDE.md of today; **gate G1 stays the gate before any product file** (not run in CI, peg azimuth conflict open) |
| ADR-0013 | (Superseded, no action) | |
| ADR-0014 back interface | **Not accepted** | redrafted to the annular bayonet with the accessory family; owner chose not to accept yet |
| ADR-0015 licensing corrections | (already Accepted 2026-11-04) | |
| ADR-0016 gate | (Accepted 2026-11-04) Amendment 2 **Accepted** | VBUS_IC supply, E96 resistors, six 100 nF; open: bench check, TVS1, debounce maximum, spike regeneration |
| ADR-0017 evidence format | Accepted | no goldfish review; header fixed |

Not approved by this walkthrough: any requirement (HW-010, SYS-020, SW-005 to SW-010, HW-013), DEV-001, DEV-005. The readiness goldfish verdict (RV-010) is still NO-GO on the requirements.
