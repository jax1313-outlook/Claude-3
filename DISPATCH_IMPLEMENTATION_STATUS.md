# Dispatch — Implementation Status

**What this file is:** a pointer, recorded in this repository so that someone reading its
documents knows where the working system actually lives and what it currently does.

**What this file is not:** a change to any document here. Nothing in this repository was
edited, superseded, retired or adopted by adding it or by updating it. Every existing file is
exactly as it was.

| | |
|---|---|
| Recorded by | Claude Code |
| Date | 2026-08-29 (supersedes the 2026-08-24 version of this file) |
| Implementation truth | [`jax1313-outlook/Dispatch`](https://github.com/jax1313-outlook/Dispatch) — `main` at `4a572dc` |
| This repository holds | Specification and doctrine material only — 29 documents, no application code |
| Relationship to Dispatch | These documents are **source material**. Where one of them and the merged code disagree, the code is what runs; neither is automatically the authority on what *should* run. See "What is settled, and what is not" below. |

---

## What changed since this file was last written

The previous version of this note was recorded on 2026-08-24 against Dispatch `main` at
`523ee32`, and it ended by saying that the launcher had never started a Windows process.

**That is no longer true. Dispatch runs on Mike Zachary's Windows laptop.** He double-clicks a
file, chooses a PIN, signs in, and the portal renders. Five pull requests carried it there.

| PR | |
|---|---|
| **#117** | Repository context reconciled — `CLAUDE.md` rewritten as a cold-start brief, six missing context documents created, five standing doctrines recorded, 43 drift tests added. Plus the launch path: `DISPATCH_START_HERE.cmd`. |
| **#118** | First-run PIN setup and a Reset PIN control. Before this there was **no way to sign in at all**. |
| **#119** | A crash page that names what broke and where the log is. Before this every exception fell through to Flask's bare page, which does not mention that a log exists. |
| **#120** | The auto-interest email recorded as an exception to *"score does not decide"*. |
| **#121** | Two launcher windows that closed and took their message with them, fixed; plus the status report and Completion Blueprint v2. |

**Four defects were found, all by Mike simply trying to use the program.** None would have
surfaced from testing — a Linux container cannot report what Windows does.

1. The launcher could not be found. 82 entries in the folder; Windows hides extensions, so
   `dispatch.bat` and the `dispatch` *folder* displayed under the same name, folder first.
2. There was no way to sign in. No PIN existed, and the only way to create one was a Command
   Prompt command that was not installed.
3. A crashed page said nothing.
4. Two windows closed before their message could be read.

A fifth failure took a whole day: every page behind the login returned HTTP 500 for seven
hours. The cause was **not** a damaged database and **not** a missing drive — Mike had three
copies of Dispatch, and the one holding port 8080 had an incomplete extraction missing
`dispatch\connectors` entirely. The diagnosis took four wrong turns, recorded in
`DECISION_LOG.md` 2026-08-25 rather than tidied away, because the log file had named the
module, the file and the line since 11:20 that morning while every theory was being built
without reading it.

---

## What Dispatch now implements

Everything in the previous version of this note still holds — the Control Center, rehearsal
mode, the twenty-step proof system, the sandbox survey tooling, the connector boundary, and
the A–F repair campaign. Added since:

| | |
|---|---|
| A findable launch path | `DISPATCH_START_HERE.cmd`, a Desktop shortcut created on first run, and `docs/readiness/LAUNCH_PATH.md` recording why that file and not `dispatch.bat`. |
| First-run identity | A PIN chosen in the launcher window on first start, idempotent, stored as a scrypt hash and never in plaintext. A Reset PIN control for recovery. |
| An honest crash page | `portal/errors.py` — names the failure, redacts anything that looks like a secret, gives the log path, and recognises known conditions such as a damaged database with the steps to fix them. |
| Repository context | `CLAUDE.md` as a cold-start brief, plus architecture, governance, operator, maintenance, operational-proof and known-limitations documents. |
| Drift tests | `tests/test_repository_doctrine.py` — 43 tests that fail if the doctrine and the code diverge. One of them found a real defect: `create_app()` failed outright when the Route Risk plug-in was absent, violating *degradation is permitted, incapacity is not*. |

**Verification, on the merged content of `main`:** **3,822 tests passing** on Python 3.11, 3.12
and 3.13; 0 failed, 0 skipped, 0 warnings; gated coverage **94.80%** against a 90% floor.
*(Figures read from the CI job log of the run that gated the merge, not from memory.)*

---

## What is settled, and what is not

**Settled, and reflected in merged code** — unchanged from the previous version of this note:

- **CF-04** — Dispatch Spine is the authoritative lifecycle engine and single source of
  lifecycle truth. Opportunity recommends; the human decides; Spine records reality.
- **Outlook is the single source of scheduling truth.** Dispatch creates no calendar event.
- **Dispatch is not an ELD.** It holds no duty-clock data and has no telematics or GPS feed.
- **No Mike attribution is manufactured anywhere.** Every proof step defaults to
  `not performed`.

**Recorded since, and now standing doctrine in Dispatch** (`DECISION_LOG.md` 2026-08-25):

- **General Contractor Doctrine** — Dispatch is the General Contractor, System of Record and
  Operational Authority; it coordinates rather than rebuilding external wheels, and it
  **remains complete and operational without optional plug-ins**.
- **Plug-In Separation** — Route Risk, Mission Visibility, SAM and Assistant are plug-ins.
  Degradation is permitted; incapacity is not. No direct Dispatch write authority is granted
  to Assistant.
- **No Manager** — there is no Manager component. `MANAGER.md` **in this repository** is the
  record of a capability that was named in planning and never built. It authorises no code,
  no route, no data model and no runtime behaviour.
- **Repository Doctrine** and the **Repository Handoff Rule** — the repository, not
  conversation history, is the source of truth.

**Not settled — and this document does not settle it:**

- The **Constitution v3 document stack in this repository is explicitly NOT ADOPTED.**
  `DISPATCH_DEPLOYMENT_BLUEPRINT.md` §18 records the instruction verbatim: this stack
  *"uses different vocabulary than what's already locked in real Dispatch … that document
  stack is explicitly out of scope here and not adopted."*
- **Where that citation actually lives, checked 2026-08-29.** The previous version of this note
  cited §18 without saying where to find it, and it is **not in this repository's `main`, not in
  Jules, and not in Dispatch.** It is on an unmerged branch of `jax1313-outlook/Claude-3`:
  `claude/dispatch-jules-arch-review-i87dru`, at `DISPATCH_DEPLOYMENT_BLUEPRINT.md` line 494.
  The section is headed *"Jules Sandbox Discovery Report — NOT AUTHORITATIVE, reference only"*.
  The quotation is accurate; the pointer to it was missing, and is supplied here so the next
  reader does not have to hunt for it. **That the governing instruction sits on an unmerged
  branch is itself unresolved, and this note does not resolve it.**
- Whether any of that material should be adopted, amended or retired is a decision for
  Mike Zachary. **Nothing here changes its status.**

---

## What has been observed, and what has not been proven

This is the section that changed most, and it needs stating carefully, because it is now
possible to overclaim in a way it was not before.

**Observed on the target machine**, by Mike, on 2026-08-25 and 2026-08-26: launch from a
double-click; Python resolution (3.14 — outside the 3.11–3.13 the suite covers); Flask
present; idempotent first-run setup; PIN creation and sign-in; start with a real process ID;
a second start refused by process identity; the Desktop shortcut; the browser opening; and
the portal rendering every page tried.

**Not proven, and not close:**

- **Dispatch has done no freight work.** Zero loads, zero drivers, zero equipment. The
  completion gate in `CLAUDE.md` §2 — *he uses it to run a load and gets paid* — is not met.
- **The fifteen first-start acceptance items remain `UNVERIFIED`.** About half now have real
  observations behind them; none is recorded in the form the template requires. The one that
  matters most — Reset Session **refusing** while Dispatch is running — is untouched.
- **Every external system is `UNCONFIGURED`.** No ELD, GPS, traffic, weather, load board,
  mapping, accounting, scanner or Outlook client is connected.

Repository test results are evidence of software behaviour. They are not operational proof
and are not cited as such. **The suite found none of the four Windows defects above, and
could not have.**

---

## What is open, in Dispatch, awaiting Mike

From `docs/readiness/COMPLETION_BLUEPRINT_v2.md`, Stage A — every item is currently between
Mike and using the program:

| | | |
|---|---|---|
| **BLOCK-01** | Label the sample data | `/home` renders freight cards with a lane, a rate and a broker while `ACTIVE LOADS` reads **0**. The four entries in `sandbox.json` are bundled samples and nothing on screen says so — `CLAUDE.md` §6: *never represent sample data as live data.* **Mike's decision required first:** label them, or ship with none. |
| **BLOCK-02** | Record the fifteen acceptance items | **Only Mike can produce this.** |
| **BLOCK-03** | Home screen layout | Mike's own first observation — some items belong on a second screen. Blocked on his answer. |
| **BLOCK-04** | One copy of Dispatch | Three copies existed and the broken one ran for seven hours. Each copy carries its own database. |
---

## A note on duplication

**Checked, 2026-08-29:** 21 of the 29 documents in this repository are **byte-identical** to
their namesakes in `jax1313-outlook/Jules`. Seven exist only here (`CLONE_MAP.md`,
`DISPATCH_V0_BLUEPRINT.md`, `DISPATCH_V0_BUILD_PLAN.md`, `OPEN_QUESTIONS_FOR_MIKE.md`,
`RECOVERY_REPORT.md`, `SOURCE_ARTIFACT_INDEX.md`, `SURVIVES_EVOLVES_RETIRES.md`); two exist
only in Jules (`DEPLOYMENT.md`, `PORTAL_WIRING.md`). This file is the one document
deliberately different in each.

There is **no mechanism keeping the copies in sync**. An edit made here does not reach Jules,
and nothing reports the divergence.

The earlier version of this note also claimed these documents exist byte-identically in a
`Library` repository. That claim is **`UNVERIFIED`** — `Library` is not reachable from the
session that wrote this line, so it was neither confirmed nor contradicted, and it is recorded
here as unchecked rather than repeated as fact.

---

*Nothing in this document is accepted doctrine or a Mike decision. It records where the
implementation is and what it does, and changes the status of nothing.*
