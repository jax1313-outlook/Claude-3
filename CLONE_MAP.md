# CLONE_MAP.md

**Program:** Dispatch Recovery
**Document Type:** Clone Map — Recovered Artifact → Dispatch v0 Workflow Stage
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Purpose

Per the steering mission's closing instruction — *"Prefer recovered working patterns over new design. If a working portal/card/archive/scoring pattern exists, identify it before proposing replacement"* — this document maps every stage of the Hard Dispatch v0 workflow to the specific recovered artifact that already implements it, partially implements it, or has no recovered equivalent at all. Nothing here is a build instruction; it feeds `DISPATCH_V0_BUILD_PLAN.md`.

## 2. The target workflow (as specified in the steering mission)

```
SWEEP → FIT → ROUTE → SCORE → AVAILABLE LOADS → SANDBOX
                                                    ↓
                                    View Original Load / Send Interested Email /
                                    Call Broker / Compare Options
                                                    ↓
                                                DECISION → COMMIT → HOLD (grace period) → DELETE stale runner-ups

Winning load: ACTIVE LOAD → POD → INVOICE → PAYMENT → ARCHIVE
```

## 3. Stage-by-stage map

| v0 Stage | Closest recovered artifact | Coverage | Notes |
|---|---|---|---|
| **SWEEP** | `Dispatch/dispatch/acquisition.py`; `Dispatch/dispatch/models.py`'s `LOAD_SOURCES` enum (`direct`, `dat`, `truckstop`, `broker_call`, `email`, `referral`, `website`, `other`) | **Partial.** The source taxonomy already anticipates load-board sweeping (`dat`, `truckstop`), but no working adapter to an actual load-board API was found anywhere in the recovered material — `cin_lite/acquisition.py` and `hybrid_v1/hybrid/acquisition/` both sweep SAM.gov (government), not DAT/Truckstop.com. | Biggest genuine build gap. See `DISPATCH_V0_BUILD_PLAN.md` Phase 1. Doctrine requirement ("Load intake must begin with automated sweep/scrape/intake; manual entry/CSV only as fallback") has no working precedent to clone from — it must be built new, informed by the *pattern* (acquire → normalize → fallback-on-failure) common to every acquisition module found. |
| **FIT** | `Dispatch/dispatch/scoring.py` (`_HOME_BASE`, `_OPERATING_RADIUS_MILES`) | **Reusable as-is.** Home base and radius constants are already correct for this operation (Jacksonville, FL; 500mi). | No separate "fit" function exists yet — it's implicit in scoring. May want to split into an explicit fit/eligibility gate, mirroring how `hybrid_v1`'s SDVOSB build treats eligibility as "first-class, not buried in scoring" (`Hybrid/architecture/system_overview.md` principle 4) — a good pattern to borrow even though that codebase itself is out of scope. |
| **ROUTE** | `Dispatch/dispatch/scoring.py`'s `_KNOWN_DISTANCES` lookup table and `_lookup_distance()` | **Partial.** Covers ~20 fixed Southeast city pairs. No real routing API integration found anywhere in scope. | Fine for MVP within the known lane set; will need a real distance/routing service before geographic coverage grows. |
| **SCORE** | `Dispatch/dispatch/scoring.py` in full (position impact, return-home-required, tomorrow's-position-risk, HOS risk, route risk, economic-opportunity flag, deadhead miles, fuel estimate, 0–100 score) | **Directly reusable, near-verbatim.** | This is the single most complete, ready-to-clone piece of the entire recovery. It already implements Claude-3's `INTELLIGENCE_ANALYST.md` §5.1 concretely. |
| **AVAILABLE LOADS** (listing) | `Dispatch/portal/templates/queues.html`, `search.html`, `dispatch.html` | **Partial — UI shell exists**, backed by `dispatch_api.py`'s `list_loads` endpoint (filters by `status`). | Needs a dedicated "available/unassigned" filter and load-board-sourced records to actually populate it once SWEEP exists. |
| **SANDBOX** | `Dispatch/portal/models/sandbox.py` (JSON-backed staging store, `create_entry`, `update_scoring`, status lifecycle); `Dispatch/cin_lite/pending.py` (store/load/complete/list_pending pattern) | **Strong partial match, needs adaptation.** `sandbox.py`'s status list (OPEN, INTERESTED, PURSUE, WATCH, PASS, INQUIRY_DRAFTED, INQUIRY_SENT_MANUAL, PUBLISHER_REQUIRED, BOOKED, EXPIRED, CLOSED) already covers most of the "active working area, not storage" concept and most of the named SANDBOX actions conceptually (INTERESTED ≈ "Send Interested Email", the model already stores `card_data` and `intelligence`). | `PUBLISHER_REQUIRED` is SAM-flavored and should drop. "Call Broker" and "Compare Options" have no dedicated status or action hook yet — these read as UI-level actions logged against a sandbox entry, not new statuses, per the steering doctrine ("HOLD is not a card type... HOLD is a workflow state" — the same logic implies these are actions, not states). |
| **DECISION** | `Hold/contracts/queue_item.schema.json` + `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` Part 1.3 (open→in_review→approved/rejected/resolved; no-timer-transitions rule; full queue always visible; rejected items resolved-with-note, never deleted) | **Strong pattern match, wrong payload.** The queue mechanics are exactly right (this is precisely the discipline the steering mission's Decision Card needs) but built for IFTA/evidence exceptions. | Clone the *mechanics* (no auto-approve, always-visible queue, audit-on-every-transition), not the schema fields. |
| **COMMIT** | `Dispatch/dispatch/models.py`'s `LOAD_STATUSES` transition into `dispatched` | **Reusable.** | Straightforward state transition once DECISION produces an approved outcome. |
| **HOLD (grace period for runner-up loads)** | *No recovered equivalent found.* | **Gap.** `cin_lite/pending.py` has a `complete()` that deletes a pending record, but only on explicit human action — nothing in any recovered codebase implements a *timed* expiry. | Must be built new: a scheduled job or TTL field on sandbox/queue entries that (a) is distinct from SANDBOX per doctrine ("HOLD is not a card type... HOLD is a workflow state"), and (b) deletes rather than archives on expiry. |
| **DELETE stale runner-up loads** | *No recovered equivalent found.* | **Gap**, same as HOLD above. | The doctrine is explicit that this is a hard delete, not an archive move — worth double-checking against the "no worker deletes anything, ever" rule in `Hold/docs/governance/DISPATCH_BASE_CONSTITUTION_v1.md` hard gate, since that rule comes from an adjacent (not identical) governance lineage. Flagged in `OPEN_QUESTIONS_FOR_MIKE.md`. |
| **ACTIVE LOAD** | `Dispatch/dispatch/models.py`'s `LOAD_STATUSES` (`in_transit`, `at_delivery`, etc.), `portal/routes/dispatch_api.py` milestone endpoints | **Reusable as-is.** | |
| **POD** | `Dispatch/dispatch/models.py`'s `EVIDENCE_TYPES` (includes `pod`), `POD_STATUSES` (draft, complete, delivered), `dispatch_api.py` evidence endpoints; `portal/templates/rate_confirmation_print.html` | **Reusable as-is.** | |
| **INVOICE** | `Dispatch/dispatch/models.py`'s `SETTLEMENT_STATUSES` (draft, invoiced, paid, overdue, disputed, written_off), `portal/templates/billing.html` | **Reusable as-is.** | |
| **PAYMENT** | Same `SETTLEMENT_STATUSES`/`PAYMENT_METHODS` (check, ach, wire, factored, other) | **Reusable as-is.** | |
| **ARCHIVE** | `Dispatch/dispatch/models.py`'s `RETENTION_STATUSES` (active, archived, expired); `portal/models/archive.py`; `portal/templates/archive.html` | **Reusable as-is.** Note this is a genuinely different concept from HOLD's delete-on-expiry — Archive doctrine ("preserve-by-default... only through approved retention policy") matches Claude-3's `ARCHIVE_REVIEW_POLICY.md` closely. | |

## 4. Supporting/cross-cutting mappings

| v0 Concept | Recovered artifact | Notes |
|---|---|---|
| Card doctrine (Decision / Action / Awareness only) | Claude-3's 0–5 consequence-level cards (`DISPATCH_CONSTITUTION_v3.md` §17); `Hold`'s queue-item-to-card pattern | No recovered artifact implements the specific 3-type model from the steering mission. Needs a fresh mapping decision — see `OPEN_QUESTIONS_FOR_MIKE.md`. |
| Portal = Operations Cockpit | `Dispatch/portal/` (Flask, ~35 templates already built: `home.html`, `dispatch.html`, `dispatch_decision.html`, `dispatch_detail.html`, `brief.html`, `brokers.html`, `fleet.html`, `driver_pay.html`, `queues.html`, `exceptions.html`) | Largest single reusable UI asset in the entire recovery. Build v0's screens as additions to this app, not a new one, pending Mike's confirmation (see `OPEN_QUESTIONS_FOR_MIKE.md`). |
| "No shared live code with SAM" | `Dispatch/reconciliation/contracts.py`'s posture (mirrors shared contracts read-only, never writes back) | Good precedent for how a Dispatch-side module should relate to SAM-side data if any ever needs to be referenced: read-only view, never a shared runtime dependency. |
| Source remains system of record | `Dispatch/dispatch/models.py`'s evidence-linked records (every load/expense/exception carries source references) | Already the working pattern; nothing to change. |
