# SURVIVES_EVOLVES_RETIRES.md

**Program:** Dispatch Recovery
**Document Type:** Classification Register
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Definitions (as given in the steering mission)

- **SURVIVES** — still belongs in Dispatch, as-is or nearly as-is.
- **EVOLVES** — belongs in Dispatch but must be adapted before use.
- **RETIRES** — should not be carried forward.
- **REFERENCE** — useful historical context, not part of Dispatch v0.
- **NEEDS MIKE DECISION** — cannot classify without owner judgment.

Every entry cites the specific recovered artifact it is judged from (see `SOURCE_ARTIFACT_INDEX.md` for full paths). This is a working classification for planning purposes — it does not alter any existing constitution or doctrine on its own.

---

## 2. SURVIVES

| Item | Source | Rationale |
|---|---|---|
| Mike Zachary as final, non-transferable authority; "Dispatch thinks. Mike decides." | Claude-3 doctrine (universal); `Hold/docs/governance/DISPATCH_BASE_CONSTITUTION_v1.md` | Reaffirmed independently across every doctrine generation found, including the unrelated Hold/IFTA lineage. Zero conflicting evidence anywhere. |
| Portal as required Operations Cockpit | Claude-3 `PORTAL_DESCRIPTION.md`; `Dispatch/portal/` (real Flask app with `base.html`, `home.html`, `dispatch.html`) | Already partially built, not just doctrine. |
| Deterministic-first, cognition-only-where-needed split | Claude-3 doctrine; `Dispatch/dispatch/scoring.py` (pure deterministic, no LLM calls); Hold's IFTA/Reports lanes (explicit "arithmetic yes, domain judgment via LLM never recomputed") | Consistently implemented in every working codebase found, not just asserted in doctrine. |
| `dispatch/scoring.py`'s deterministic scoring engine (home base, radius, fuel cost, rate thresholds, distance lookup, 0–100 score, 6 risk flags) | `Dispatch/dispatch/scoring.py` | Working, tuned to the actual operation (Jacksonville, 500mi radius). Directly implements the SCORE stage of the v0 workflow. |
| `dispatch/models.py`'s load lifecycle enums (`LOAD_STATUSES`, `LOAD_SOURCES`, milestone/evidence/exception types, `SETTLEMENT_STATUSES`) | `Dispatch/dispatch/models.py` | Already covers ACTIVE LOAD → POD → INVOICE → PAYMENT → ARCHIVE almost field-for-field. |
| No autonomous booking, no autonomous legal commitment, no autonomous submission | Claude-3 Constitution; `Hold/docs/governance/DISPATCH_BASE_CONSTITUTION_v1.md` hard gate 3; steering mission doctrine | Named as a hard, non-negotiable rule in every governance generation found. |
| No 11-agent mesh; no Manager-as-probabilistic-router | Claude-3 `SUPERSESSION_MAP.md`, `ARCHITECTURAL_DISPOSITION.md`; `DISPATCH_DECISION_MATRIX.md` REJECT bucket | Explicitly retired in the doctrine lineage and never reappears in any later repo. |
| Source remains system of record; no fabrication ("Unknown means Unknown") | Claude-3 Constitution §10; `Dispatch/reconciliation/contracts.py` (refuses to invent fields it can't support, cites missing contract file explicitly rather than guessing) | Practiced, not just stated — `contracts.py` is a concrete example of a builder honoring this rule under real constraints. |
| Six-gate validation discipline (contract conformance, golden regression, boundary refusal, audit completeness, human walkthrough, docs-match-as-built) | `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` Part 5 | Proven, already Mike-approved for Matrix Group 1. Worth adopting for the Dispatch v0 build even though Group 1's content is out of scope. |
| Real-world Dispatch/SAM inbox separation (`02 Dispatch` vs `03 Contracts`) | `Email intake system.docx` | Independent, already-in-production confirmation of the SAM-separation doctrine the steering mission requires. |

## 3. EVOLVES

| Item | Source | Required adaptation |
|---|---|---|
| `portal/models/sandbox.py`'s 11-value status enum | `Dispatch/portal/models/sandbox.py` | Built for a merged SAM+Dispatch sandbox (statuses like `PUBLISHER_REQUIRED` are SAM-flavored). Needs to be narrowed to the freight-only SANDBOX doctrine: an active working area (not storage) feeding DECISION, with the specific actions named in the steering mission (View Original Load, Send Interested Email, Call Broker, Compare Options) as UI actions rather than status values. |
| `cin_lite/pending.py`'s staging-and-complete pattern (store full context, act on it later, then delete) | `Dispatch/cin_lite/pending.py` | The store/complete/list-pending shape is a reasonable pattern for SANDBOX and HOLD, but it was built for the email-checkbox contract pipeline, not loads. Needs re-pointing at load records and needs the HOLD-specific behavior (timed expiry → delete, not manual `complete()`) added — that doesn't exist in the source. |
| `reconciliation/contracts.py`'s canonical-view dataclasses | `Dispatch/reconciliation/contracts.py` | Good discipline, wrong object set — it mirrors `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`'s Library/Publisher/Archive objects, not a Sandbox/Hold/Decision/Action/Awareness card set. The pattern (read-only views, explicit "not enforced yet" flags) should survive; the specific dataclasses need new counterparts for the v0 workflow objects. |
| `L2-intelligence-agent.`'s object model (`IntelligenceFinding`, `PublisherRequirement`, `LibraryCandidate`, `ManagerDecisionSupportNote`) | `L2-intelligence-agent./src/dispatch_intel/{models,service}.py` | Well-designed and doctrine-compliant, but built for government-opportunity text classification (federal/FEMA/state/SAM domains, per its own `examples/` folders). The `service.py` pattern (route-only-when-actually-routed, never invent a requirement) is reusable; the domain content is not. |
| Claude-3's 0–5 Portal card consequence levels vs. the steering mission's 3-card-type doctrine (Decision/Action/Awareness) | Claude-3 `DISPATCH_CONSTITUTION_v3.md` §17; steering mission card doctrine | These are two different card models from two different doctrine generations and they do not obviously reconcile 1:1. This needs an explicit mapping decision before Portal UI work starts — flagged in `OPEN_QUESTIONS_FOR_MIKE.md`. |
| Hold's Manager decision/review queue (`queue_item` contract: open→in_review→approved/rejected/resolved, no-timer-transitions rule) | `Hold/contracts/queue_item.schema.json`; `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` Part 1.3 | The no-auto-approve, always-visible, resolved-never-deleted discipline is exactly right for DECISION-stage cards, but the queue was built for IFTA/evidence exceptions, not load decisions. Needs a Dispatch-flavored `payload_refs` shape. |
| `Dispatch/portal/routes/dispatch_api.py`'s REST surface | `Dispatch/portal/routes/dispatch_api.py` | Solid starting shape (loads, milestones, evidence, exceptions, POD, retention archive) but has no endpoints yet for SWEEP intake, SANDBOX actions, or HOLD/DELETE — those need to be added, not retrofit from something else. |

## 4. RETIRES (from Dispatch v0 scope specifically — not necessarily deleted from the account)

Per the steering mission: *"If a recovered component is government-opportunity specific, classify it as SAM or Reference, not Dispatch."* The following are retired **from Dispatch v0**, not judged as bad work — most of it is competent, some of it (`hybrid_v1`, the Hybrid architecture docs) is genuinely sophisticated. It simply belongs to the other program.

| Item | Source | Why it's out of v0 scope |
|---|---|---|
| `cin_lite` (all copies), `hybrid_v1`, `cin-hybrid` runtime (`dispatcher.py`, `event_bus.py`, `state_manager.py`) | `Dispatch-Old/cin_lite/`, `Dispatch/cin_lite/`, `E-Ingestion` zip (multiple copies) | Built around SAM.gov acquisition, 9 government-solicitation rule modules (set-aside, NAICS/SIN, past performance, pricing anomaly, vendor network, subcontractor dominance, JV/MP structure, foreign influence, cyber compliance). No freight/load concept anywhere in it. |
| "Hybrid (SDVOSB Contract Engine)" architecture (`system_overview.md`, `module_map.md`, `build_sequence.md`, `landing_points.md`, `integration_points.md`, `dependencies.md`, `versioning_strategy.md`) | `E-Ingestion/Hybrid Calude/Hybrid/architecture/` | Its own system-overview document names itself an SDVOSB contract-pursuit platform (SAM.gov intake, VetCert/CVE eligibility, DocuSign submission). Not adaptable to freight without replacing nearly every layer. |
| `hybrid-operator` Next.js UI (`ContractList.tsx`, `ContractFlags.tsx`, `RiskPanel.tsx`) | `E-Ingestion/nested_zips/hybrid-operator*/` | UI for reviewing government contract opportunities, not loads. Different tech stack (Next.js) from the rest of the Dispatch build (Flask). |
| `MicroCIN_Documentation_Package_v1_0.md` ("Micro-CIN" / "CIN-Tell", 5-agent SAM-scanning pipeline) | `E-Ingestion/MicroCIN_Documentation_Package_v1_0.md` | Explicitly a federal/state/county government-contract scanning system for 7 Southeast states. Zero freight content. |
| `FEMA On Boarding and Market Packet.docx` | `E-Ingestion/FEMA On Boarding and Market Packet.docx` | SDVOSB certification and FEMA disaster-response contracting steps. Pure government business development. |
| `Dispatcher Agent` as a cognitive role name; Refinement Analyst; Controlled Aggression as a permanent role; Research Scout as an internal Dispatch component | Claude-3 `SUPERSESSION_MAP.md`, `ARCHITECTURAL_DISPOSITION.md`, `DISPATCH_DECISION_MATRIX.md` REJECT bucket | Already retired in the doctrine lineage; recovery found nothing that revives the case for any of them. |

## 5. REFERENCE (SAM-side or historically informative, keep for context, don't build into v0)

| Item | Source | Reference value |
|---|---|---|
| `Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md` (IFTA / evidence / receipt / Manager queue / Reports) | `Hold` repo | Real, Mike-approved, adjacent build (named "Matrix Group 1"). Its **process discipline** (six validation gates, frozen contracts, lane structure) is worth reusing for v0 even though its content (fuel tax, receipts) is a different Matrix Group entirely. See `DISPATCH_V0_BUILD_PLAN.md`. |
| `Hold/docs/governance/` per-subsystem constitutions (`IFTA_CONSTITUTION_v1.md`, `RECEIPT_CONSTITUTION_v1.md`, `MANAGER_CONSTITUTION_v1.md`, `LIBRARIAN_CONSTITUTION_v1.md`, `MEMORY_DOCTRINE_v1.md`) | `Hold` repo | Model for how to write a per-worker constitution cleanly; not itself freight doctrine. |
| Email intake taxonomy (Type/Urgency/Owner/Action) | `Email intake system.docx` | Genuinely useful pattern for how incoming items get triaged; informs SWEEP/intake design even though the document itself is about email sorting, not load boards. |
| `Claude/proposal/spine_prototype/` (Spine prototype scaffold) | `Claude` repo | Historically the origin of the Dispatch Spine concept; Decision Matrix already KEEP-listed it as "useful proof of shape." Worth reading before designing v0's deterministic core, not worth cloning verbatim. |
| L1-COS/L2-COS naming and scope note in `Dispatch-Old/CONSTITUTION.md` | `Dispatch-Old/CONSTITUTION.md` line 6 | Only surviving textual definition of what L1-COS/L2-COS actually were (a family of programs: L1-COS, SAM Sweeper, Dispatch/Load Board Sweeper, L2-COS Operations Portal, Publisher, Library, Archive, Operational Intelligence). Useful for understanding lineage; nothing to clone. |

## 6. NEEDS MIKE DECISION

| Item | Why it can't be classified without Mike |
|---|---|
| Whether the `Dispatch` GitHub repo is the intended base to build v0 on top of, or whether v0 should start in a clean repository | It is by far the most-developed freight codebase found, but nobody has confirmed it's the sanctioned base. Building on it silently would be an architecture decision this recovery mission isn't authorized to make. |
| Whether Hold's Matrix Group 1 lane/gate process should be formally adopted for a new "Matrix Group 2: Dispatch Ops" build, as Hold's own blueprint suggests by name | This is Mike's call about program structure, not a technical question. |
| HOLD grace-period duration and the exact trigger for deleting stale runner-up loads | Not specified in any recovered doctrine or code. Steering mission says HOLD items "expire and are deleted, not archived" but gives no duration. |
| How to reconcile the 0–5 Portal card consequence-level model (Claude-3) with the 3-card-type doctrine (Decision/Action/Awareness) from the steering mission | Two different, non-identical card models exist in the lineage. Needs an explicit ruling, not an inferred mapping. |
| Whether the `.pst` mail archives and the Hertzner password document found in the recovery archive should be reviewed, and by what process | Sensitive material; not opened during this recovery. |
| Status of `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`, `TRI_DEPARTMENT_BUILD_RECEIPT_AND_QUALITY_AUDIT_v1.md`, `07_DISPATCH_REPO_PLACEMENT_PLAN.md` — genuinely lost, or do they exist somewhere not yet searched | Referenced by name across multiple repos but not found anywhere in the 13-repo + archive search performed. |

See `OPEN_QUESTIONS_FOR_MIKE.md` for these framed as direct questions.
