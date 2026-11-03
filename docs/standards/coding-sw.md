# Software Coding Standard (C / Zephyr)

- **Status:** Draft -- basis selection is recorded in `ADR-0001` (Proposed)

## 1. Basis
1. **SEI CERT C Coding Standard** -- primary security/reliability baseline (freely available; enforceable with clang-tidy `cert-*`).
2. **MISRA C:2012 (incl. Amendments 1-4)** / MISRA C:2023 -- safety/robustness rules. Apply the **subset adopted by the
   Zephyr project's coding guidelines** (Zephyr is *not* fully MISRA compliant), then tighten for project-owned code.
3. Zephyr's own coding style and guidelines for upstream-facing code and API usage.
Rule precedence on conflict: project deviation record > CERT > MISRA > Zephyr style, unless an ADR says otherwise.

## 2. Scope
- **Project code** (`sw/app`, `sw/drivers`, `sw/lib`): full compliance, no unrecorded deviations.
- **Zephyr and third-party modules:** not modified; not subject to rules, but findings that affect us are risk-assessed.
- Generated code: excluded only if listed with generator version.

## 3. Mandatory practices (beyond rule sets)
- C11 (or the Zephyr-supported dialect), `-Wall -Wextra -Werror`, `-Wconversion` where practical.
- Fixed-width integer types; no implicit narrowing; explicit units in names (`timeout_ms`).
- No dynamic allocation after init (prefer static, `k_mem_slab`, `k_heap` with proven bounds); stack sizes justified by measurement (`CONFIG_THREAD_ANALYZER`).
- Every return value checked (`cert-err33-c`); error handling defined per function (`-errno`/`int` convention).
- Bounded loops and recursion forbidden; ISR work minimal; shared data protected and documented.
- Assertions for programmer errors (`__ASSERT`), explicit handling for runtime faults; defined fail-safe state; watchdog configured (SYS-level requirement).
- Logging via Zephyr `LOG_*`; no `printk` in production paths; no secrets in logs.
- Device-tree/Kconfig as the single source of hardware configuration; no magic numbers.
- Every file/function traceable: header comment or commit references requirement IDs (`SW-nnn`).
- Doxygen comments on public APIs, including preconditions, units, thread/ISR safety.

## 4. Enforcement (automation = audit evidence)
| Tool | Purpose | Config |
|------|---------|--------|
| compiler warnings as errors | baseline | CMake |
| clang-tidy (`cert-*`, `bugprone-*`, `clang-analyzer-*`) | CERT checks | `sw/.clang-tidy` |
| cppcheck with MISRA addon (rule texts supplied locally) or commercial checker | MISRA compliance | to be decided in ADR-0001 |
| clang-format | style | `sw/.clang-format` (Zephyr) |
| Twister + native_sim unit tests, coverage (gcov) | verification | `sw/app/tests` |
| Sanitizers (ASan/UBSan on native_sim) | runtime defects | CI |

Static analysis results are retained as release evidence. A MISRA compliance report lists rules,
categories (Mandatory/Required/Advisory), deviations, and tool versions. **Do not claim MISRA compliance
without that report.**

## 4a. Cyber Resilience Act-driven practices (see `docs/regulatory/`)
Secure development lifecycle and CRA Annex I: secure-by-default configuration, no default/hard-coded credentials, minimal attack surface
(disable unused services/debug in production), authenticated + integrity-protected updates with rollback (MCUboot), secure boot where feasible,
input validation, data minimisation, logging of security events, secure data removal. Maintain an **SBOM per release** (`west spdx`, or CycloneDX),
track dependency vulnerabilities (Zephyr security advisories, CVE feeds), keep a coordinated vulnerability disclosure policy and the 24 h/72 h
reporting procedure *(verify)* in `docs/regulatory/technical-file/05-cybersecurity/`. Threat model per release (`docs/risk/`).

## 5. Review
Reviewers check against this document and the PR checklist. New suppressions (`// NOLINT`, `cppcheck-suppress`)
require an inline `DEV-nnn` reference.
