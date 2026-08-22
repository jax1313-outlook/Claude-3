# RECOVERY_REPORT.md

**Program:** Dispatch Recovery
**Document Type:** Recovery Report
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Mission Recap

The steering mission asked for a recovery mission over evidence located at `D:\DISPATCH_AND_SAM_RECOVERY`, treating Claude-3 as an active sandbox/staging workspace rather than production Dispatch. The sequence required was Inventory → Classification → Clone Map → Build Plan, with no implementation until recovery analysis is complete. This report documents what was actually recoverable and how, since the named local path was never directly reachable.

## 2. What Was and Wasn't Reachable

**Not reachable, ever, from this session:** the local path `D:\DISPATCH_AND_SAM_RECOVERY` and everything under it. This session runs in an isolated cloud container with no mount, network path, or credential that reaches a user's local Windows machine. This is a hard environment boundary, not a permission that could be granted.

**Reachable and used:**
1. **13 GitHub repositories** under the `jax1313-outlook` account, discovered via `list_repos` and cloned read-only. Several repo names (`Claude-2`, `Jules-2`, `Test-Grounds`, `Hold`, `Dispatch`) are the exact lane names described in `DISPATCH_REPO_MANIFEST_v3.md`'s promotion path, confirming they are the working instances of that pipeline, not unrelated repos.
2. **A user-uploaded archive, `E-Ingestion.zip`** (21.5MB, ~600 files after extraction), which is a direct, if messy, export of a local folder structure — its own internal path strings (`C:\USERS\JAX13\ONEDRIVE - LEVEL 1 TRANSPORT INC (1)\COPILOT WORKSPACE\E-INGESTION\...`) confirm it is a real snapshot of the local recovery folder the mission originally pointed at, delivered through chat instead of live directory access.

Full detail on every artifact is in `SOURCE_ARTIFACT_INDEX.md`. This report focuses on findings and their implications.

## 3. Headline Finding: Two Separate Programs Share This History

The single biggest finding of this recovery is that the recovered material splits cleanly into **two different programs that have been developed together, under overlapping names, since the beginning**:

- **Dispatch** — freight load dispatching for Level 1 Transport, a Jacksonville, FL-based owner-operator. Doctrine lives in Claude-3 (and its siblings `Jules-3`, `Library`). Working code lives in the `Dispatch` GitHub repo: a load lifecycle model, a deterministic scoring engine, a Flask portal, and a REST API.
- **CIN / CIN-Lite / Hybrid / Micro-CIN / SDVOSB Contract Engine** — federal, state, and municipal government contract sourcing and pursuit for the same company, trading on its SDVOSB (Service-Disabled Veteran-Owned Small Business) status. This is the much larger body of recovered code: `cin_lite`, `hybrid_v1`, the `cin-hybrid` runtime, the Next.js `hybrid-operator` UI, and the `Micro-CIN`/"CIN-Tell" doctrine package.

The steering mission's own doctrine ("SAM separation... Do not build SAM workflows into Dispatch v0") anticipated exactly this split. What recovery adds is confirmation that the split is not hypothetical — it is how the actual email inbox is already organized (`02 Dispatch` = broker/load-board/rate-con traffic; `03 Contracts` = SAM/solicitation traffic; see `Email intake system.docx`), and it is the majority of the recovered codebase by volume. **Most of what was recovered is CIN/SDVOSB material and is not Dispatch v0 material.** See `SURVIVES_EVOLVES_RETIRES.md` for the full classification.

## 4. What Actually Exists for Freight Dispatch (the smaller, more valuable slice)

The `Dispatch` GitHub repo (pushed 2026-08-14, the most recent push of anything in scope) contains real, working freight-side code:

- `dispatch/models.py` — a complete load lifecycle: `LOAD_STATUSES` (created → dispatched → en_route_pickup → at_pickup → picked_up → in_transit → at_delivery → delivered → completed → archived → cancelled), `LOAD_SOURCES` (direct, dat, truckstop, broker_call, email, referral, website, other), milestone types, evidence types, exception types, and `SETTLEMENT_STATUSES` (draft → invoiced → paid → overdue → disputed → written_off).
- `dispatch/scoring.py` — a deterministic load-scoring engine already tuned to this operation: home base Jacksonville FL, 500-mile operating radius, $0.62/mile fuel cost, rate-per-mile floor/good/excellent thresholds, a Southeast city-distance lookup table, and computed outputs (position impact, return-home-required, tomorrow's-position-risk, HOS risk, route risk, economic-opportunity flag, deadhead miles, fuel estimate, 0–100 score). This is a working implementation of what `INTELLIGENCE_ANALYST.md` §5.1 in Claude-3 only describes abstractly.
- `portal/routes/dispatch_api.py` and `portal/models/sandbox.py` — a REST API and a sandbox staging model with an 11-value status enum (OPEN, INTERESTED, PURSUE, WATCH, PASS, INQUIRY_DRAFTED, INQUIRY_SENT_MANUAL, PUBLISHER_REQUIRED, BOOKED, EXPIRED, CLOSED) — already close in spirit to the mission's SANDBOX concept, though not identical to the workflow the steering mission specifies.
- `reconciliation/contracts.py` — deliberately conservative "canonical view" adapters that refuse to fabricate fields Dispatch's existing data can't support, citing the missing `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` by name. This is good practice already in place and worth preserving as a pattern.

None of this was built from the steering mission's Hard Dispatch v0 workflow (SWEEP→FIT→ROUTE→SCORE→AVAILABLE LOADS→SANDBOX→DECISION→COMMIT→HOLD→DELETE / ACTIVE LOAD→POD→INVOICE→PAYMENT→ARCHIVE) — it predates that workflow. But it maps onto most of it directly. See `CLONE_MAP.md`.

## 5. A Second, Unrelated Blueprint Was Found

`Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` is a complete, detailed, six-gate-validated build blueprint that Mike has apparently already begun approving (it carries `[MIKE APPROVES]` markers throughout). It is real and load-bearing — but its scope is **"Dispatch Workforce Core v1 — Matrix Group 1": IFTA fuel-tax preparation, expense/evidence records, a Manager decision queue, and a Reports layer.** It explicitly excludes Publisher, Intelligence, Accounting, and — naming it directly — "Dispatch Ops full build (first candidate for Matrix Group 2...)". That excluded Matrix Group 2 is precisely the freight load-dispatch system this recovery mission is chartered to plan. See `OPEN_QUESTIONS_FOR_MIKE.md` for why this matters before building starts.

## 6. Named Recovery Targets That Were Not Found

`L1-COS_Prototype_v1_3_2_GOLD`, the `NEVER MOVE` folder, `cin-hybrid.zip` under it, and `L2-v1 Prototype Development Rules_files` do not exist in any of the 13 GitHub repos or the uploaded archive. `TREE.txt`/`INVENTORY.csv`/`CODE_FILE_LIST.csv` were not found by those exact names, but functionally equivalent files (`repo_tree.txt`, `compare_all_files.txt`, `working_tree.txt`) were found inside the archive and used for this inventory. Full detail in `SOURCE_ARTIFACT_INDEX.md` §4.

## 7. What Was Deliberately Not Opened

Two Outlook `.pst` mail archives and one document that appears to be a server root password were found inside the uploaded archive. Neither was opened. Their existence is logged in `SOURCE_ARTIFACT_INDEX.md` §3.1 for Mike's awareness; opening them requires a separate, explicit instruction.

## 8. Recovery Value Assessment

High. Despite the local-drive gap, the combination of 13 GitHub repos and one large uploaded archive produced a coherent, cross-referenced picture: a governing doctrine lineage (Claude-3 and siblings), a working freight backend one repo away from what v0 needs (`Dispatch`), a large parallel government-contracting codebase that must be excluded from v0 scope, and an already-approved blueprint for an adjacent (not overlapping) build lane whose validation-gate pattern is worth reusing even though its content isn't. Nothing found required guessing or fabricating content — every claim in `SURVIVES_EVOLVES_RETIRES.md`, `CLONE_MAP.md`, and `DISPATCH_V0_BLUEPRINT.md` traces to a specific file cited in `SOURCE_ARTIFACT_INDEX.md`.

## 9. Authority Closing

This report is a recovery finding, not doctrine. It does not authorize deployment, code merge, or architecture change. Mike decides.
