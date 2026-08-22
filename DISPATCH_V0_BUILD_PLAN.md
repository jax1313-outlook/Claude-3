# DISPATCH_V0_BUILD_PLAN.md

**Program:** Dispatch Recovery
**Document Type:** Build Plan (Draft — Not Approved, Not Authorized)
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Status of this document

This is a sequencing proposal, not an implementation authorization. Per the steering mission: "Do not skip to implementation." No line item in this plan may be built until Mike approves `DISPATCH_V0_BLUEPRINT.md` and resolves the items in `OPEN_QUESTIONS_FOR_MIKE.md`. This plan borrows its *process structure* (lanes, gates, frozen contracts) from `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md`, which Mike has already begun approving for a different, adjacent build (Matrix Group 1: IFTA/evidence/reports). Reusing a proven process is not the same as reusing that build's content, and this plan does not assume Mike has pre-approved anything about Dispatch v0 itself.

## 2. Recommended process model (borrowed pattern, not borrowed content)

Adopt Hold's six validation gates for every phase below, since they are already proven and already have Mike's approval language attached to a sibling build:

1. Contract conformance (schemas frozen before code, tested against fixtures).
2. Golden regression (a fixed, human-blessed test set that only grows, never shrinks).
3. Boundary refusal (negative tests proving the hard constraints actually hold — e.g., "no auto-approve config can exist" as a test, not just a sentence in a doc).
4. Audit completeness (every action produces a well-formed audit entry, sampled and verified).
5. Human walkthrough (Mike runs the lane end-to-end on real data and signs off in writing — no merge on green checks alone).
6. Docs match as-built (governing documents updated to reality; divergences resolved in the documents first).

Also adopt Hold's contract-freeze discipline: schemas for SANDBOX/DECISION/HOLD objects should land early and freeze, with any later change requiring an explicit version bump and same-day notice — mirroring `DISPATCH_BUILD_BLUEPRINT_v1.md` Part 1's "a frozen contract changes only by Mike's decision, a version bump, and same-day notice to every open lane."

## 3. Proposed phases

### Phase 0 — Contracts and repo decision
- Resolve `OPEN_QUESTIONS_FOR_MIKE.md` items on repo base and card-type mapping before any code is written.
- Freeze schemas for: the SANDBOX entry object (trimmed from `Dispatch/portal/models/sandbox.py`), the DECISION queue item (adapted from `Hold/contracts/queue_item.schema.json`'s shape), and the HOLD object (net new — no recovered precedent).
- **Blocked on:** Mike's approval of `DISPATCH_V0_BLUEPRINT.md`.

### Phase 1 — SWEEP (highest-risk, highest-value gap)
- Build load-board acquisition adapters. This is the one stage with no reusable recovered code — every acquisition module found in recovery (`cin_lite/acquisition.py`, `hybrid_v1/hybrid/acquisition/`) targets SAM.gov, not a load board.
- Manual entry / CSV import as fallback-and-test-only utilities, never the primary path (steering doctrine, restated).
- **Depends on:** Phase 0 contracts (canonical intake record shape).
- **Open question:** which load board(s) first, and API credential availability — see `OPEN_QUESTIONS_FOR_MIKE.md`.

### Phase 2 — FIT / ROUTE / SCORE
- Port `Dispatch/dispatch/scoring.py` forward with minimal changes; split FIT into an explicit pre-scoring gate per `DISPATCH_V0_BLUEPRINT.md` §3.2.
- Extend `_KNOWN_DISTANCES` or plug a real routing API for pairs outside the known lane set.
- **Depends on:** Phase 1 (needs real intake records to score against) — though the scoring module itself can be unit-tested against fixtures in parallel.
- **Golden regression set:** reuse or extend the pattern from `Hold`'s golden-quarter approach — a fixed set of real loads with Mike-blessed expected scores.

### Phase 3 — AVAILABLE LOADS + SANDBOX + Decision Card UI
- Extend `Dispatch/portal/`'s existing `queues.html`/`search.html` for the available-loads view.
- Adapt `Dispatch/portal/models/sandbox.py` per `CLONE_MAP.md`'s SANDBOX row (trim `PUBLISHER_REQUIRED`, add the four named actions as logged events, not statuses).
- Build the Decision Card UI on Hold's queue-item mechanics (no-timer transitions, always-visible queue, resolved-not-deleted).
- **Depends on:** Phase 0's frozen SANDBOX/DECISION schemas; Phase 2's scoring output as SANDBOX input.

### Phase 4 — COMMIT / HOLD / DELETE (net-new logic)
- COMMIT: straightforward `LOAD_STATUSES` transition, reusing `Dispatch/dispatch/models.py`.
- HOLD: new scheduled-expiry mechanism — no recovered precedent exists for this. Needs Mike's grace-period duration decision before the TTL logic can even be written (see `OPEN_QUESTIONS_FOR_MIKE.md`).
- DELETE: the hard-delete path executing HOLD's expiry. Given every other doctrine generation recovered treats deletion as near-forbidden ("no worker deletes anything, ever" — `Hold/docs/governance/DISPATCH_BASE_CONSTITUTION_v1.md`), this phase should not proceed without an explicit, written exception from Mike, logged the same way `Hold`'s blueprint logs `[MIKE APPROVES]` items.
- **Depends on:** Phase 3 (needs a real DECISION outcome to commit or hold against); Mike's ruling on HOLD duration.

### Phase 5 — ACTIVE LOAD → POD → INVOICE → PAYMENT → ARCHIVE
- Almost entirely a integration/wiring phase, not new design — `Dispatch/dispatch/models.py` and `Dispatch/portal/templates/{billing,archive,rate_confirmation_print}.html` already model every stage.
- **Depends on:** Phase 4 (a committed load is the entry point).

### Phase 6 — Portal cockpit polish
- Cards trigger attention, briefs support decisions, no alert spam (steering doctrine). Reuse `Dispatch/portal/templates/brief.html` and the existing base layout.
- Reconcile the card-type model per `OPEN_QUESTIONS_FOR_MIKE.md`'s ruling before finalizing card UI, since Phase 3's Decision Card work will need revisiting if the ruling changes the model.
- **Depends on:** all prior phases having real data to display.

## 4. What this plan does not include, by design

Matching Hold's own blueprint discipline of naming exclusions explicitly rather than leaving them ambiguous: this plan does not include SAM/government-opportunity workflows, IFTA/receipt/evidence processing (that is Hold's own Matrix Group 1, already separately approved), Publisher, Intelligence, or Accounting builds beyond the minimum v0 needs to move a load through its lifecycle. No coding prompts are written for any of those here, by design — matching the convention `DISPATCH_BUILD_BLUEPRINT_v1.md` itself uses in its own Part 6.

## 5. Sequencing rationale

Phase 1 (SWEEP) is placed first despite being the highest-risk, least-recovered stage, because every downstream phase (FIT/ROUTE/SCORE/SANDBOX/DECISION) is either fully or mostly already built and only needs real intake data to prove itself against — the fastest way to find out whether the recovered scoring and sandbox code actually holds up is to feed it real swept loads as early as possible, mirroring `DISPATCH_BUILD_BLUEPRINT_v1.md`'s own principle of building "integration adapters as leaf nodes so live wiring can proceed in parallel without blocking the core."

## 6. Authority Closing

This build plan does not authorize implementation. No lane may start without Mike's approval of the blueprint and resolution of the open questions. Mike decides.
