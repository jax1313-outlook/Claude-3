# OPEN_QUESTIONS_FOR_MIKE.md

**Program:** Dispatch Recovery
**Document Type:** Decisions Required
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Purpose

Everything in `SURVIVES_EVOLVES_RETIRES.md`, `CLONE_MAP.md`, `DISPATCH_V0_BLUEPRINT.md`, and `DISPATCH_V0_BUILD_PLAN.md` that could not be resolved from recovered evidence alone is collected here as a direct question. No recommendation in this document is a decision. Nothing proceeds to implementation until these are answered.

## 2. Questions

### Q1 — Which repository is the base for Dispatch v0?
The `Dispatch` GitHub repo already contains a working load model (`dispatch/models.py`), a tuned scoring engine (`dispatch/scoring.py`), a REST API, and a ~35-template Flask portal — by far the most-developed freight codebase found in this recovery. Is this the sanctioned base to build v0 on top of, or should v0 start in a new, clean repository? Building on `Dispatch` silently would be an architecture decision this recovery mission is not authorized to make on its own.

### Q2 — Should Hold's Matrix Group process be adopted for a new "Matrix Group 2: Dispatch Ops"?
`Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` is a real, detailed blueprint you have apparently already begun approving (it carries `[MIKE APPROVES]` markers), scoped to IFTA/evidence/receipts/reports as "Matrix Group 1." It names "Dispatch Ops full build" as the explicit next candidate for "Matrix Group 2." Do you want Dispatch v0 built as that named Matrix Group 2, using the same six-gate validation process and lane structure — or is Dispatch v0 an entirely separate initiative from the Hold lineage?

### Q3 — HOLD grace-period duration
The steering mission specifies that runner-up loads enter a HOLD state after commitment and are deleted (not archived) on expiry, but gives no duration. No recovered doctrine or code specifies one either. How long should a runner-up load remain in HOLD before deletion — hours, or days?

### Q4 — Card-type reconciliation
Two non-identical card models exist in the recovered doctrine lineage: Claude-3's 0–5 consequence-level system (Silent Log / Status / Review / Decision / Conflict / Authority) versus the steering mission's 3-type model (Decision Card / Action Card / Awareness Card, with HOLD explicitly *not* a card type). `DISPATCH_V0_BLUEPRINT.md` §4 proposes a tentative mapping (levels 3–5 → Decision Card, level 2 → Action Card, levels 0–1 → Awareness Card) but this is a proposal, not a ruling. Which model governs Dispatch v0 — the 3-type model as stated, the 0–5 model, or the proposed mapping between them?

### Q5 — Is a hard-delete path acceptable for HOLD expiry?
Every other doctrine generation found in recovery treats deletion as forbidden or near-forbidden — most explicitly, `Hold/docs/governance/DISPATCH_BASE_CONSTITUTION_v1.md`'s hard gate: "No worker deletes anything, anywhere, ever." The steering mission's HOLD doctrine explicitly calls for deletion of stale runner-up loads. This is a direct tension between two governance lineages that recovery cannot resolve on its own. Do you want an explicit, written exception carved out for HOLD-expiry deletion specifically (and if so, should it still write an audit-log entry before the record is gone), or should "delete" here actually mean something softer (e.g., a hard-to-reach archive tier) despite the doctrine's wording?

### Q6 — Which load board(s) first for SWEEP?
No recovered code reaches an actual load board (DAT, Truckstop.com, or otherwise) — every acquisition module found targets SAM.gov, which is the wrong domain entirely. Which load board(s) should the first SWEEP adapter target, and are API credentials for it/them already available?

### Q7 — Are the `.pst` mail archives and the password document meant to be part of this recovery?
`Documents/backup.pst`, `jax1313@outlook.com.pst`, and `Hertzner Root Password.docx` were found inside the uploaded recovery archive and were deliberately not opened. Do you want them reviewed as part of this recovery effort, and if so, what's the safe process (e.g., should the password document be handled outside this session entirely, via a password manager, rather than read into a chat transcript)?

### Q8 — Are `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`, `TRI_DEPARTMENT_BUILD_RECEIPT_AND_QUALITY_AUDIT_v1.md`, and `07_DISPATCH_REPO_PLACEMENT_PLAN.md` genuinely lost, or do they exist somewhere not yet searched?
These are referenced by name — repeatedly and specifically — by `L2-intelligence-agent.`'s README and `KNOWN_GAPS.md`, but were not found in any of the 13 GitHub repos or the uploaded archive searched during this recovery. `Dispatch/reconciliation/contracts.py` implements what looks like a partial local mirror of the first one's `LibraryObject`/`LibraryCandidate` shapes, suggesting the original once existed somewhere. Is there another repository, local folder, or export not yet in scope for this recovery session?

### Q9 — Does `DISPATCH_FINAL_BLUEPRINT_v1.md` still need to be produced, separately from this recovery mission's deliverables?
Claude-3's own `README.md` states its mission is to produce `DISPATCH_FINAL_BLUEPRINT_v1.md`, covering the full end-to-end Dispatch program (not just v0's load workflow). That file still does not exist. `DISPATCH_V0_BLUEPRINT.md` produced in this recovery mission is explicitly scoped narrower (freight load-dispatch only) and is not a substitute for it. Should the final, full-program blueprint still be produced as a separate, later step — and if so, should it incorporate this recovery mission's findings, or supersede them?

## 3. How to answer

Each answer above becomes a version-stamped decision recorded against the relevant document (`SURVIVES_EVOLVES_RETIRES.md`, `CLONE_MAP.md`, `DISPATCH_V0_BLUEPRINT.md`, or `DISPATCH_V0_BUILD_PLAN.md`), not a silent edit — consistent with the recovered doctrine's own version-visibility rules (`DISPATCH_VERSION_DOCTRINE.md`). None of these documents should be treated as final until every question above has an explicit answer.

## 4. Authority Closing

This document asks questions. It does not answer them. No action is authorized by anything in this document alone. Mike decides.
