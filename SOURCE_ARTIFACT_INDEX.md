# SOURCE_ARTIFACT_INDEX.md

**Program:** Dispatch Recovery
**Document Type:** Source Artifact Index
**Status:** Recovery Working Document
**Authority:** Mike Zachary remains final authority

## 1. Purpose

This index catalogs every source location actually inspected during this recovery mission, what it contains, and how confident the inventory is. Nothing in this document is doctrine. It exists so the other six recovery documents can cite a specific artifact instead of a vague memory of one.

Two source classes were searched: GitHub repositories under `jax1313-outlook`, and a user-uploaded recovery archive (`E-Ingestion.zip`). The originally-referenced local path `D:\DISPATCH_AND_SAM_RECOVERY` was **never reachable** from this session — no local filesystem access exists in this environment. Everything below was either already on GitHub or arrived via the uploaded zip.

## 2. GitHub repositories (13 total)

| Repo | Visibility | Last push | Contents | Role |
|---|---|---|---|---|
| `Claude-3` | public | 2026-08-10 | This repo — 20 doctrine files, no code | Active recovery/staging workspace (this document lives here) |
| `Dispatch` | public | 2026-08-14 (newest) | `cin_lite/` (extended), new `dispatch/` package (models, scoring, services, store, db, notifications, acquisition), full Flask `portal/` (routes, models, ~35 templates), `reconciliation/` adapters + `contracts.py`, `sync/` engine, 7 IFTA/Archive phase walkthrough reports, ~100 test files | **Most advanced freight-side build.** Primary candidate base for Dispatch v0 |
| `Dispatch-Old` | public | 2026-08-12 | `cin_lite/` (earlier version), `Portal Deploy/` (nginx, systemd, certbot, DNS, deploy checklist), `Final_Architecture_for_Hybrid_CIN-Lite_System (1).docx`, `CONSTITUTION.md` (origin of "L1-COS"/"L2-COS" naming), `CURRENT_STATE.md`, `REPO_TO_DISPATCH_MAP.md` | Predecessor of `Dispatch`; CI badge shows it was originally named `cin-hybrid` |
| `L2-intelligence-agent.` | private (trailing dot in name) | 2026-08-11 | Numbered doctrine 01–08, legacy v1/v2 docs (`DISPATCH_CONSTITUTION_v2.md`, `DISPATCH_CONTEXT_MASTER_v2.md`, `MANAGER_DESCRIPTION_v2.md`, `DISPATCH_AGENT_GOVERNANCE_LAW_v1.md`), working `src/dispatch_intel/` (classifier/extractor/risk/routing pipeline + object-model layer), 33 passing tests, `MERGE_READINESS_REPORT.md`, `KNOWN_GAPS.md` | Doctrine-compliant Intelligence department rebuild; explicitly retires "L2-COS" terminology |
| `Publisher` | public | 2026-08-11 | Doctrine 02–08 + v1/v2 legacy, `src/dispatch_publisher/` (models, service, intelligence_client, library_client), tests, `MERGE_READINESS_REPORT.md` | Standalone Publisher department build |
| `Library` | public | 2026-08-11 | Same 20 doctrine files as Claude-3, plus 04/05 matrix files, `src/dispatch_library/` (ingestion, recipes, registry, resolver, service, taxonomy), tests | Standalone Library department build |
| `Jules-3` | public | 2026-08-10 | Identical 20-file set to Claude-3 | Parallel AI-reviewer doctrine snapshot (Round 2) |
| `Jules-2` | public | 2026-08-10 | Doctrine subset + `Jules.md` | Earlier reviewer snapshot |
| `Jules` | public | 2026-08-10 | `DISPATCH_CONSTITUTION_v2.md`, `DISPATCH_PROGRAM_MAP_AND_PROPOSAL.md` | Earliest Jules snapshot |
| `Claude-2` | public | 2026-08-10 | Doctrine set incl. both `DISPATCH_SPINE_SPECIFICATION_v1.md` and `DISPATCH_SPINE_SPEC_v1.md`, `DISPATCH_FINAL_ARCHITECTURE_STRESS_TEST_PROMPT.md` | Earlier Claude reviewer snapshot |
| `Claude` (original) | public | 2026-08-10 | `DISPATCH_CONSTITUTION_v2.md`, `DISPATCH_BUILD_PROPOSAL.md`, `DISPATCH_PROGRAM_MAP.md`, **`proposal/spine_prototype/`** (`state_registry.py`, `routing.py`, `event_log.py`, `validation.py`, `demo.py`) | Earliest Claude snapshot; contains the working Spine prototype the Decision Matrix KEEP-listed |
| `Test-Grounds` | public | 2026-08-08 | Numbered doctrine 02–08 + v1/v2 legacy (same set as `Publisher`) | Doctrine staging only, no code |
| `Hold` | public | 2026-08-05 | `docs/governance/` (per-subsystem constitutions: Base, IFTA, Librarian, Manager, Receipt, Memory Doctrine, Reports Charter), `docs/reference/` (`DISPATCH_BUILD_BLUEPRINT_v1.md` and 10 audit docs), `contracts/*.schema.json`, `docs/lanes/A–D`, `library_seed/`, `src/dispatch/` (evidence, ifta, queue, receipt, reports, common), golden-file tests | **Deepest, most mature repo.** Contains a complete, Mike-approved build blueprint — but for a different scope (see §5) |

## 3. Uploaded archive: `E-Ingestion.zip` (21.5MB, ~600 files after extraction)

Extracted to `E-Ingestion/`. Top-level structure and what each cluster contains:

| Path | Contents | Notes |
|---|---|---|
| `cin-hybrid-main/`, `Hybrid Calude/cin_lite/`, `WORKSPACE/WORKING_EXTRACT/`, `WORKSPACE/REPO_EXTRACT/`, `Repo.zip` (nested), `Hybrid-cin.zip` (nested) | Near-identical copies of the same "Hybrid CIN-Lite" Python codebase already on GitHub as `Dispatch-Old` | Redundant duplicates, not new evidence |
| `Hybrid Calude/cin-hybrid/` (also duplicated as `Hybrid-cin.zip/cin-hybrid/`) | `app.py`, `cli/hybrid_cli.py`, `core/{agents,intel,services,utils}/`, `runtime/{dispatcher.py, event_bus.py, state_manager.py}`, tests | A runtime orchestration layer over cin_lite — includes a literal `dispatcher.py`, but for the SDVOSB/contract pipeline, not freight |
| `Hybrid v1/hybrid_v1_codebase/hybrid_v1/` | Containerized rebuild: `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `hybrid/` package (`acquisition`, `archive`, `audit`, `config`, `control`, `data_model`, `events`, `integrations/{ai,portals,sam,smtp}`, `intelligence/{compliance,eligibility,partnering,pricing,risk}`, `normalization`, `proposal`, `routing`, `runtime`, `workflows`), `ci/deployment/hetzner-layout.md`, systemd units, `FILE_TREE.txt`, `MANIFEST.md`, `TEST_OUTPUT.txt` | The most mature single Python build in the whole corpus. Government-contract/SDVOSB domain, not freight |
| `Hybrid Calude/Hybrid/architecture/*.md` (7 files: `system_overview`, `module_map`, `build_sequence`, `landing_points`, `integration_points`, `dependencies`, `versioning_strategy`) | Full design doctrine for **"Hybrid (SDVOSB Contract Engine)"** — layered Intake→Eligibility→Intelligence→Decision→Generation→Execution pipeline, single-Intelligence-Owner pattern, human control gate, schema-freeze-at-Step-2 versioning discipline | Sophisticated, well-reasoned design. 100% government-contract scope (SDVOSB, VetCert, SAM.gov, DocuSign) |
| `nested_zips/hybrid-operator*/` (`hybrid-operator.zip`, `hybrid-operator-production-ready.zip`) | Next.js/TypeScript contract-review UI: `ContractList.tsx`, `ContractFlags.tsx`, `RiskPanel.tsx`, `ActionBar.tsx`, `ErrorMessage.tsx`, `LoadingState.tsx`, `pages/contract/[id].tsx`, `vercel.json`, Dockerfile | A third, JS-based implementation lineage — small, distinct tech stack, contract (not load) domain |
| `MicroCIN_Documentation_Package_v1_0.md` | Full engineering-grade doctrine for **"Micro-CIN"** (built by vendor "CIN-Tell" for Level 1 Transport): 5-agent pipeline (Portal Scanner → Contract Filter → Risk & Fit Evaluator → Dispatcher Liaison → Learning & Feedback), full JSON/YAML config, SOPs, Phase 1→2 roadmap, scoped to 7 Southeast states | Government/municipal contract intelligence, not freight load dispatching |
| `DETERMINISTIC CORE BUILD PLAN.docx` | Design spec that produced `hybrid_v1` | Confirms deterministic-first, AI-as-optional-enhancement principle |
| `Hybrid CIN-Lite Comprehensive Architecture Report.docx` | A prior AI session's own completion report for generating `hybrid_v1_codebase.zip` | Confirms `hybrid_v1` is a finished deliverable, not an abandoned draft |
| `FEMA On Boarding and Market Packet.docx` | "FEMA Region IV Entry Plan" — SDVOSB certification and SAM.gov registration steps for Level 1 Transport | Government-opportunity business development material |
| `Email intake system.docx` | Real, in-use inbox scheme for `cin-tell@l1truck.com`: folders `01 Intake`, **`02 Dispatch`** ("Broker, load boards, rate cons, route changes"), `03 Contracts` (SAM/solicitations), `04 VA/Gov`, `05 System`, `99 Archive` | **Real-world confirmation that "Dispatch" already means freight/broker/load-board traffic, and "Contracts" already means SAM/government, in actual daily use.** Names the n8n automation platform |
| `WORKSPACE/repo_tree.txt`, `compare_all_files.txt`, `working_tree.txt`, `changed_common_files.txt`, `repo_only_files.txt`, `working_only_files.txt` (also duplicated inside `consolidation_package.zip`) | Windows `tree` output and PowerShell `Compare-Object` output comparing a "REPO_EXTRACT" copy against a "WORKING_EXTRACT" copy | UTF-16 encoded; functions as the TREE.txt/INVENTORY equivalent originally requested. Confirms REPO_EXTRACT and WORKING_EXTRACT are near-identical — no material divergence found |
| `Screenshots/`, `Emails/`, `Exports/`, `Hold/` (inside the zip) | Empty directories | Contrary to the original mission brief, no recovered portal screenshots were actually present in this archive |
| `New Compressed (zipped) Folder.zip` | Confirmed empty (0 bytes of content) | Nothing to recover |

### 3.1 Flagged but deliberately NOT opened (sensitive)

- `Documents/backup.pst` and `jax1313@outlook.com.pst` — Outlook mail archives. Not parsed; personal/business correspondence.
- `Hybrid/Hertzner Root Password.docx` — appears to be a server credential document. Not opened.

These are noted for completeness only. Opening them requires an explicit, separate instruction from Mike.

## 4. Named items from the original mission brief that were NOT found anywhere in scope

- `L1-COS_Prototype_v1_3_2_GOLD` — no file, folder, or zip with this exact name exists in any of the 13 GitHub repos or the uploaded archive. `L1-COS` appears only as a named program in `Dispatch-Old/CONSTITUTION.md`'s scope line ("Applies To: L1-COS, SAM Sweeper, Dispatch/Load Board Sweeper, L2-COS Operations Portal, Publisher, Library, Archive, Operational Intelligence") — it is referenced as a sibling program, never as recovered code.
- `NEVER MOVE\cin-hybrid.zip` and `NEVER MOVE\L2-v1 Prototype Development Rules_files` — no "NEVER MOVE" folder exists in the uploaded archive or any repo.
- `TREE.txt`, `INVENTORY.csv`, `CODE_FILE_LIST.csv` (exact filenames) — not found by that name; the functional equivalents are the `WORKSPACE/*.txt` files in §3 above.
- `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`, `TRI_DEPARTMENT_BUILD_RECEIPT_AND_QUALITY_AUDIT_v1.md`, `07_DISPATCH_REPO_PLACEMENT_PLAN.md` — referenced repeatedly by `L2-intelligence-agent.`, but not present in Claude-3 or any of the other 12 repos searched by exact name. `Dispatch/reconciliation/contracts.py` explicitly implements a "local mirror" of `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`'s `LibraryObject`/`LibraryCandidate` shapes, which is the closest surviving trace of that file's content.

## 5. Two blueprints exist under similar names — do not confuse them

- **`DISPATCH_FINAL_BLUEPRINT_v1.md`** (referenced by `Claude-3/README.md` as this repo's stated deliverable) — **does not exist anywhere.** This recovery mission's own deliverables are not that file either; see `OPEN_QUESTIONS_FOR_MIKE.md`.
- **`Hold/docs/reference/DISPATCH_BUILD_BLUEPRINT_v1.md`** — a real, detailed, Mike-approval-drafted blueprint that **does exist**, but its scope is "Dispatch Workforce Core v1 — Matrix Group 1": IFTA, fuel/expense/evidence records, a Manager decision queue, and Reports. It explicitly excludes Publisher, Intelligence, Accounting, and — by name — "Dispatch Ops full build (first candidate for Matrix Group 2 — unblocks real mileage records, Cost Per Mile, and the Loads report)." **The freight load-dispatch workflow this recovery mission is chartered to plan is exactly the excluded "Matrix Group 2."**
