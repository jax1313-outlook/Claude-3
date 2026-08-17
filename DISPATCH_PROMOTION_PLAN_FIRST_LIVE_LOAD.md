# DISPATCH_PROMOTION_PLAN_FIRST_LIVE_LOAD.md

**This is a plan, not an action.** No file in `jax1313-outlook/Dispatch` was read for writing, staged, or modified to produce this document. Every "target" cited below is from the earlier read-only architectural review of Dispatch's `main` branch. Nothing here has been executed.

**Goal:** move the First Live Load candidate (built clean-room in `jax1313-outlook/Claude-3`, branch `claude/dispatch-jules-arch-review-i87dru`) into Dispatch's existing codebase field-by-field and module-by-module — extending what's there, not replacing it.

---

## Promotion sequence (dependency order)

Later items depend on earlier ones landing first. Do not promote out of order.

1. Completion message template *(no dependencies, smallest, land first)*
2. Accounting handoff mock/interface *(no dependencies on Dispatch code, only on Completion Packet's call site — can land in parallel with #1)*
3. Trip Card *(depends on nothing new; adapts existing Dispatch objects)*
4. Completion Packet *(depends on Trip Card for BOL/POD evidence refs)*
5. Email Helper boundary *(depends on nothing new; wraps existing `dispatch/notifications.py`)*
6. HOLD 3-hour delete rule *(retention doctrine resolved, SAM/freight scoping built in Claude-3 and merged into Dispatch main via PR #88 — see item 4; the sibling/competing-candidates decision remains open)*
7. Communication Card *(depends on Library's real asset governance, Publisher's existing action vocabulary)*
8. Archive final record flow *(depends on Trip Card + Completion Packet being promoted)*
9. Operations Cockpit queue data *(depends on 3, 4, 6, 7 — promote last; it has nothing real to display before then)*

---

## 1. Trip Card

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/models.py` (`TripCard`, `TripCardItem`, `TripCardItemName`, `TripCardOverride`), `dispatch_build/trip_card.py` (`TripCardBoard`) |
| **Dispatch target** | `dispatch/models.py` (`MilestoneEvent`, `EvidenceItem`, `ExceptionNotice`); new file `dispatch/trip_card.py` |
| **Target exists?** | Partially — the underlying data (milestones, evidence, exceptions) exists; a checklist object with checkbox semantics does not |
| **Port / adapt / rename / merge / skip** | **ADAPT + MERGE.** Do not replace `MilestoneEvent`/`EvidenceItem` — they carry IFTA and rate-confirmation linkage Claude-3's build doesn't have. Add `dispatch/trip_card.py` as a view/gating layer that reads existing records and maps them onto the 7-item checklist (Arrival←`arrived_pickup`/`arrived_delivery`, Pickup←`loaded`/`departed_pickup`, BOL←`bol` evidence, Load Check←`checkpoint`, Delay←`delay` exception, Delivery←`delivered`, POD←`pod_received`+`PODPackage`). Port the `required` flag and `is_ready_to_close()` gating logic from Claude-3 as new functions operating on Dispatch's real enums — do not port Claude-3's simplified enum itself. |
| **Risks** | Two Dispatch milestone types can map to one checklist item (Arrival, Pickup) — needs an explicit "which instance completes the box" rule (recommend: latest by timestamp) or completion silently over/under-reports. Loads with milestones already recorded before this ships will retroactively show boxes as complete — fine for display, but do not let existing loads suddenly become Close-Load-gated without Mike opting in. Claude-3's `close_load()` gating must be composed with `archive_load()`, not swapped in over it. |
| **Required tests** | Mapping test: every Dispatch milestone/evidence/exception type resolves to exactly one checklist item, no silent drops. Gating test against a real `Load` fixture with partial milestones. Regression test: `archive_load()` behavior for existing callers is unchanged while Trip Card gating ships as opt-in. |
| **Dependencies** | `dispatch/models.py`, `dispatch/services.py` (existing milestone-recording functions) |
| **SAM/CIN contamination** | None — touches only `dispatch/` freight objects |
| **Manager touched** | No |
| **External systems** | N/A — internal state only |

---

## 2. Communication Card

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/models.py` (`CommunicationCard`, `CommunicationAction`, `CommunicationStatus`), `dispatch_build/publisher.py` (`create_communication_card`, `draft_communication`), `dispatch_build/store.py` (`send_communication`) |
| **Dispatch target** | New file `portal/models/communication_card.py`; consumes existing `portal/models/library.py`, `portal/models/publisher.py` |
| **Target exists?** | No — net-new object. Closest existing thing is Publisher's general `ACTION_TYPES` queue, which is a different concept, not a Communication Card |
| **Port / adapt / rename / merge / skip** | **PORT** the model and lifecycle largely as-is. **ADAPT** `draft_communication()` to call Dispatch's real `portal/models/library.py` (`get_available_company_assets()` / `get_missing_company_assets()`) instead of Claude-3's placeholder tuple, so the Onboarding Packet rule pulls real, approved company documents. |
| **Risks** | Dispatch's real Library has a human-vs-machine submission approval gate Claude-3's simplified version doesn't model — porting without it could let an unapproved document into a sent packet. Publisher's existing `ACTION_TYPES` overlaps conceptually with the five approved Communication Card actions (e.g. "Broker Packet Required" vs. "Broker Interest") — needs an explicit mapping so the two queues don't drift into duplicates. |
| **Required tests** | Onboarding Packet pulls real Library assets (not a mock). Communication Card cannot reach `DRAFT_READY` if a required Library asset is missing, mirroring `get_missing_company_assets()`. Lifecycle test ported directly from Claude-3. |
| **Dependencies** | `portal/models/library.py`, `portal/models/publisher.py`, `portal/models/identity.py` (for `requested_by` authorization — new requirement Claude-3's build didn't need) |
| **SAM/CIN contamination** | None if built under `portal/models/` and explicitly excludes GovCon-style action types from the five approved actions — this must not become a sixth home for the SAM bridge |
| **Manager touched** | No |
| **External systems** | Sends only through Email Helper (below); no direct Outlook call |

---

## 3. Completion Packet

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/models.py` (`CompletionPacket`), `dispatch_build/store.py` (`close_load()` assembly) |
| **Dispatch target** | `dispatch/services.py::archive_load()`, `dispatch/models.py::RetentionArchive` |
| **Target exists?** | Partially — `RetentionArchive` already bundles invoice/BOL/POD by content, just not as a standalone object created at Close Load time |
| **Port / adapt / rename / merge / skip** | **MERGE.** Do not stand up a second, independently-populated bundling object. Extend `archive_load()` so it derives a `CompletionPacket` view from the same data used to build `RetentionArchive`, in the same call. Do not rename `RetentionArchive` — its retention semantics are broader than "completion." |
| **Risks** | Two objects claiming to be "the" closed-load record will drift out of sync if populated independently rather than derived from one source in one call site. |
| **Required tests** | `CompletionPacket` fields are always a strict derivation of the `RetentionArchive` built in the same `archive_load()` call — no independent data-entry path. Regression test: existing `archive_load()` callers unaffected. |
| **Dependencies** | `dispatch/services.py::archive_load()`, `dispatch/models.py::RetentionArchive`, Trip Card (for BOL/POD evidence refs) |
| **SAM/CIN contamination** | None — stays inside `dispatch/`, does not touch `cin_lite/archive.py` |
| **Manager touched** | No |
| **External systems** | N/A internally; downstream consumers (Email Helper, Accounting) are adapter-based |

---

## 4. HOLD 3-hour delete rule

> **Sign-off status: RESOLVED.** See "HOLD sign-off log" below — this section was updated after Mike's ruling. Delete-on-expiry is confirmed as originally built; no code change was required. **Target architecture updated, current promotion unchanged** — see "Doctrine clarification: Sandbox is not one model long-term" below. The `source_type` filtering in this section is accepted as the correct bridge measure for promoting into today's still-shared Dispatch Sandbox; it is explicitly not the long-term design once Dispatch and SAM are physically separated.
>
> **MERGED.** With explicit confirmation to write to Dispatch (this plan's own "separate, future action requiring Mike's approval"), the filtering below was ported into the real `portal/models/sandbox.py` on branch `claude/sandbox-source-type-filtering-hold`, opened as [PR #88](https://github.com/jax1313-outlook/Dispatch/pull/88) (explicitly requested), watched through a green CI run across Python 3.11/3.12/3.13 with no review comments outstanding, and **squash-merged into `main`** at commit `48b953f`. Added: `get_all_for_source()`, `start_hold()`/`run_hold_sweep()` (freight-scoped by default, `HOLD_HOURS = 3`, deletes not archives), and two new entry fields (`hold_started_at`/`hold_expires_at`, default `None`) — additive only, no existing signature changed. 7 new tests shipped with it (`tests/test_sandbox_program_scoping.py`); the full existing Dispatch suite (~86 files) was re-run before the PR and passed clean. **Deliberately not ported:** the logic that decides which open entries count as "losing siblings" when one is booked — Dispatch's schema has no competing-candidates relationship between entries today, and inventing one was judged to be a real business-rule decision beyond "port the filtering," so `start_hold()` only does timer bookkeeping once a caller has already decided an entry is on HOLD. That decision is still open and is not resolved by this merge.

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/sandbox.py` (`run_hold_sweep`, `HOLD_HOURS`), `dispatch_build/models.py` (`SandboxStatus.RUNNER_UP`/`EXPIRED`) |
| **Dispatch target** | `portal/models/sandbox.py` (11-state lifecycle; `EXPIRED` exists as a static status only) |
| **Target exists?** | Partially — the status value exists, the timer and deletion behavior do not. The only place a literal `SANDBOX_HOLD_HOURS` constant exists anywhere is the abandoned, superseded `claude/l2-cos-dispatch-refactor` branch, and even there it never deletes |
| **Port / adapt / rename / merge / skip** | **ADAPT.** Port the sweep *logic* (start clock on commit, delete-not-archive at expiry) into `portal/models/sandbox.py`, wired to its real 11-state enum — do not port Claude-3's simplified 4-state enum. Scope the sweep to freight-sourced entries only (`sid` prefix pattern `SBX-DISPATCH-*`, per the existing `sid = f"SBX-{source_type}-{source_id}"` convention), unless Mike explicitly approves extending it to SAM entries. |
| **Risks** | (1) **Scoping now built and proven in Claude-3 (`dispatch_build/sandbox.py`, `dispatch_build/cockpit.py`), not yet ported into Dispatch.** Dispatch's Sandbox is shared infrastructure serving both SAM and freight opportunities — an unscoped sweep would silently delete SAM/contract sandbox entries, which is the exact contamination this plan exists to prevent. The Claude-3 build now filters on `source_type` at three points: commit side-effects (`Sandbox.siblings_of()` only turns same-program siblings into runner-ups), the HOLD sweep itself (`Sandbox.run_hold_sweep(source_type=...)`, defaults to freight, a caller must explicitly opt in to touch another program), and Cockpit read time (`build_cockpit_view()` never surfaces a non-freight entry). Promoting this into `portal/models/sandbox.py` means porting the same three filter points against its real 11-state enum, not just the concept. (2) **Resolved:** delete-without-archive does *not* conflict with the "nothing deleted without Mike approval" principle — see sign-off log. |
| **Required tests** | Ported and passing in Claude-3 (`tests/test_sandbox_program_scoping.py`, 5 tests): a foreign (non-freight) sandbox entry is never flipped to runner-up by a freight commit even when open in the same store; `commit_load()` refuses a non-freight sandbox id outright; the HOLD sweep never deletes a foreign entry even if forced into an expired-runner-up state (proving the filter doesn't just rely on "it can't get there"); Cockpit's `sandbox`/`decisions`/`awareness` queues never surface a foreign entry. The same five scenarios need re-proving against Dispatch's real Sandbox and Cockpit once ported — passing here demonstrates the pattern works, not that Dispatch's port is correct. |
| **Dependencies** | `portal/models/sandbox.py`, the existing `source_type` field for freight/SAM discrimination |
| **SAM/CIN contamination** | **Resolved in Dispatch itself.** Scoping mechanism proven in Claude-3, ported into `portal/models/sandbox.py`, and merged to `main` via [PR #88](https://github.com/jax1313-outlook/Dispatch/pull/88) — no longer a documented-but-unbuilt risk |
| **Manager touched** | No |
| **External systems** | N/A |

### HOLD sign-off log

- **First answer (retracted):** an initial sign-off request returned "Approve timer, not delete" — keep the 3-hour clock, change expiry from delete to a retained `EXPIRED` status. Before any code or doc changed to match it, the requester flagged this as a misclick ("stop" / "miss key no further") and withdrew it. No implementation work was done against this answer; it is recorded here only so the retraction is visible, not silently erased.
- **Governing ruling (current):** *"Sandbox is a Decision Workspace, not a Records Repository. Loads presented in HOLD are decision-support artifacts, not business records. A Dispatch record is created only by ingestion or Publisher creation. Therefore retention doctrine applicable to Library and Archive does not automatically apply to Sandbox objects. The HOLD system exists solely to provide a short operator decision window and may sweep stale candidates to prevent search stacking and cognitive overload."*
- **Effect:** this doesn't override the no-delete-without-Mike principle for a special case — it establishes that principle was never in scope for Sandbox/HOLD entries in the first place, since they aren't records. The apparent doctrine conflict flagged in the original architectural review is dissolved by this distinction, not overruled by it. `dispatch_build/sandbox.py`'s delete-on-expiry behavior, as originally built, is confirmed correct and requires no change.
- **What this ruling does not settle:** the SAM/freight scoping requirement for promoting HOLD into Dispatch's real, shared Sandbox model. That risk is independent of retention doctrine. It has since been scoped and built in Claude-3 (this section, above), ported into Dispatch, and merged via PR #88 (see the MERGED callout at the top of this section).

### Doctrine clarification: Sandbox is not one model long-term (accepted, changes the target architecture)

A further ruling arrived after the scoping work above landed, and changes what "promotion" is ultimately promoting *toward* — recorded verbatim, then reconciled against what's built:

> *"The original shared Sandbox assumption is no longer valid. Freight and SAM are being separated. They have materially different operational lifecycles. Freight Sandbox: short-duration decision workspace, HOLD/SWEEP behavior applies. SAM Sandbox: long-duration opportunity workspace, research and proposal workflow, HOLD behavior does not apply. Future architecture should assume separate physical Sandboxes rather than a shared model."*
>
> *"Dispatch and SAM have materially different missions, workflows, retention requirements, decision timelines, and operational behaviors. Dispatch = Freight. SAM = SAM. Future architecture should assume separation of Dispatch and SAM into separate physical programs. Sandbox behavior, retention rules, workflow states, and lifecycle management should be evaluated within the context of each program rather than through a shared-model assumption."*

**What this changes:** the target architecture is no longer "one shared Sandbox, filtered per-program at read/write time" (what item 4's scoping work assumes it's promoting into). It's "two Sandboxes, one per physically separate program, each with its own retention and lifecycle rules — Freight's short and HOLD-governed, SAM's long and research/proposal-governed, with no shared model to filter at all."

**What this does not change, and what was explicitly accepted:** *"Accept the source_type filtering and the five scoping tests as the immediate guardrail required for safe HOLD promotion into the current shared Dispatch codebase."* The filtering built in this section is confirmed as the correct **bridge** measure — Dispatch's real Sandbox is shared today, whatever the target architecture becomes, and HOLD cannot be promoted safely into that shared reality without it. It is explicitly not the destination:

- **Now → promotion into current Dispatch:** port the `source_type` filtering as built and tested here. This is still required and still correct.
- **Later → physical separation lands:** freight Sandbox code (HOLD, sweep, short-duration decision logic) moves into a freight-only Sandbox with no filtering, because there is no longer anything foreign to filter against. SAM's Sandbox becomes its own model, without HOLD, shaped around its actual long-duration research/proposal lifecycle instead of inheriting freight's timing assumptions. The `source_type` field and every filter built around it in this promotion plan become dead code at that point and should be retired, not carried forward as a permanent pattern.
- This plan promotes HOLD into today's shared reality only. It does not design, build, or schedule the physical separation — that is a separate future mission, out of scope here as much as SAM/CIN-Lite itself is (see program separation, throughout).

---

## 5. Email Helper boundary

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/email_helper.py` (`EmailHelper`, `Transport` protocol, `MockOutlookTransport`) |
| **Dispatch target** | `dispatch/notifications.py` (freight HMAC action-link emails) |
| **Target exists?** | Partially — sending capability exists, a shared interface does not |
| **Port / adapt / rename / merge / skip** | **ADAPT.** Introduce the `Transport` protocol and `EmailHelper` wrapper as a thin layer in front of `dispatch/notifications.py`'s existing sender. Do **not** touch `cin_lite/email_delivery.py` — that sender stays on the SAM side of the program boundary, untouched. |
| **Risks** | If one `EmailHelper` instance is pointed at both `dispatch/notifications.py` and `cin_lite/email_delivery.py` "for convenience," that recreates the exact cross-program bridge the earlier review flagged for removal. One instance per program, never a shared singleton. |
| **Required tests** | `EmailHelper` wraps the existing freight sender without changing observable behavior (same HMAC logic, same recipient rules). An explicit test or import-boundary check confirming no path connects the freight `EmailHelper` instance to `cin_lite`. |
| **Dependencies** | `dispatch/notifications.py` |
| **SAM/CIN contamination** | None, provided the one-instance-per-program rule is enforced and tested — at risk if it isn't |
| **Manager touched** | No |
| **External systems** | Adapter-based — `MockOutlookTransport` ports directly; live Outlook/Graph transport is a future swap, out of scope for this promotion |

---

## 6. Operations Cockpit queue data

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/cockpit.py` (`build_cockpit_view`) |
| **Dispatch target** | New file `portal/cockpit.py`; consumes `portal/routes/pages.py` and related handlers (currently fragmented, per Dispatch's own `docs/MANAGER.md`) |
| **Target exists?** | Label only ("Operations Cockpit" sidebar text); the fragmented views it should unify already exist separately |
| **Port / adapt / rename / merge / skip** | **ADAPT.** Port the six-queue *shape* as a new read-only aggregation function pulling from Dispatch's real `Load`, Trip Card, Sandbox, and Communication Card objects. Do not port Claude-3's in-memory `DispatchStore` traversal — the real queue-builder must query Dispatch's actual persistence layer. |
| **Risks** | Built before its four data sources are promoted, three of six queues would have nothing real to show — sequencing (see Promotion sequence above) is what prevents this. |
| **Required tests** | One test per queue, written **after** each data source lands, proving it reflects real Dispatch state, not Claude-3's mock objects. |
| **Dependencies** | Trip Card, Completion Packet, HOLD/Sandbox, Communication Card — promote this last |
| **SAM/CIN contamination** | Resolved in Claude-3's version — `build_cockpit_view()` filters every Sandbox-derived queue to `source_type == "dispatch"` before building `sandbox`, `decisions`, or `awareness`, proven by `test_cockpit_never_surfaces_a_foreign_sandbox_entry`. The promoted `portal/cockpit.py` must apply the same filter against Dispatch's real Sandbox — this is a port-and-retest, not open design work |
| **Manager touched** | No — presentation only, does not require Manager to route or prioritize anything |
| **External systems** | N/A — read-only aggregation |

---

## 7. Completion message template

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/library.py` (`TEMPLATES["completion_message"]`) |
| **Dispatch target** | `portal/models/library.py` |
| **Target exists?** | The storage mechanism doesn't formally exist yet — `library.py` currently models documents (`COMPANY_ASSETS`), not message templates. Small schema extension, not a new module |
| **Port / adapt / rename / merge / skip** | **PORT** the literal template text; **ADAPT** `library.py` to add a `TEMPLATES` table alongside `COMPANY_ASSETS`, under the same approval discipline already applied to documents |
| **Risks** | Lowest-risk item in this plan. Main risk is scope creep — this needs one string, not a templating engine |
| **Required tests** | Publisher's completion-message assembly (once ported) pulls this exact template and fails closed if it's missing, mirroring Claude-3's behavior |
| **Dependencies** | `portal/models/library.py`, Publisher (consuming call site) |
| **SAM/CIN contamination** | None |
| **Manager touched** | No |
| **External systems** | N/A |

---

## 8. Accounting handoff mock/interface

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/accounting.py` (`AccountingAdapter`, `AccountingHandoffReceipt`) |
| **Dispatch target** | New file `dispatch/accounting.py` |
| **Target exists?** | No — `DECISION_LOG.md` (Phase 4) records QuickBooks integration as an acknowledged placeholder; no code exists to merge against |
| **Port / adapt / rename / merge / skip** | **PORT** as-is — the most direct, lowest-adaptation item in this plan, since nothing conflicting exists in Dispatch |
| **Risks** | Low. Only risk is a future developer mistaking the mock for a real integration — the existing `mocked=True` flag on the receipt already guards against this |
| **Required tests** | Port Claude-3's test directly; add a test confirming `mocked=True` is always set until a real adapter is substituted |
| **Dependencies** | Completion Packet (the handoff call site) |
| **SAM/CIN contamination** | None |
| **Manager touched** | No |
| **External systems** | Explicitly mocked — that is the point of this component, and it stays that way through this promotion |

---

## 9. Archive final record flow

| | |
|---|---|
| **Claude-3 source** | `dispatch_build/archive.py` (`Archive.store`) |
| **Dispatch target** | `dispatch/services.py::archive_load()` |
| **Target exists?** | Yes, fully — a real, working, more mature archive engine already exists |
| **Port / adapt / rename / merge / skip** | **SKIP the Claude-3 `Archive` class entirely.** Do not promote it. Instead, extend `archive_load()`'s existing call site to attach the newly-promoted `CompletionPacket` to the record it already writes. |
| **Risks** | The temptation to promote a second archive engine because it's simpler is real — resist it. A duplicate source of truth here is higher-stakes than for Completion Packet, since Archive is the terminal, audit-relevant step. |
| **Required tests** | Regression test: existing `archive_load()` behavior and output shape unchanged except for the added `CompletionPacket` reference |
| **Dependencies** | `dispatch/services.py::archive_load()`, Completion Packet |
| **SAM/CIN contamination** | None — stays inside `dispatch/`'s own archive, does not touch `cin_lite/archive.py` |
| **Manager touched** | No |
| **External systems** | N/A |

---

## Cross-cutting summary

**SAM/CIN contamination** — Zero contamination by design in 7 of 9 components (Trip Card, Completion Packet, Email Helper, Completion message template, Accounting, Archive, and Communication Card provided its action set stays closed). **HOLD and Operations Cockpit are the two components that touch the shared Sandbox model** — both now have a working, tested freight-only filter in Claude-3 (`source_type` scoping at commit, sweep, and Cockpit read time; see item 4 and item 6), rather than only a documented intention. The remaining risk is narrower: the same filter has to be ported into `portal/models/sandbox.py` and `portal/cockpit.py` and re-proven against Dispatch's real, larger Sandbox — not designed from scratch. **This filtering is accepted as an interim bridge, not the target architecture** — Mike's later doctrine clarification (item 4) calls for Dispatch and SAM to eventually become separate physical programs with separate Sandboxes, at which point the `source_type` filter has no remaining purpose and should be retired rather than preserved as a permanent pattern.

**Manager** — Touched by none of the nine mandatory components. Nothing in this plan requires, reads from, or writes to `docs/MANAGER.md` or any `stage12/13-*` branch. Manager remains deferred through this entire promotion.

**External systems** — Every component that talks to an external system (Email Helper → Outlook, Accounting → QuickBooks-or-equivalent) stays adapter-based or mocked through this promotion. No live external integration is part of this plan; swapping a mock for a live transport is explicitly future work, out of scope here.

**What this plan does not do** — Every item except HOLD's SAM/freight scoping (item 4, merged via [PR #88](https://github.com/jax1313-outlook/Dispatch/pull/88)) remains untouched in `jax1313-outlook/Dispatch` — this plan does not execute the other eight components. It does not merge, extend, or otherwise interact with SAM/CIN-Lite. It does not resurrect Manager.

**Definition of done for this document**: satisfied — every mandatory component has a named Claude-3 source, a named Dispatch target, an existence check, a port/adapt/rename/merge/skip decision, risks, required tests, dependencies, and explicit SAM/Manager/external-system status. Execution against this plan is a separate, future action requiring Mike's approval.
