# ADR-0008: Transport protection for the web interface and the push endpoint

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review not yet run
- **Related:** NEED-002, NEED-018, SYS-003, SYS-004, SYS-016, SYS-031, SYS-034, SYS-035, SYS-026, ADR-0002; design doc `docs/plans/02-system-design.md` (section 4.8, gap G3)

## Context and problem
The web interface (SYS-016) takes a password and lets the user change settings and upload a certificate. The push endpoint (SYS-004) takes a token
from Jenkins. The owner stated that the LAN can be shared with untrusted users (assumption A3). On such a LAN, anyone can read clear-text
traffic and replay it. The device has no clock until SNTP succeeds (SYS-031), so any scheme that needs correct time cannot be the only protection.
The device also has little RAM: an HTTPS server and an HTTPS client (Jenkins poll) can run at the same time (SYS-026).
Not known yet (spike 7.1 on ESP32-C3): free RAM with two TLS sessions, time to create a key pair, and whether Zephyr's HTTP server accepts TLS sockets
in the pinned revision.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Password and token never in clear on the LAN | 5 | SYS-034, A3 |
| No dependency on a correct clock | 4 | SYS-031 |
| Fits RAM and flash margin | 4 | SYS-026 |
| Ease of setup for the user (browser, Jenkins) | 3 | NEED-016 |
| Own or company certificate possible later | 3 | SYS-035, NEED-018 |
| Testable on PC and with fuzzing | 3 | SYS-025 |
| Small amount of code to maintain | 2 | project |

## Alternatives considered

### A. Plain HTTP everywhere; password and token in clear (SYS-004/016 as first written)
Smallest code, no certificate handling, works with every Jenkins plug-in.
Strongest case: many hobby devices do this and a home LAN is often trusted.
Cons: on a shared LAN, any user reads the password and token and can replay them. Fails SYS-034.

### B. HTTP with a signed push request (HMAC over body, time stamp and counter); web interface on HTTP
Push token never crosses the LAN. Strongest case: no TLS server on the device, so least RAM and flash for push.
Cons: needs time or a stored counter (replay after reboot is possible if the counter is not persistent, flash wear if it is); Jenkins needs a script, not a stock plug-in;
the web password still crosses the LAN in clear, so B alone fails SYS-034. B would need the web interface to be moved to the access point only, which
removes LAN configuration (SYS-016).

### C. HTTPS on the LAN with a device-generated key pair; plain HTTP only inside the WPA2 provisioning access point (X3 + X4 of the design doc)
In the access point (SSID with unit passphrase, WPA2) the Wi-Fi layer already encrypts and authenticates, so the page is plain HTTP there.
On the LAN, the web interface and the push endpoint use TLS 1.2 with an EC P-256 key pair created at first start. The device shows the SHA-256
fingerprint of the public key. Jenkins pins it (for example `curl --pinnedpubkey`). The user may replace the pair with their own (SYS-035).
Cons: browser warning at first use; TLS server and client in RAM together; key creation time; Java-based Jenkins plug-ins need the certificate in their trust store.

### D. HTTPS everywhere, including inside the access point
One code path, one test matrix. Strongest case: simpler than two modes, and the warning also appears only once per browser.
Cons: the user gets a browser warning during first setup, the worst moment for a non-technical user (NEED-016), with no added protection: the
access point is already encrypted with a per-unit passphrase. The key pair does not exist before first start completes.

### E. Do nothing / defer
Ship A for the prototypes and decide later. Cons: the first 10 units go to real networks (owner round 2), and changing transport later changes the Jenkins
side, the manual and the tests. Rejected.

## Comparison
Scores 0 (poor) to 5 (good), weighted sum in the last row.

| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| No clear text on LAN (5) | 0 | 2 | 5 | 5 | 0 |
| No clock dependency (4) | 5 | 1 | 5 | 5 | 5 |
| RAM and flash (4) | 5 | 4 | 2 | 2 | 5 |
| Ease of setup (3) | 5 | 2 | 3 | 2 | 5 |
| Own certificate later (3) | 0 | 0 | 5 | 5 | 0 |
| PC test and fuzzing (3) | 4 | 3 | 4 | 4 | 4 |
| Code to maintain (2) | 5 | 3 | 3 | 4 | 5 |
| **Weighted sum (max 120)** | 77 | 51 | 95 | 94 | 77 |

A and E pass only if the LAN is trusted, which the owner has ruled out. Scores are my judgement, not measurements; the RAM row is the least certain.

## Decision
Choose **C**: plain HTTP only inside the provisioning access point, TLS with a device-generated EC P-256 key on the LAN, pinned by fingerprint.
It is the only low-cost option that keeps the password and token off the LAN without needing a clock, and it keeps the door open for company certificates (SYS-035).
D scores almost the same (94 vs 95), and is the fallback if the two-mode test matrix proves too costly.

Details fixed by this decision:
1. The self-created certificate has a validity of 2000-01-01 to 2049-12-31 because no clock exists at creation. Both dates fit the ASN.1 UTCTime type, which avoids parser problems with year 9999 (RV-001, finding 14). Trust comes from pinning the key, not from dates. SYS-031 (no valid time, no certificate accepted) applies to outgoing connections only, not to the device's own certificate.
2. The key pair is created at first start and after factory reset (SYS-034), only after the hardware random generator is shown to be seeded (on the ESP32-C3 this normally needs the radio on; spike 7.1). Key and certificate are written as one record with a checksum; on a bad record the device creates a new pair (power cut during the write, RV-001 finding 20). The private key is never exported through a network or user interface; a flash dump through USB is possible on prototypes (no fuses, ADR-0007).
3. The fingerprint is shown in the access point page (a channel protected by WPA2) and in the LAN interface. The manual tells the user to compare the browser's fingerprint
   with the one from the access point page. Without that comparison, first contact on the LAN is trust-on-first-use.
4. A user-supplied certificate (SYS-035) is only accepted through the access point or the authenticated TLS interface, never over plain HTTP on the LAN.
5. The plain HTTP listener is bound to the access-point interface only. On the LAN interface, port 80 either is closed or answers with a redirect that carries no data.

## Consequences
- Positive: no password or token in clear on the LAN; a company CA can be used; no clock needed.
- **Negative / trade-offs accepted:** browser warning at first use (hurts NEED-016); two listeners and modes to test; RAM for TLS server plus client at once;
  Jenkins plug-ins other than curl-style scripts may need extra setup; the first LAN contact is trust-on-first-use unless the user compares fingerprints.
- New risks (to add to the risk register): RAM exhaustion with two TLS sessions; private key stored unencrypted in flash on prototypes (see ADR-0007 for protection later);
  weak random source at first start (key quality); a device that answers on port 80 on the LAN by mistake; certificate lifetime logic for user certificates without a clock.
- Requirements created or changed: SYS-034 and SYS-035 stay as drafted. SW-level requirements to be derived: listener binding per interface, key generation, fingerprint display,
  TLS session limit. SYS-004 and SYS-016 should be read as "over the transport of SYS-034" (wording check in the next requirements pass).

## Verification and revisit
- Spike 7.1: measure free RAM with a TLS server session and a TLS client session open, and the time to create a P-256 key on the ESP32-C3. Decision stands if at least the SYS-026 margin remains; if not, revisit toward B for push plus C for the web interface with a one-session limit.
- Test cases TC-034 and TC-035: plain request on LAN returns nothing, fingerprint equals served key, key not readable.
- Fuzz the HTTP/TLS request parser on the PC (SYS-025).
- Revisit when: ADR-0002 platform changes; Zephyr HTTP server drops or changes TLS support; an authority on trust (for example the CRA harmonised standard) requires something stronger.

## Critical review notes
Strongest objection: "A self-signed certificate that browsers warn about teaches users to click through warnings, so the TLS adds little real protection."
Answer: the protection is real against passive listening and replay, which is the stated threat on a shared LAN, and pinning (Jenkins) and the fingerprint comparison via the access
point give a working check against active attackers. The cost is the user experience; the manual and the company-certificate path (SYS-035) are the mitigation. The objection is
partly valid for active attackers when the user skips the comparison, and that residue is accepted.
A factory reset creates a new key and breaks the pin held by Jenkins. With push-only use and no liveness check (SYS-033, deferred) this is silent. The manual and the stale indication decision (RV-001, finding 1) must cover this.
Second objection: "Bind-by-interface may fail if the access point and the station run at once." To be checked in spike 7.1.
