# DISPATCH_DEPLOYMENT_BLUEPRINT

Deployment-hardening pass against `jax1313-outlook/Dispatch` `main` @ `48b953f`. Four parallel investigative workstreams (config/credentials inventory, external-system/middleware boundary map, freight-core defect sweep, readiness matrix) plus direct implementation of the safe fixes and two adapter boundaries they surfaced. Every finding below is cited to a file; nothing is invented. No file in `main` was changed directly — all code lives on branches (listed in §9), none merged.

**Source note on §0:** `DISPATCH_DRIVER_FIRST_DOCTRINE.docx` was checked for in `Dispatch` and `Claude-3` (repo search + local clone) and does not exist in either. The doctrine content itself was supplied in full, verbatim, in the chat message that requested this update — that text is treated as authoritative project doctrine directly; no file needed to be located to act on it.

**Mode note:** This update is blueprint-only, per the doctrine message's own explicit instruction ("do not implement yet if still in blueprint mode... instead, update the blueprint, decision register, and first-live-load completion plan"). No application file in `Dispatch` was touched this pass — only this document and the Claude-3 copy of it.

---

## 0. Driver-First Doctrine (Constitutional — LOCKED)

Recorded as decision **D9** in §6; stated here because it governs how every other section in this document should be read, not just one line item in a register.

**Primary doctrine:** Dispatch is not office software adapted to a truck. Dispatch is truck-cab operational software with office functions behind it. The design center is the cab of the truck, not a desktop dispatch office — an owner/operator actively operating a commercial vehicle while freight is moving, not a dispatcher sitting behind a desk.

**The 70 MPH test, applied to every feature:** Mike is driving. The phone rings. Someone needs load information. Can Dispatch provide the answer within seconds? If not, redesign the feature.

**Design priorities this implies**, in order: fast retrieval over deep navigation; large obvious actions over complex menus; card workflows over multi-screen workflows; immediate operational support over administrative reporting; mobile use over desktop use; plain-language labels over technical labels; one-touch activation over buried functions; operational truth over software elegance.

**Governance rule this adds:** any proposed implementation that treats a driver-facing operational need as a secondary utility, a hidden admin feature, a report-only screen, or a future enhancement violates this doctrine. The design question is not "how does a dispatcher manage loads" — it's "how does Mike survive the bees while moving freight."

**Immediate consequence for this blueprint:** §6 reclassifies `PORTAL_INQUIRY_MODE` (D6) under this doctrine, and §10/§11 add the resulting feature — Load Search / Operational Retrieval — to the required first-live-load scope, not as an unresolved question anymore but as a scoped, not-yet-built requirement.

---

## 1. Closed Critical Gaps

Branch: `claude/freight-core-defect-fixes`. All fixes have dedicated tests (`tests/test_deployment_hardening_fixes.py`) plus a full-suite regression run (§8).

| # | Finding | Fix | File |
|---|---|---|---|
| 1 | **Critical** — Flask `debug=True` hardcoded on the only documented entry point; combined with #3/#4 below, an unauthenticated client could reach a remote Python shell via the Werkzeug debugger on any triggered 500 | Extracted to `_debug_enabled()`, gated on `PORTAL_DEBUG` env var, defaults `False` | `portal/app.py` |
| 2 | **Critical** — the freight decision-email endpoint (`/api/dispatch/decision/<load_id>/<action>`) was not exempted from the login gate, so every one of Dispatch's own action-link emails (acknowledge/flag/escalate/request-info) redirected a clicking reviewer to `/login` with no way back — breaking the Control Layer this repo's own CLAUDE.md describes. Unnoticed because the whole test suite runs with `TESTING=True`, which disables the gate outright | Added a narrow, single-endpoint exemption (`dispatch_api.dispatch_decision`) alongside the existing `decisions` blueprint exemption — not a blanket blueprint exemption | `portal/app.py` |
| 3 | **High** — 11 PATCH/POST endpoints crash with an unhandled `TypeError` → 500 if a request body echoes the record's own ID field (a very plausible "fetch, edit, PATCH the whole object" client pattern) | `data.pop("<id_field>", None)` before splatting into each `services.update_X(id, **data)` call, at all 12 sites found (11 originally flagged + `update_driver_pay`, same pattern, added defensively) | `portal/routes/dispatch_api.py` |
| 4 | **High** — ~30 write endpoints 500 on a syntactically-valid-but-non-dict JSON body (a list/string/number), since `get_json(silent=True) or {}` only substitutes `{}` on parse *failure*, not on wrong type | New `_json_body(force=False)` helper normalizing any non-dict result (including `None`) to `{}`; all 30 `silent=True` and 18 `force=True` call sites replaced | `portal/routes/dispatch_api.py` |
| 6 | **Medium** — none of the 11 `notify_*` call sites are wrapped in try/except; an SMTP timeout/auth failure raised *after* the underlying DB write already committed turns an already-successful archive/delivery/invoice into an apparent 500 | New `_notify_safe()` wrapper around every notify call site; logs and continues rather than propagating | `dispatch/services.py` |
| 7 | **Medium** — one malformed or wrongly-shaped JSON file in the load-source directory aborts acquisition for every load in the batch, not just the bad one | `_acquire_local()` now catches per-file parse/shape errors, skips and logs the offending file, continues with the rest | `dispatch/acquisition.py` |
| 8 (sweep's #9) | **Low-Medium** — a malformed (non-empty) `ended_at` on stop-detention is silently swallowed by `DetentionEvent.total_hours()` into `0.0` hours, which means `stop_detention()` creates **no expense at all**, with no error surfaced — real revenue disappearing silently | API-boundary validation in the `stop_detention` route: a non-empty, unparseable `ended_at` now returns 400 before reaching the service layer. An empty value still defaults to "now," unchanged | `portal/routes/dispatch_api.py` |
| 9 (sweep's #10) | **Low** — two financial reporting paths (`get_financial_dashboard`, `get_load_profitability`) disagreed on totals by up to a cent or more for the same underlying data, due to sum-then-round vs. round-then-sum | `get_financial_dashboard()` now rounds per-load before accumulating, matching the convention `store.get_load_profitability_data()` already used — one consistent rule everywhere revenue/expenses are aggregated | `dispatch/services.py` |
| 10 (sweep's #11) | **Low** — `GET /api/dispatch/fuel-estimate` 500s on a non-numeric query parameter, unlike the equivalent POST-body path | Wrapped in try/except, returns 400, matching the pattern already used elsewhere in the same file | `portal/routes/dispatch_api.py` |

**Finding #5 is not in this list — attempted, reverted, moved to §2.** See below: it looked like a safe mechanical fix and wasn't.

**Not fixed on purpose beyond that — see §2 for why.**

### A fix that was attempted, broke real tests, and was reverted

Finding #5 (`archive_load()`/`add_milestone()` bypassing `validate_status_transition()`) was implemented first: `add_milestone()` was changed to validate before cascading a status change, and `archive_load()` gained a non-blocking consistency check logging when archiving from a status outside `_VALID_TRANSITIONS`' listed paths.

**The full-suite regression run (§8) caught the mistake before anything was pushed.** 10 pre-existing, passing tests failed — `test_financials.py::test_archive_with_financials` among them, which calls `add_milestone(lid, "dispatched")` then `add_milestone(lid, "delivered", ...)` and expects the load to reach `delivered` cleanly. `_VALID_TRANSITIONS` doesn't allow `dispatched -> delivered` directly (only via the intermediate steps) — but this test, and evidently the intended design, treats milestone-triggered status cascades as legitimately able to skip ahead (a driver's report doesn't always cover every checkpoint), unlike `update_load()`'s explicit, deliberate status-setting API, which *should* follow the table strictly.

The fix was built on a wrong premise: that milestones should be governed by the same strict adjacency rule as explicit status updates. They're not, and real passing tests already relied on that difference. Both changes were fully reverted (verified: full suite green again, §8). This is now **finding #5 in §2 (Unresolved Issues)** — it needs more careful, test-verified design that distinguishes legitimate skip-ahead from reviving a genuinely terminal state (`cancelled`/`archived`, both of which have zero allowed outbound transitions in the table), not a second attempt under this pass.

---

## 2. Identified Unresolved Issues (not fixed, and why)

| Issue | Why it wasn't fixed here |
|---|---|
| **`archive_load()` and `add_milestone()` bypass `validate_status_transition()`** (sweep finding #5) — no consistency check between milestone-triggered/archive status changes and the codebase's own `_VALID_TRANSITIONS` table. | **Attempted and reverted** — see the writeup above §1's table. Milestones legitimately skip ahead (real, passing tests depend on it); `_VALID_TRANSITIONS`'s strict adjacency was designed for `update_load()`'s deliberate API, not the looser event-driven cascade. A correct fix needs to distinguish "skip-ahead" (fine) from "reviving a terminal state" (`cancelled`/`archived`, both `set()` in the table — never fine) — that distinction wasn't verified before the first attempt, and shouldn't be guessed at twice in the same pass. |
| **`archive_load()`'s three-step write isn't atomic** (sweep finding #8) — a process death between `create_retention()` and `update_load(status="archived")` can strand a load in a state where the retention record exists but the load never shows as archived, and re-archiving is permanently blocked (the "already archived" check is keyed on retention existing). | Fixing this properly means giving `store.py`'s ~50+ functions a way to share one transaction — `get_connection()` opens and commits a fresh connection on *every* call today, with no shared/global connection anywhere. That's a real change to a foundational pattern used throughout the entire data layer, not a contained fix to one function. Governance rule 3 ("do not silently change architecture") applies. Needs a scoped follow-up, not a rushed patch. |
| **TOCTOU race in `update_load()`'s status validation** (sweep finding #12) — read-validate-write across separate connections with no locking; two concurrent status changes from the same starting state can race. | Confirmed **not currently reachable**: the only run path (`portal/app.py`, `python portal/app.py`) uses Flask's default single-threaded dev server. Becomes real only behind a multi-worker/multi-threaded WSGI server (i.e. the VPS deployment path with gunicorn `--workers 2`, per `DEPLOY_VPS.md`). Worth resolving before scaling past one dispatcher on a networked deployment — not before a first local live load. |
| **`archive_load()` has no completeness gate** (from the earlier gap analysis, reconfirmed) — a load with zero evidence and no POD can be archived. | Explicitly out of scope per your own instruction when this was first found: a business-rule decision (what must exist before a load can close), not a code defect. |
| **Double-booking of drivers/equipment is not prevented** — `_validate_driver_assignment`/`_validate_equipment_assignment` only check `status == "active"`, never whether the driver/equipment is already on another open load, even though `store.get_active_load_for_driver`/`get_active_load_for_equipment` already exist and are used for display elsewhere. | Business-rule gap (can one driver legitimately run two loads simultaneously in some workflow?), not a code-safety defect — correctly separated by the defect-sweep agent, not re-litigated here. |
| **`PORTAL_INQUIRY_MODE`** — **RESOLVED, no longer unresolved.** See D6 (§6): reclassified as a Mandatory Core Function (Load Search / Operational Retrieval) under Driver-First Doctrine (§0). Moved out of this table because the *question* is answered — but the *feature* it now names doesn't exist yet (today it's read into `Config` and shown on settings, nothing else). It's tracked as a required, not-yet-built item in §10/§11, not left here as an open question. | — |
| **`DISPATCH_ARCHIVE_PATH` vs `DISPATCH_ARCHIVE_ROOT` naming collision** (original decision-register question D7) — two different env vars controlling two different trees (contract-intel vs. freight), yet freight notification `.eml` fallbacks land under the `DISPATCH_ARCHIVE_PATH` tree, not the freight-intuitive `DISPATCH_ARCHIVE_ROOT` tree. The codebase's own comments (`dispatch/services.py`) acknowledge this exact confusion for a related case. | **Still genuinely open.** The "Final D1-D8 Decisions" message answered a different question under the label "D7" (email/business-document archive handling — recorded as new decision **D10** in §6) — that is not an answer to this one. Kept here, unresolved, rather than silently marked answered by a decision that addressed something else. |
| **Reconciliation adapters (`reconciliation/`) are a genuinely tested but completely unwired stub** — zero routes, zero UI, confirmed by grep. Explicitly documented as intentional in `docs/CANONICAL_RECONCILIATION_INTEGRATION.md`. | Not a gap to close — it's working as designed (a read-only reporting layer not yet wired in). Included here only so it isn't mistaken for broken. |
| **`publisher_adapter.py` hardcodes `is_approval_enforced=False`**, which is now stale — `portal/models/publisher.py`'s `update_action_status()` *does* enforce a real `approved_by` identity for `APPROVED` transitions. | The adapter under-reports current enforcement state. Low-stakes (the adapter is unwired, per above) but worth a follow-up ticket since it's a factual inaccuracy in code, not a design gap. |
| **DAT/Truckstop load-board adapter is half-built** — `dispatch/acquisition.py` already has the URL/key/JSON-parsing/fallback scaffolding (`DISPATCH_LOAD_API_URL`/`_KEY`), just unwired to a real vendor and untested at the `urlopen` level (the existing test monkeypatches the whole function, not the network call underneath it). | Needs a vendor choice and real response-shape confirmation from Mike before it can be finished — see §6. |

---

## 3. Corrected Implementation Defects

Ten items, §1 above. All additive/mechanical, no business logic changed, no existing test broken (§8).

---

## 4. Defined API and Middleware Connection Points

Branch: `claude/freight-core-defect-fixes` (same branch as the defect fixes — both are code changes per rule 7's "separate documentation, code, configuration, and business-rule decisions," and these two boundaries are code, like the fixes). Tests: `tests/test_deployment_boundaries.py`, 5 tests.

Both follow the one proven degradation pattern already in this codebase (`cin_lite/email_delivery.py`'s `_send_or_write`: attempt the real integration if configured, else write a local artifact, never block the pipeline) rather than inventing a new shape per integration.

| Boundary | File | What it does | What it deliberately does NOT do |
|---|---|---|---|
| **Customer/broker-facing email** | `dispatch/customer_notifications.py` — `notify_customer(to_address, subject, body, fallback_id)` | Sends via the same SMTP-or-local-file transport every other email in this codebase uses. Confirmed: **nothing in this codebase has ever sent a customer/broker-facing email** — all 11 existing `notify_*` functions go to the internal reviewer only. | Does not decide what triggers it, what it says, or where the recipient address comes from — **the `Load` model has no `broker_email`/`customer_email` field at all** (confirmed by reading `dispatch/models.py`; only `customer` and `broker_shipper`, both plain name strings), so the caller must supply the address explicitly. This is a real schema gap, not something to paper over — see §6. |
| **Accounting export** — **superseded, needs rework** | `dispatch/accounting_export.py` — `export_settlement(settlement) -> dict` | Writes a structured JSON export of a settlement's real fields (from the actual `Settlement` model — nothing invented) to a local `AccountingExport` folder, following the same local-file-fallback shape as the acquisition layer. Never raises. | **D4 (§6) replaces this whole approach.** The decision is a generic "System Keys Card" integrations registry (Accounting/ELD/Scanner/Printer/DAT/TruckSmart/Other, each holding an API key/credentials/token/config) inside the Driver Portal, not a single accounting-specific adapter. This file is a reasonable *pattern* to reuse for whatever the accounting entry in that registry ends up calling, but it's built as a one-off, not as a registry entry — it needs to be re-scoped, not deleted, once the registry itself is designed. Not reworked this pass (blueprint mode). |
| **DAT/Truckstop load-board API** | `dispatch/acquisition.py` (pre-existing, not built this pass) | Already has URL/key config, generic JSON parsing, and exception-safe local fallback | Not wired to a real vendor; untested at the transport level. Closer to done than the other two — needs a vendor choice, not a new boundary. |

---

## 5. Deployment Configuration & Credentials Inventory

Full inventory (every env var, manual step, and hardcoded value) delivered separately during the investigation phase — summarized here; see the config-inventory workstream's findings for the complete table.

**Confirmed: nothing in this codebase hard-fails at startup for a missing env var** — every value is read with `os.environ.get(...)`, never `os.environ[...]`, and `DEPLOY_LOCAL.md` says so itself. "Required" below means required for *correct/safe* live-load behavior, not required to boot.

**Manual steps that actually gate first use (fixed in docs, §7):**
- `cin-portal-init-admin` — one-time, interactive, bootstraps the PIN identity. Without it, every route redirects to `/login` with nothing to log into. This was undocumented in both deploy guides before this pass.
- `pip install -e .`

**External accounts Mike would need, and what happens without each:**
| Account/credential | Needed for | Without it |
|---|---|---|
| SMTP provider (Gmail app password, SendGrid, SES, etc.) | Real email delivery | Degrades gracefully — every notification writes to `Archive/Outbox` as a `.eml` file instead. App never crashes, but zero real emails go out until configured. |
| Anthropic API key | IFTA receipt-vision photo prefill; cin_lite agents | Degrades gracefully — deterministic/manual fallback everywhere. Not confirmed configured in the last known dev session. |
| Domain name + SSH access | VPS deployment only (`certbot`, `systemd`) | Not needed for local-desktop-only operation. |

**No account or credential is a hard blocker for a local first live load on Windows.** The only genuine blocker found was the undocumented `init-admin` step — now fixed.

**Hardcoded values worth knowing about, not currently configurable:**
- Detention rate: `free_hours=2.0`, `hourly_rate=$75/hr` (`dispatch/models.py`)
- Stalled-load thresholds (per-status, `dispatch/services.py`)
- PIN lockout: 5 attempts, 15-minute lockout (`portal/models/identity.py`)

---

## 6. Deployment Decision Register

D1-D9 below are answered (as of "FINAL D1-D8 DECISIONS" + the Driver-First Doctrine message). D10 is new, recorded from content that arrived labeled "D7" in that message but answers a different question than original D7 — see the note under D10. The original D7 (archive path naming) is **still open** — nothing in the message answered it; it remains in §2's table rather than being marked resolved by a decision that addressed something else.

None of these decisions have been implemented yet — this section records *what was decided*, not that the code reflects it. §11 sequences the implementation work.

| # | Status | Decision | Implementation note |
|---|---|---|---|
| D1 | **RESOLVED — ACCEPT** | `archive_load()` should enforce transitions. Allowed paths to `archived`: `completed → archived`, `delivered → archived`, `cancelled → archived`. No other operational state may archive directly. Reasoning given: "Archive is a historical record system, not an operational bypass." | `_VALID_TRANSITIONS` (`dispatch/services.py`) needs `"cancelled": {"archived"}` added (currently `set()` — today's code allows this in practice by bypassing the table entirely, so this is a net-new table entry, not a loosening). Then the non-blocking consistency check already added to `archive_load()` (§1) can become a real, enforced gate — flip the log-only check to a raise. |
| D2 | **RESOLVED — ACCEPT** | `Load` (once committed) must eventually carry: Broker Company, Broker Contact, Broker Email; Customer Name, Customer Contact, Customer Email; Rate Confirmation; POD; Invoice; Completion Packet. Reasoning given: "Every committed load eventually requires these." | Broader than the original question (which only asked about `broker_email`/`customer_email`). Rate Confirmation, POD, and Invoice already exist as separate records linked by `load_id` (§10) — this decision says a *committed* load should be treated as incomplete until all of these exist, not just permitted to have them. Completion Packet doesn't exist as a concept yet — see D3/D5. |
| D3 | **RESOLVED — ACCEPT WITH DRIVER-FIRST AMENDMENT** | Completion workflow: End Load → Publisher Request → Library Template → Publisher Creates Documents → Email Helper Review Package → Human Review → Submit → Email Cluster Archived → Archive Takes Custody. Auto-send allowed **only** for 97%+-confidence opportunity alerts. Broker communications, customer communications, invoices, POD packages, and completion emails all stay human-approved — never auto-sent. | `Publisher`/`Library` already exist and are real (`portal/models/publisher.py`, `library.py` — §4's middleware map). "Email Helper" as a named review-package step does not exist as a component yet; the closest existing piece is the new `dispatch/customer_notifications.py` boundary (§4), which is a transport, not a review/approval step — this workflow implies more than that boundary currently does. |
| D4 | **RESOLVED — REPLACES ORIGINAL PROPOSAL** | Not an accounting-specific export. A generic **"System Keys Card"** integrations registry inside the Driver Portal, covering Accounting, ELD, Scanner, Printer, DAT, TruckSmart, and Other — each holding an API Key, Credentials, Token, and Configuration. Reasoning given: "Dispatch should manage integrations, not hard-code vendors." | Supersedes `dispatch/accounting_export.py` as built (§4 note above) — that file's pattern is reusable, its scope isn't. Also subsumes the DAT/Truckstop vendor question (original D5) as one registry entry rather than a bespoke adapter — but the *specific* sub-question (which vendor, what's their real response shape) is still unanswered and still needs a real answer before that entry can do anything live. |
| D5 | **RESOLVED — OVERRIDES "delay" RECOMMENDATION** | "End Load" is a deterministic event, not a judgment call. On press: Generate Completion Packet → Generate Invoice → Attach POD → Generate Broker Email → Generate Customer Email → Create Email Package → Route to Email Helper. Reasoning given: "No mystery exists. It is a workflow trigger." | This is the trigger-precision D3 was missing ("which milestone should fire it" — answered: the End Load button itself, always, deterministically). Same build dependency as D3: needs Completion Packet and Email Helper as real concepts/components, neither of which exist in code yet. |
| D6 | **RESOLVED — MAJOR RECLASSIFICATION** | `PORTAL_INQUIRY_MODE` is not dead config or a read-only utility. Reclassified as a **Mandatory Core Function**: Load Search / Load Lookup / Operational Retrieval. Mission: "find the answer now." Governed by the 70 MPH test (§0). Must be reachable from every major Driver Portal screen, not buried in reports or admin navigation. | See full spec in §10 (new readiness-matrix row) and §11 (sequencing) — this is the single largest net-new scope this doctrine adds to the first-live-load path. Backend: recognize inquiry/retrieval as a protected, read-only mode with fast access to load records, documents, contacts, and archive data. Required lookup targets: Load Number, BOL Number, PO Number, Reference Number, Broker Contact/Phone/Email, Customer Contact/Phone/Email, Pickup/Delivery Address, Appointment Time, Rate Confirmation, POD, Invoice, Completion Packet, Current Load Status, Archive Record, related documents. Allowed actions: search, view, lookup, retrieve, print, export, review, reference, open documents, confirm data. Blocked actions: create, modify, delete, archive, complete, dispatch, send, overwrite, finalize, change status. |
| D7 | **Not answered — see §2.** Original question (archive fallback-mail path: `DISPATCH_ARCHIVE_ROOT` vs `DISPATCH_ARCHIVE_PATH`) remains open. | — | — |
| D8 | **RESOLVED — ACCEPT** | Archive atomicity is a future architecture refactor, not a first-live-load blocker. Scoped as its own separate work item: `ARCHITECTURE_REFRACTOR_ATOMIC_STORAGE` (name as given). | Matches this document's own original assessment (§2) — governance rule 3 applies, this was already flagged as needing a scoped follow-up rather than a rushed patch. Confirmed, not changed. |
| D9 | **RESOLVED — LOCKED, Constitutional priority** | Driver-First Doctrine, in full — see §0. | Governs interpretation of every other decision and every future feature, not just D6. |
| D10 *(new)* | **RESOLVED** | Email Archive Handling — no standalone email archive system. Workflow: Email Sent → Render Email to Business Document → Attach Related Files → Create Email Cluster → Store With Completion Package → Archive Takes Custody. Reasoning given: "Dispatch is a business record system... Outlook remains email system of record. Archive retains operational package history." | Arrived labeled "D7" in the decisions message but answers a different question than this document's original D7 (see above) — recorded under a new number so neither answer overwrites the other. Elaborates D3/D5's "Email Cluster Archived → Archive Takes Custody" step with the render-to-document mechanism. |

---

## 7. Deploy Documentation Fixes

Branch: `claude/fix-deploy-docs-init-admin` (separate from the code branch, per rule 7). Doc-only, no code touched.

- Both `DEPLOY_LOCAL.md` and `DEPLOY_VPS.md` `git clone`d the wrong, stale repo name (`cin-hybrid.git`) — following either doc from scratch failed at step one. Fixed to `Dispatch.git`.
- Added the missing `cin-portal-init-admin` bootstrap step to both docs, in the right place in each walkthrough (documented interactively, with the real prompts, verified directly against `portal/cli.py` — not guessed).
- `DEPLOY_VPS.md` claimed "No authentication — the portal is open to anyone with the URL" and recommended building Flask-Login or nginx basic auth from scratch. Corrected: PIN auth already exists and is fail-closed; the real gap was the missing bootstrap step, not missing code. Nginx basic auth is now framed as an optional second layer, not "the fix."
- Documented `sync/sync_config.json` (the VPS↔local sync utility) — previously required by `run_sync.py` but undocumented in either guide.

---

## 8. Test Evidence

- **New tests this pass:** 15 (`test_deployment_hardening_fixes.py`) + 5 (`test_deployment_boundaries.py`) = 20, all passing (plus 5 in `test_sandbox_program_scoping.py` from the prior, already-merged HOLD work).
- **Full suite regression check:** `python -m pytest -q` run twice against the defect-fix branch. First run: 10 pre-existing tests failed, caused by the finding-#5 fix (see §1) — that fix was fully reverted. Second run, after the revert: **2,434/2,434 tests pass, exit 0** (the 2,414-test baseline plus this pass's 20 new tests). The failure-then-fix cycle is left in this record on purpose rather than only reporting the clean final state — the process working as intended is itself evidence worth keeping.

---

## 9. Branches (none merged to `main`, per governance rule 4)

| Branch | Contents | Status |
|---|---|---|
| `claude/sandbox-source-type-filtering-hold` | HOLD/Sandbox SAM-freight scoping | **Merged** via PR #88 (explicitly requested and approved earlier in this engagement) |
| `claude/fix-deploy-docs-init-admin` | Deploy doc fixes (§7) | Pushed, not merged, no PR opened |
| `claude/freight-core-defect-fixes` | 9 defect fixes (§1) + 2 adapter boundaries (§4); finding #5 attempted and reverted (§1, §2) | Pushed, not merged, no PR opened |

---

## 10. Deployment Readiness Matrix

14 of 16 freight subsystems rate **COMPLETE** (real model + service layer + API route + UI + dedicated tests, all independently cited): Load intake & lifecycle, Milestones & evidence, POD generation, Load archive/retention, Rate confirmation, Driver pay, Fleet, Broker contacts/scorecards, Billing/settlement, IFTA, Detention tracking, Compliance tracking, Sandbox/booking pipeline, Authentication.

1 rates **COMPLETE with a functional gap noted**: Notifications/email — real and tested, but silently degrades to local file-writing without `DISPATCH_SMTP_HOST` configured; worth an explicit pre-flight check before relying on it for a real load.

1 rates **STUB**: Reconciliation adapters — genuinely tested, zero route/UI reachability, confirmed intentional per the repo's own docs. Poses no deployment risk (can't be triggered) but isn't "shipped" functionality.

**1 new row, added by Driver-First Doctrine (§0), rates ABSENT — newly required, not yet built:**

| Subsystem | Data Model | Service Layer | API Route(s) | UI | Tests | Readiness | Notes |
|---|---|---|---|---|---|---|---|
| **Load Search / Operational Retrieval** (D6, §6) | None | None | None | None | None | **ABSENT** | `PORTAL_INQUIRY_MODE` is a `Config` value read at startup and displayed on the settings page — that's the entire footprint. No search index, no lookup endpoint, no driver-facing UI exists. Per D9's doctrine, this is now required in the first-live-load path (§11), not optional. |

Full test suite (independently confirmed twice by two different workstreams, on unmodified `main`): **2,414/2,414 pass, exit 0.**

---

## 11. Recommended Deployment Sequence

D1-D6, D8-D10 are now resolved (§6); this sequence reflects that. D7 (archive path naming) is the one still-open item from the original register.

1. **Merge the two already-pushed branches** (§9) after review — doc fixes first (zero risk), then the defect-fix/boundary branch (tested, additive, but touches more surface).
2. **Build Load Search / Operational Retrieval (D6, D9) — highest-priority net-new item, required in the first-live-load path per Driver-First Doctrine.** Per the doctrine message's own scoping for the smallest functional version that passes the 70 MPH test: a visible LOAD SEARCH/LOOKUP action reachable from every major Driver Portal screen; a fast search path over existing load records (start with Load Number, BOL Number, PO/reference number, broker/customer contact fields — the full required-target list is in §6/D6); read-only display of key load info; read-only access to attached/related documents where available; strictly no create/modify/send/archive/complete/status-change actions from this mode. This is genuinely new — no data model, service layer, route, or UI exists for it today (§10).
3. **Update `_VALID_TRANSITIONS`** (D1) to add `"cancelled": {"archived"}`, then flip `archive_load()`'s existing non-blocking consistency check (§1) to a real, enforced gate.
4. **Extend the `Load` model and commit-time validation** (D2) to carry broker/customer contact fields and treat Rate Confirmation/POD/Invoice/Completion Packet as expected-eventually on a committed load.
5. **Build the End Load deterministic workflow and Completion Packet concept** (D3, D5) — these two decisions describe one pipeline (End Load → Completion Packet → Invoice/POD attach → Broker/Customer email generation → Email Package → Email Helper) that doesn't exist as a component yet, only as connected existing pieces (Publisher, Library) plus new ones (Completion Packet, Email Helper review step, the customer-notification transport already built in §4). Build in this order, since each depends on the last: Completion Packet assembly → Email Helper review/approval step → wire End Load to trigger it deterministically.
6. **Build Email Archive Handling** (D10) once the above lands — it's the terminal step of the same pipeline (render sent email to business document, cluster with the Completion Packet, hand custody to Archive).
7. **Design the System Keys Card integrations registry** (D4) and rework `dispatch/accounting_export.py` (§4) to fit it as one registry entry, rather than staying a bespoke accounting adapter. Still needs a real DAT/Truckstop vendor answer before that entry does anything live.
8. **Run one real load locally**, per the corrected `DEPLOY_LOCAL.md` walkthrough, exercising Load Search mid-run — this is still the fastest way to validate the doctrine against reality rather than pre-deciding every detail.
9. **Scope D8 (archive atomicity) and the TOCTOU fix separately** before any networked/multi-worker deployment — neither blocks local single-user use, both remain deferred per D8's own resolution.
10. **Resolve D7** (archive path naming) whenever convenient — low-stakes, not sequenced against anything else.
