# Dispatch — Implementation Status

**What this file is:** a pointer, recorded in this repository so that someone reading its
documents knows where the working system actually lives and what it currently does.

**What this file is not:** a change to any document here. Nothing in this repository was
edited, superseded, retired or adopted by adding it. Every existing file is exactly as it
was.

| | |
|---|---|
| Recorded by | Claude Code |
| Date | 2026-08-24 |
| Implementation truth | [`jax1313-outlook/Dispatch`](https://github.com/jax1313-outlook/Dispatch) — `main` at `523ee32` |
| This repository holds | Specification and doctrine material only — 21 documents, no application code |
| Relationship to Dispatch | These documents are **source material**. Where one of them and the merged code disagree, the code is what runs; neither is automatically the authority on what *should* run. See "What is settled, and what is not" below. |

---

## What Dispatch now implements

Merged into `jax1313-outlook/Dispatch` `main` as **`523ee32`** (pull request #116, merged
2026-08-24), covering two authorized missions.

**Operational Readiness Mission (Tasks 1–4)**

| | |
|---|---|
| Dispatch Control Center | `dispatch.bat` plus a `dispatch_launcher/` control core. Eight controls — Start, Open Dispatch, Refresh Status, Settings, Version, Restart, Reset Session, Stop. It observes process state and configuration only; it never imports `dispatch.services`, `dispatch.store` or `dispatch.spine.*`, and a test enforces that boundary against a real interpreter. |
| Rehearsal mode | A `rehearsal_session` column on seven tables, tagged in the write path. A banner while a session runs, and a badge on the record that outlives it. Rehearsal records are excludable from operational queries and purgeable as a set; purging is gated and called by nothing. |
| Operational proof system | The twenty-step proof path with the exact action for each step, six readiness checks, and a report generator that structurally cannot print `REHEARSAL PASSED` without every step performed on a named machine. |
| Sandbox survey tooling | A deterministic, read-only inventory and classifier. Enforced in code: every input read is `open(..., "rb")`, one write choke-point, no move/rename/merge code path at all. |
| Connector boundary | Eight connector definitions, all reporting `UNCONFIGURED`; one mock reporting `SIMULATED` and deliberately not registered. Enforced at construction, statically by AST import-graph scan, and at runtime by a connection seal. |

**Repair, Connection, Security and Durability Campaign (Workstreams A–F)**

Dynamic Capacity truth and integration · Opportunity lifecycle alignment behind Spine ·
an operational deployment that refuses to start on a published default secret ·
backup and restore · token expiry and revocation · CSRF on every mutating route.

**Verification:** 3,655 tests passing on Python 3.11, 3.12 and 3.13; 0 failed, 0 skipped,
0 warnings; coverage 94.37% against a 90% gate.

## What is settled, and what is not

**Settled, and reflected in merged code:**

- **CF-04** — Dispatch Spine is the authoritative lifecycle engine and single source of
  lifecycle truth. Opportunity recommends; the human decides; Spine records reality.
  Opportunity's competing state list and transition table were removed, and a structural
  test fails if either reappears.
- **Outlook is the single source of scheduling truth.** Dispatch creates no calendar event.
- **Dispatch is not an ELD.** It holds no duty-clock data and has no telematics or GPS feed.
  Fourteen places that stated or implied otherwise were corrected.
- **No Mike attribution is manufactured anywhere.** Rehearsal sessions require an explicit
  actor and refuse reserved system identities; every proof step defaults to `not performed`.

**Not settled — and this document does not settle it:**

- The **Constitution v3 document stack in this repository is explicitly NOT ADOPTED.**
  `DISPATCH_DEPLOYMENT_BLUEPRINT.md` §18 records the instruction verbatim: this stack
  *"uses different vocabulary than what's already locked in real Dispatch … that document
  stack is explicitly out of scope here and not adopted."* The doctrine Dispatch's code
  actually follows has never been in any repository's `main`.
- Whether any of that material should be adopted, amended or retired is a decision for
  Mike Zachary. **Nothing here changes its status.**

## What has not been proven

Everything above is `IMPLEMENTED` — the code exists and the tests pass. **Nothing is
`OPERATIONALLY PROVEN`.** As of this commit the launcher has never started a Windows
process, no load has moved through a running portal on Mike's machine, and
`D:\Sandbox\Play Pen` has never been read. The two proof documents in Dispatch carry
`UNVERIFIED` on every acceptance item and say so on their first line by construction.

Repository test results are evidence of software behaviour. They are not operational proof
and are not cited as such.

## A note on duplication

Every document in this repository also exists byte-identically in `jax1313-outlook/Jules`
and in the `Library` repository. Three copies, no mechanism keeping them in sync. That is
worth knowing before editing any of them here: an edit made in one place does not reach
the other two, and there is currently nothing that would report the divergence.

---

*Nothing in this document is accepted doctrine or a Mike decision. It records where the
implementation is and what it does, and changes the status of nothing.*
