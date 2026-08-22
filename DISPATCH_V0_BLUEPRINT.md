# DISPATCH_V0_BLUEPRINT.md

**Program:** Dispatch Recovery
**Document Type:** Dispatch v0 Target Architecture (Draft — Not Approved)
**Status:** Recovery Working Document — every item below is a proposal, not law
**Authority:** Mike Zachary remains final authority

## 1. Status of this document

This is a **draft blueprint synthesized from recovered evidence**, not a replacement for `DISPATCH_FINAL_BLUEPRINT_v1.md` (which does not exist yet — see `RECOVERY_REPORT.md` §6) and not the same document as `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` (which is real, approved, but scoped to a different Matrix Group — IFTA/evidence/reports, not load dispatch; see `SOURCE_ARTIFACT_INDEX.md` §5). Nothing here is authorized for implementation. It exists to give Mike a single, concrete thing to approve, amend, or reject.

## 2. Scope

Dispatch v0 is the freight load-dispatch workflow only, per the steering mission's Hard Dispatch v0 workflow:

```
SWEEP → FIT → ROUTE → SCORE → AVAILABLE LOADS → SANDBOX
                                                    ↓
                                    View Original Load / Send Interested Email /
                                    Call Broker / Compare Options
                                                    ↓
                                                DECISION → COMMIT → HOLD (grace period) → DELETE stale runner-ups

Winning load: ACTIVE LOAD → POD → INVOICE → PAYMENT → ARCHIVE
```

**Explicitly out of scope for v0** (per steering doctrine): SAM/government-opportunity workflows, IFTA/fuel-tax/receipt processing (Hold's Matrix Group 1), Publisher, Intelligence, and Accounting builds beyond what v0 directly needs to move a load through its lifecycle.

## 3. Proposed architecture, stage by stage

### 3.1 SWEEP
Automated load intake as the required entry point; manual entry and CSV import exist only as fallback/test utilities (steering doctrine, restated). No recovered adapter reaches an actual load board — `Dispatch/dispatch/models.py`'s `LOAD_SOURCES` enum already names the intended sources (`dat`, `truckstop`, `broker_call`, `email`, `direct`, `referral`, `website`) but nothing sweeps them yet. Proposed shape: one acquisition module per source, each normalizing into the same canonical load-intake record, following the acquire→normalize→fallback-on-failure pattern already proven in every acquisition module found in recovery (`cin_lite/acquisition.py`, `hybrid_v1/hybrid/acquisition/`), even though those specific modules target the wrong domain (SAM.gov, not load boards).

### 3.2 FIT
A deterministic eligibility/fit gate using `Dispatch/dispatch/scoring.py`'s existing home-base and operating-radius constants. Proposal: split fit out as its own explicit step ahead of scoring (rather than buried inside the score, as it currently is) — this mirrors a principle from the recovered (but out-of-scope) SDVOSB architecture docs that eligibility should be "first-class, not a rule buried in scoring" (`E-Ingestion/Hybrid Calude/Hybrid/architecture/system_overview.md`), which is a sound structural idea independent of that codebase's domain.

### 3.3 ROUTE
Reuse `_KNOWN_DISTANCES`/`_lookup_distance()` from `Dispatch/dispatch/scoring.py` for the initial known-lane set; flag any origin/destination pair not in the table for manual estimate or a future routing-API integration, rather than silently guessing.

### 3.4 SCORE
Clone `Dispatch/dispatch/scoring.py` directly — it already produces exactly the fields v0 needs (position impact, return-home-required, tomorrow's-position-risk, HOS risk, route risk, economic-opportunity flag, deadhead miles, fuel estimate, 0–100 score), tuned to this operation's actual home base and cost structure.

### 3.5 AVAILABLE LOADS
An "unassigned/available" filtered view on top of the existing `dispatch_api.py` `list_loads` endpoint and the existing `queues.html`/`search.html` templates in `Dispatch/portal/`.

### 3.6 SANDBOX
An active working area (never storage — per doctrine, and per `README.md`'s own disclaimer that Claude-3 "is not... a sandbox" applies equally here: a sandbox is somewhere work happens, not somewhere it rests). Base this on `Dispatch/portal/models/sandbox.py`, trimmed of its SAM-flavored statuses (`PUBLISHER_REQUIRED`), with the four named actions (View Original Load, Send Interested Email, Call Broker, Compare Options) implemented as logged actions against a sandbox entry rather than as new status values, consistent with how the steering doctrine treats HOLD as a workflow state rather than a card type.

### 3.7 DECISION
One Decision Card per sandboxed load reaching a decision point, using the queue mechanics already proven in `Hold/contracts/queue_item.schema.json` and `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` Part 1.3: no status transition ever fires on a timer (silence is never consent), the full queue is always visible, every transition writes an audit entry, rejected items are resolved-with-note and never deleted. This is a process pattern worth cloning even though Hold's own payload (fuel/evidence records) is out of scope.

### 3.8 COMMIT
Transition the load's status to `dispatched` per the existing `LOAD_STATUSES` enum in `Dispatch/dispatch/models.py`.

### 3.9 HOLD
**No recovered precedent exists for this stage — it must be designed, not cloned.** Proposed shape: runner-up loads (sandboxed but not committed once a winner is chosen) enter a HOLD state with a Mike-approved grace-period TTL (duration is an open question — see `OPEN_QUESTIONS_FOR_MIKE.md`). On expiry, a scheduled process deletes the HOLD record — not archives it, per doctrine ("HOLD items expire and are deleted, not archived"). This is a genuine hard-delete path, which is unusual relative to the "nothing is ever deleted" posture found in the Hold repo's own (unrelated) governance doctrine — flagged explicitly for Mike rather than resolved silently.

### 3.10 DELETE stale runner-up loads
The execution of HOLD's expiry above. No audit-trail question here should be treated as settled without Mike's sign-off, since deletion is otherwise treated as forbidden everywhere else in every doctrine generation recovered.

### 3.11 Winning-load lifecycle: ACTIVE LOAD → POD → INVOICE → PAYMENT → ARCHIVE
Reuse directly. `Dispatch/dispatch/models.py` already models every stage: `LOAD_STATUSES` for ACTIVE LOAD progression, `EVIDENCE_TYPES`/`POD_STATUSES` for POD, `SETTLEMENT_STATUSES`/`PAYMENT_METHODS` for INVOICE and PAYMENT, `RETENTION_STATUSES` for ARCHIVE. `Dispatch/portal/` already has matching templates (`billing.html`, `archive.html`, `rate_confirmation_print.html`).

## 4. Card doctrine

Only three primary card types: **Decision Card**, **Action Card**, **Awareness Card**. HOLD is a workflow state, not a card type (steering doctrine, restated for emphasis since it is easy to conflate with the SANDBOX status-list pattern found in recovery).

No recovered artifact implements this exact three-type model — Claude-3's doctrine uses a 0–5 consequence-level system instead. **This is an open reconciliation question, not a resolved one** — see `OPEN_QUESTIONS_FOR_MIKE.md`. Proposed default, pending Mike's ruling: Decision Card = consequence levels 3–5 (Decision/Conflict/Authority collapsed into one type, distinguished by an internal severity field rather than a separate card type); Action Card = level 2 (Review, reframed as an action prompt); Awareness Card = levels 0–1 (Silent Log/Status). This is a proposal, not a decision.

## 5. Portal

Portal is the Operations Cockpit; a cockpit shows only what the operator needs; cards trigger attention; briefs support decisions (steering doctrine). `Dispatch/portal/` already contains a `brief.html` template and a working Flask app structure — propose building v0's screens into this existing app rather than starting a new one, pending Mike's confirmation this repo is the sanctioned base (see `OPEN_QUESTIONS_FOR_MIKE.md`).

## 6. Hard constraints carried forward unchanged

No 11-agent mesh. No Manager as probabilistic router. No autonomous booking. No autonomous legal commitment. No autonomous submission. No shared live code with SAM. Source remains system of record. No alert spam. These are restated from the steering mission and are not weakened, modified, or reinterpreted by anything in this blueprint.

## 7. What this blueprint deliberately excludes

Per the steering mission's SAM-separation instruction, and confirmed by the volume of recovered evidence: any load-board-vs-government-opportunity ambiguity should resolve toward the load-board (Dispatch) side only when the evidence is unambiguous (per `Email intake system.docx`'s real, already-in-production folder split). All CIN/CIN-Lite/Hybrid/Micro-CIN/SDVOSB material is excluded — see `SURVIVES_EVOLVES_RETIRES.md` §4. IFTA, receipts, evidence records, and the Manager decision-queue implementation from `Hold`'s Matrix Group 1 are excluded as content (their process pattern is reused, not their payload) — see §3.7 above and `CLONE_MAP.md`.

## 8. Authority Closing

This blueprint is a recommendation only. No architecture is authorized by this document alone. Mike decides.
