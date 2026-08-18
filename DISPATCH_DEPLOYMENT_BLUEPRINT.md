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

## 0b. COMI Doctrine v1 — Communications Intelligence (Constitutional — LOCKED)

Recorded as decision **D12** in §6; given the same authority tier as §0 (Driver-First Doctrine) per explicit instruction — placed immediately after §0 rather than renumbered into the sequential sections below, to avoid disturbing every cross-reference into §1 onward while still marking it as governing, not just one line item.

**What this doctrine resolves:** Vision 2 (Archive) and Vision 4 (Library) each independently described a future "Email Helper" layer, with two different, overlapping scopes. This engagement built something under that name (§14) before the ambiguity was resolved. COMI Doctrine v1 formally resolves it: the "Email Helper" idea was never meant to be an email platform — it's a **communications orchestration layer**, now named **COMI (Communications Intelligence)**.

**The core distinction:**
- **Outlook (or another approved external platform) is the vehicle** — send/receive/mailbox storage/folders/search/message transport/attachments-as-objects. Dispatch does not rebuild it, the same way Dispatch doesn't rebuild accounting software, scanners, printers, ELDs, or load-board infrastructure.
- **COMI is the traffic controller** — why a message is needed, who must receive it, what operational event triggered it, whether Publisher must produce content, whether human review is required, whether the result becomes a business record, and where it flows next.

**COMI's mission:** ensure the right information reaches the right stakeholder at the right time through the right approved channel, in service of the lifecycle — find a load, book a load, run a load, deliver a load, bill a load, get paid.

**COMI may:** detect communication-triggering events; determine required stakeholders, recipients, and copied parties; route production requests to Publisher; route completed drafts to the appropriate review surface; duplicate communications across multiple stakeholders; track delivery attempts, results, and return messages/responses; route completed records to Archive and reusable language/templates to Library; coordinate communication cards and alerts in the Driver Portal; interface with Outlook (or an approved platform) for transport; support deterministic behavior where authorized; preserve human review and approval where required.

**COMI does not own:** email infrastructure, mailboxes, Exchange/Outlook storage, folders, or search; accounting, scanner, printer, ELD, or load-board software; final business decisions, legal commitments, or human approval authority; document creation authority (that's Publisher); long-term archive custody (that's Archive); current approved asset custody (that's Library). Mike Zachary retains final authority.

**Relationships (each already-established department's boundary is reaffirmed, not changed):**
- **Publisher** produces and drafts; COMI routes and tracks movement. Publisher must not invent facts, certifications, pricing, or unsupported claims (pre-existing rule, reaffirmed — already enforced in code, `portal/models/publisher.py`). COMI must not create production documents when Publisher is the proper authority.
- **Library** stores, retrieves, maintains, versions, and presents approved assets; does not create, research, negotiate, approve, or submit (pre-existing rule, reaffirmed). COMI may route approved communication templates/reusable wording/message components to Library, and may request retrieval when a communication requires an approved asset. COMI does not replace Library.
- **Archive** owns completed records, historical records, retention, retrieval, purge recommendations, and document-review alerts. COMI may route completed communications, delivery confirmations, response records, and communication artifacts to Archive once they become business records. COMI does not replace Archive, and does not determine retention or purge policy — Archive assumes custody at the point a communication transitions from an operational event into a retained record.
- **Cards** — COMI is tightly integrated with the Portal card system: review cards, communication cards, alert cards, missing-recipient cards, follow-up cards, return-message cards, escalation cards, stakeholder-notification cards. The card is the human-facing display; COMI determines why it exists, what movement is required, who must act, and what status is tracked.

**Current build classification:** the freight closeout communications work built this engagement (§13/§14/§15 — `portal/models/email_helper.py`, the draft → human review → submit → cluster → Archive-custody pipeline) is reclassified as **"COMI Component: Freight Closeout Communications"** — the first operational COMI component, not "Completion Packet Review" and not an Outlook replacement. It demonstrated the COMI pattern precisely: Operational Event Detection → Stakeholder Identification → Draft Creation → Human Review → Communication Delivery → Status Tracking → Archive Handoff.

**Naming guidance:** *COMI* = Communications Intelligence (the layer). *COMI Component* = a specific communication workflow. *Freight Closeout Communications* = the currently-implemented COMI component. *Outlook* = the external transport platform. **Legacy `email_helper` references in code may remain where renaming effort exceeds present value** — future architecture discussions favor COMI terminology, but this doctrine does not itself mandate a rename. See the impact analysis below for what a future rename would actually touch.

**Doctrine rule:** Dispatch does not rebuild wheels; Dispatch uses wheels and orchestrates workflow around them. Dispatch requires Communications Intelligence. Dispatch does not require a custom email platform.

**Required interpretation going forward, for any communication-related architecture question:** (1) determine whether responsibility belongs to COMI, Publisher, Library, Archive, Outlook, or another external platform; (2) avoid duplicating mature communications infrastructure; (3) preserve departmental boundaries; (4) preserve human authority; (5) route reusable assets toward Library; (6) route completed records toward Archive; (7) treat COMI as a workflow/routing layer, never a transport layer; (8) flag naming conflicts between legacy `email_helper` references and COMI doctrine before implementing anything that touches them.

### Architecture impact analysis — existing "Email Helper" references (informational only; no rename, refactor, or code change made)

Per explicit instruction, this is a report, not an action. Grepped the full Dispatch working tree for `email_helper`/`email_package`/`Email Helper`/`email-package`: **120 occurrences across 9 files.**

| File | Occurrences | What a future rename would touch |
|---|---|---|
| `portal/models/email_helper.py` | 4 (module-level: file itself is the module) | The module file itself — this is the actual "Email Helper" implementation (draft/edit/submit logic, `RESERVED_SYSTEM_IDENTITIES` reuse, `cin_lite.email_delivery.send()` call). A rename means moving/renaming this file and updating every importer. |
| `portal/routes/dispatch_api.py` | 19 | `from portal.models import email_helper` import; route handlers `get_email_package`, `draft_email_package`, `update_email_package`, `submit_email_package`; URL paths `/loads/<id>/email-package[/draft\|/submit]`. Renaming would mean new route paths (a real API-surface change, not just internal naming) or keeping old paths as aliases. |
| `portal/models/completion_packet.py` | 7 | `create_email_cluster()` accepts and reads an `email_package` dict; internal field naming (`email_cluster`, `email_package_id`) inside the stored packet record. |
| `portal/routes/pages.py` | 4 | `from portal.models import email_helper` import; `email_package=email_helper.get_package(load_id)` passed into both `dispatch_detail.html` and `load_readonly_detail.html`'s template context. |
| `portal/templates/dispatch_detail.html` | 20 | The "Email Helper Review Package" section heading, form field IDs (`eh-broker-email`, `eh-broker-subject`, etc.), and JS functions (`draftEmailPackage()`, `saveEmailPackage()`, `submitEmailPackage()`, `_emailPackageFormData()`). |
| `portal/templates/load_readonly_detail.html` | 13 | The read-only mirror of the same section — same field/label naming, no JS (read-only page). |
| `dispatch/services.py` | 1 | A single reference (docstring/comment context near `build_completion_packet()`) — not the module itself, low-impact. |
| `tests/test_email_helper.py` | 48 | The entire dedicated test file — class name, fixtures, and every test in it reference `email_helper`/the "Email Helper" concept by name. |
| `tests/test_email_archive_handling.py` | 4 | Cross-references the email_helper package shape when testing the D10 cluster/custody flow. |

**What a full rename would actually require, if ever directed:** (1) rename `portal/models/email_helper.py` → something like `portal/models/comi_freight_closeout.py` or a general `portal/models/comi.py`, updating both importers (`dispatch_api.py`, `pages.py`); (2) decide whether to change the public API routes (`/email-package/...`) — a breaking change to anything that already calls them, versus keeping the URL stable while renaming only internals; (3) rename the persisted JSON storage file (currently `email_packages.json`, via `get_data_dir()`) — a real data-migration question if any live packages already exist under that filename, though at this stage of the project that risk is low since this hasn't run in production yet; (4) update template section headings, field IDs, and JS function names in two templates; (5) rename `tests/test_email_helper.py` and update its internal naming throughout. None of this was done — this row exists so a future rename decision starts from an accurate map, not a guess.

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
| **`PORTAL_INQUIRY_MODE`** — **RESOLVED.** See D6 (§6): reclassified as a Mandatory Core Function (Load Search / Operational Retrieval) under Driver-First Doctrine (§0). **Built — see §12.** Correction to this document's own earlier claim: the search UI/route/backend were assumed absent, based on `PORTAL_INQUIRY_MODE` (the config flag) having zero wiring. That's still true of the flag itself — but a real, separate, already-tested search feature (`dispatch.store.global_search()`, `GET /search`, `GET /api/dispatch/search`) existed on `main` all along, unconnected to that flag, discovered only once implementation started. §12 covers what was found versus what was actually built. | — |
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
| D11 *(new)* | **RESOLVED, refined** | The real chain in this instance: **Manufacturer hires Shipper, who uses a Broker, who hires Level 1 Transport Inc.** (the carrier — Dispatch's own operating company). They are genuinely distinct parties, not one entity — the initial "Customer/Shipper/Broker are the same thing" framing was shorthand for the actual rule, corrected here: **the law requires open disclosure of rates, fees, and costs across this chain.** There is no need to curtain (withhold) rate/fee/cost figures between these parties for this business — not because they're the same party, but because disclosure between them is a legal requirement, not a discretionary courtesy. | Resolves §17's M4 flag the same way, for the *correct* reason: the identical rate/invoice figures in the broker and customer emails (PR #98) don't need separating, because withholding them was never required or appropriate to begin with — not because there's no one to withhold them from. **Correction to this document's own prior framing:** the earlier version of this row said Customer/Shipper/Broker "are the same entity/role" and floated collapsing `Load`'s separate `customer`/`broker_shipper` fields as a simplification opportunity — that implication doesn't hold now that the chain is known to have genuinely distinct parties (Manufacturer, Shipper, Broker, Carrier). The schema staying as-is (separate broker and customer/shipper fields and contacts) is the more accurate model, not a simplification target. No code change made or needed either way — this is a disclosure-policy clarification, not a data-model instruction. |
| D12 *(new)* | **RESOLVED — LOCKED, Constitutional priority (equal to D9)** | COMI Doctrine v1 — see §0b. "Email Helper" (Vision 2/Vision 4's ambiguous, overlapping concept) is resolved as **COMI (Communications Intelligence)**: a communications-orchestration/routing layer, not an email platform. Outlook (or an approved equivalent) remains the transport; COMI determines why/who/what-triggered/whether-Publisher-needed/whether-review-needed/where-it-flows-next. | Governs interpretation of every future communications-architecture question, not just the current build. This engagement's already-built `email_helper.py` (§13/§14/§15) is reclassified as "COMI Component: Freight Closeout Communications" — the first operational COMI component. No rename/refactor performed — see §0b's impact analysis for exactly what a future rename would touch. |

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

## 9. Branches

| Branch | Contents | Status |
|---|---|---|
| `claude/sandbox-source-type-filtering-hold` | HOLD/Sandbox SAM-freight scoping | **Merged** via PR #88 |
| `claude/fix-deploy-docs-init-admin` | Deploy doc fixes (§7) | **Merged** via PR #90 |
| `claude/end-load-completion-packet` | End Load / Completion Packet (§13) + Email Helper review package (§14), D3/D5 | **Merged** via PR #92 |
| `claude/freight-core-defect-fixes` | 9 defect fixes (§1) + 2 adapter boundaries (§4); finding #5 attempted and reverted (§1, §2) | **Merged** via PR #91 |
| `claude/driver-load-search` | Load Search / Operational Retrieval, D6/D9 (§12) | **Merged** via PR #89 — went `behind` after #90/#92/#91 merged ahead of it, updated with the latest `main` via `update_pull_request_branch`, re-ran CI green, merged |
| `claude/d10-email-archive-handling` | D10 Email Archive Handling (§15) | **Merged** via PR #93 — up to date with `main` at open, CI green on the first run, no `update_pull_request_branch` round needed |
| `claude/system-keys-registry` | D4 System Keys Card registry, Lane M3 (§17) | **Merged** via PR #94 |
| `claude/d1-status-transition-gate` | D1 status-transition gate, Lane M1 (§17) | **Merged** via PR #95 — required a mid-flight fix, see §17 |
| `claude/load-search-readonly-detail` | Read-only Load Search detail view, Lane M5 (§17) | **Merged** via PR #96 |
| `claude/publisher-adapter-flag-fix` | Reconciliation adapter flag correction, Lane M2 (§17) | **Merged** via PR #97 |
| `claude/email-helper-document-generation` | Email Helper closeout-data enrichment, Lane M4 (§17) | **Merged** via PR #98 |

**`main` is now at `43f4185`** (PR #88 → #90 → #92 → #91 → #89 → #93 → #94 → #96 → #97 → #98 → #95, in that order). All eleven branches from this engagement are now merged; none remain open.

**Post-merge full-suite confirmation, run directly against `main`** at each milestone: `cc6c467` (after #89, before #93) **2,469/2,469**; `57a7701` (after #93) **2,480/2,480**; `43f4185` (after all five §17 lanes, final) **2,534/2,534 pass, exit 0** — reconciles exactly (2,480 + 27 + 13 + 2 + 5 + 7 = 2,534 across M3/M5/M2/M4/M1 respectively), confirming the full set introduced no integration issue beyond the one caught and fixed mid-merge (§17).

**PR policy note:** as of this pass, PRs are opened one per branch as each section completes (explicit instruction), rather than only on request as in earlier phases of this engagement. Merging into `main` now happens on explicit per-PR authorization once CI is green, without further check-ins during CI/merge itself (a later explicit instruction narrowed this further) — still never merged without that original authorization, and a green-but-`behind` PR is updated with the latest `main` and re-checked rather than force-merged.

---

## 10. Deployment Readiness Matrix

14 of 16 freight subsystems rate **COMPLETE** (real model + service layer + API route + UI + dedicated tests, all independently cited): Load intake & lifecycle, Milestones & evidence, POD generation, Load archive/retention, Rate confirmation, Driver pay, Fleet, Broker contacts/scorecards, Billing/settlement, IFTA, Detention tracking, Compliance tracking, Sandbox/booking pipeline, Authentication.

1 rates **COMPLETE with a functional gap noted**: Notifications/email — real and tested, but silently degrades to local file-writing without `DISPATCH_SMTP_HOST` configured; worth an explicit pre-flight check before relying on it for a real load.

1 rates **STUB**: Reconciliation adapters — genuinely tested, zero route/UI reachability, confirmed intentional per the repo's own docs. Poses no deployment risk (can't be triggered) but isn't "shipped" functionality.

**1 new row, added by Driver-First Doctrine (§0), rates ABSENT — newly required, not yet built:**

| Subsystem | Data Model | Service Layer | API Route(s) | UI | Tests | Readiness | Notes |
|---|---|---|---|---|---|---|---|
| **Load Search / Operational Retrieval** (D6, §6) | `loads`/`drivers`/`equipment`/`settlements` tables (existing) + `BrokerContact` (existing) | `dispatch/store.py::global_search()` (existing, extended §12) | `GET /search`, `GET /api/dispatch/search` (existing) | `portal/templates/search.html` (existing, extended §12), sidebar link on every page (existing, relabeled §12) | `tests/test_global_search.py`, 27 tests (17 existing + 10 new, §12) | **COMPLETE** | Corrects this document's own earlier "ABSENT" claim — see the note under this row's original entry in §2. Built on top of a real pre-existing feature; see §12 for exactly what was found vs. added. |
| **End Load / Completion Packet** (D3, D5, §13) | `portal/models/completion_packet.py` (new, §13) | `dispatch/services.py::build_completion_packet()` (new, §13) | `POST /api/dispatch/loads/<id>/end-load`, `GET .../completion-packet` (new, §13) | Completion Packet section + End Load button on `dispatch_detail.html` (new, §13) | `tests/test_completion_packet.py`, 13 new tests (§13) | **COMPLETE** | Assembly + deterministic trigger + Publisher routing + human-review gate all real and tested. |
| **Email Helper Review Package** (D3, §14) | `portal/models/email_helper.py` (new, §14) | Draft/edit/submit logic lives in the model itself (§14) | `POST .../email-package/draft`, `GET/PATCH .../email-package`, `POST .../email-package/submit` (new, §14) | Review Package section on `dispatch_detail.html` (new, §14) | `tests/test_email_helper.py`, 16 new tests (§14) | **PARTIAL** | Drafting, human review/edit, and human-gated submit (send-or-local-fallback) all real and tested. Not built: D10 (render sent email to business document, cluster with Completion Packet, hand custody to Archive) — deliberately deferred as its own decision point, see §14. |

Full test suite (independently confirmed across four different workstreams, on unmodified `main` or a direct child of it): **2,414/2,414** (original baseline) → **2,427/2,427** (§13) → **2,443/2,443** (§14, current), exit 0 throughout. (Load Search's 27 tests live on a sibling branch not included in this count — see §9.)

---

## 11. Recommended Deployment Sequence

D1-D6, D8-D10 are now resolved (§6); this sequence reflects that. D7 (archive path naming) is the one still-open item from the original register.

1. **Merge the two already-pushed branches** (§9) after review — doc fixes first (zero risk), then the defect-fix/boundary branch (tested, additive, but touches more surface).
2. **~~Build~~ Extend Load Search / Operational Retrieval (D6, D9) — done, see §12.** Turned out to be mostly-real already; extended rather than built from scratch.
3. **Update `_VALID_TRANSITIONS`** (D1) to add `"cancelled": {"archived"}`, then flip `archive_load()`'s existing non-blocking consistency check (§1) to a real, enforced gate.
4. **Extend the `Load` model and commit-time validation** (D2) to carry broker/customer contact fields and treat Rate Confirmation/POD/Invoice/Completion Packet as expected-eventually on a committed load.
5. **~~Build~~ End Load deterministic workflow, Completion Packet concept, and Email Helper review package — done, see §13/§14.** Completion Packet assembly, the deterministic End Load trigger, Publisher routing, and the Email Helper draft/edit/human-gated-submit step are all built and tested. Still open: D10 (below).
6. **~~Build~~ Email Archive Handling (D10) — done, see §15**, PR #93 open. Terminal step of the D3/D5/D10 pipeline: render sent email to business document, cluster with the Completion Packet, hand custody to Archive — all built as a cross-reference on the Completion Packet, with Archive Load's existing manual trigger left unchanged.
7. **Design the System Keys Card integrations registry** (D4) and rework `dispatch/accounting_export.py` (§4) to fit it as one registry entry, rather than staying a bespoke accounting adapter. Still needs a real DAT/Truckstop vendor answer before that entry does anything live.
8. **Run one real load locally**, per the corrected `DEPLOY_LOCAL.md` walkthrough, exercising Load Search mid-run — this is still the fastest way to validate the doctrine against reality rather than pre-deciding every detail.
9. **Scope D8 (archive atomicity) and the TOCTOU fix separately** before any networked/multi-worker deployment — neither blocks local single-user use, both remain deferred per D8's own resolution.
10. **Resolve D7** (archive path naming) whenever convenient — low-stakes, not sequenced against anything else.

---

## 12. Load Search / Operational Retrieval — Build Report

Branch: `claude/driver-load-search`. Authorized implementation (explicit "Build Load Search now"), not blueprint mode.

**What was assumed vs. what was found.** §0/§10 originally stated Load Search was entirely absent, reasoning from `PORTAL_INQUIRY_MODE` (a `Config` value, confirmed unused) having zero wiring. Before writing new code, `base.html`'s nav was checked directly and already contained a working `Search` link → `GET /search` → `dispatch.store.global_search()` → `search.html`, covering loads/drivers/equipment/settlements, already read-only (no action buttons in results), already tested (17 tests in `tests/test_global_search.py`), already on every page. **This was a separate, real, pre-existing feature, unconnected to `PORTAL_INQUIRY_MODE` — the assumption that "the config flag is dead" implied "the feature doesn't exist" was wrong; they were never the same thing.** An initial pass of new, parallel code (a second `search_loads()` in `store.py`/`services.py`) was written before this was discovered, then fully reverted once found — see the governance note below.

**What was actually built — extension, not new construction:**

| Change | File | Why |
|---|---|---|
| Added `notes` to the load-search field list | `dispatch/store.py::global_search()` | BOL/PO/reference numbers (doctrine-required lookup targets) have no dedicated field anywhere in this schema — notes is the only place one could currently be found. Documented as an honest limitation, not fixed by inventing new schema (that's D2/future work). |
| Added a `brokers` results section, reusing the already-existing `list_broker_contacts(search=...)` (itself already searches company name, contact name, MC number, phone, and email) | `dispatch/store.py::global_search()` | Closes the "Broker Contact/Phone/Email" required lookup target directly — no new search logic needed, just wiring an existing function in. |
| Relabeled the page title, nav link, and search placeholder from generic "Search" to "Load Search" / "Find the answer now" | `portal/templates/search.html`, `portal/templates/base.html` | Driver-First Doctrine (§0): plain operational language, not a technical/generic label. |
| Added a one-line "read-only lookup" statement to the search page itself | `portal/templates/search.html` | Makes the blocked-actions rule visible to the person using it, not just documented in this file. |

**What was deliberately not touched:** the results table structure, the existing loads/drivers/equipment/settlements search logic, the `/api/dispatch/search` JSON endpoint's shape (the new `brokers` key flows through automatically — that route spreads `**results` and sums `results.values()` generically, needed no code change), and the link-through to the full `/dispatch/<load_id>` detail page (a separate, already-existing, already-audited page — not part of "search mode" itself; the doctrine's read-only requirement governs the search interaction, not everywhere a search result can lead).

**Governance note — a real mistake, caught before it shipped:** the first attempt duplicated `global_search()` with a second, parallel `search_loads()`/`get_load_search_detail()` in both `store.py` and `services.py`, written before checking whether anything already existed. This is exactly the failure mode this whole engagement's governance rules exist to prevent (per the earlier "prove what already exists, then build only what truly does not" framing). Caught by reading `base.html`'s nav before wiring routes, not by a test failure — fully reverted (`git checkout --`) before any commit. Left in this record rather than omitted.

**Doctrine-required lookup targets — coverage after this pass:**

| Target | Status |
|---|---|
| Load Number, Current Load Status | ✅ (pre-existing) |
| Broker Contact/Phone/Email | ✅ (new, this pass) |
| Customer Contact/Phone/Email | ❌ — `Load` has no such fields at all yet (D2, not yet built) |
| Pickup/Delivery Address | ✅ (pre-existing) |
| Invoice | ✅ (pre-existing, via settlements) |
| Appointment Time | Partial — `pickup_datetime`/`delivery_datetime` exist and are shown on the load detail page reachable from search, not distinctly on the results list itself |
| BOL Number, PO Number, Reference Number | Partial, honest limitation — findable only if typed into a load's free-text `notes` (new, this pass); no dedicated field exists anywhere in the schema |
| Rate Confirmation, POD, Completion Packet, Archive Record, related documents | Not shown on the search results list itself, but reachable via the linked load detail page, which already displays all of these except Completion Packet (doesn't exist as a concept yet, per D3/D5) |

**Tests:** `tests/test_global_search.py` — 27 tests (17 existing, unmodified and still passing + 6 new: load-by-notes search, broker search by company name and by phone, driver-facing label check, read-only/no-action-buttons check, brokers section rendering). Full suite re-run after this change: **2,420/2,420 pass, exit 0** (the 2,414-test baseline plus these 6).

**Not done, and why:** a distinct read-only load-detail view. The doctrine's blocked-actions list governs the search *results* view; the existing `/dispatch/<load_id>` detail page (which does have edit/action controls) is where a result links to, same as it already did before this pass. Building a second, parallel detail view was considered and rejected as unnecessary scope for "smallest functional version" — flagged here as a real design choice, not an oversight, in case Mike wants search results to link to a stricter read-only page instead.

---

## 13. End Load / Completion Packet — Build Report

Branch: `claude/end-load-completion-packet`, off `main` @ `48b953f` (does **not** include Load Search — that's a separate unmerged branch, PR #89). Authorized implementation ("Build the End Load deterministic workflow and Completion Packet concept," explicit 10-point scope), not blueprint mode. Implements D3/D5 (§6).

**What was proven to exist before anything was written (rule 10):**

| Existing piece | File | How it's reused |
|---|---|---|
| `get_load_bundle(load_id)` — already assembles rate confirmation, POD, settlement, evidence, milestones, everything needed for a closeout view | `dispatch/services.py` | `build_completion_packet()` calls it directly rather than re-querying `store` from scratch. |
| `list_broker_contacts(search=...)` — already a multi-field match on company/contact/MC/phone/email | `dispatch/store.py` | Reused unchanged to resolve a load's `broker_shipper` name string to a real broker contact record. |
| `portal/models/publisher.py::create_action()` / `update_action_status()` — the existing PENDING→DRAFT→READY→APPROVED→ARCHIVED human-review gate, with the non-self-approval enforcement already built (§4/D3 context) | `portal/models/publisher.py` | Reused **unmodified**. End Load routes into it as a new action rather than building a second review/approval mechanism. |
| The `"GOVCON-{contract_id}"` synthetic-`sandbox_id` convention already established for Publisher actions with no real Sandbox entry behind them (see the comment at `portal/routes/api.py` around the GovCon proposal trigger) | `portal/routes/api.py` | Directly answered this build's central open design question (below) — copied the same convention rather than inventing a new one or changing Publisher's schema. |
| `"Archive Load"` button / `archive_load()` / `RetentionArchive` — the terminal, already-built "Archive Takes Custody" step | `dispatch_detail.html`, `dispatch/services.py` | Left completely untouched. Confirmed via the D3 pipeline (End Load → ... → Archive Takes Custody) that these are two distinct, sequential steps, not the same action — End Load is new and earlier; Archive Load is existing and stays last. |

**The design question that had to be resolved before writing code:** `publisher.create_action()` hard-requires a `sandbox_id` (not optional), but a freight `Load` created via "+New Load" never has one — it never passed through Sandbox. Two options were considered: (a) change `create_action()`'s signature to accept an optional `load_id` alternative, or (b) reuse the synthetic-ID convention the codebase already established for exactly this situation (GovCon proposals, which also have no Sandbox entry, already anchor to `f"GOVCON-{contract_id}"`). **Chose (b)** — `f"LOAD-{load_id}"` — because it required zero changes to `publisher.py`, matched an existing, documented precedent exactly, and is the more literal reading of rule 9 ("do not duplicate existing components," which extends to not duplicating a schema-extension decision that already has a working answer in the codebase).

**What was actually built — new code, and why each piece was judged not a duplicate:**

| Component | File | Why it's new, not reused |
|---|---|---|
| `build_completion_packet(load_id)` — assembles rate confirmation, POD, settlement/invoice, evidence, and broker contact into one `available`/`missing` bundle; gates on load status (`delivered`/`completed` only) | `dispatch/services.py` | Pure freight-layer assembly logic didn't exist anywhere — `get_load_bundle()` gathers the raw pieces but has no closeout-readiness concept (no available/missing, no status gate). Stays inside `dispatch/` and imports nothing from `portal/`, preserving the existing one-directional layering (`portal` → `dispatch`, never the reverse — confirmed by grep before writing this). |
| `portal/models/completion_packet.py` — new model, one JSON-file-backed record per load (`ASSEMBLED` → `ROUTED` → `ARCHIVED`), mirrors `publisher.py`/`library.py`'s exact file-backed pattern (`get_data_dir()`, `_load()`/`_save()`) | new file | The scope explicitly asked to "create the Completion Packet concept" as a distinct thing. Publisher's action-card schema has nowhere to hold a rich, structured closeout snapshot (its `available_data`/`missing_data` are label lists, not content) — adding fields to Publisher for this would be a bigger, riskier change than a small dedicated model using the same established pattern already used for two adjacent concepts. |
| `POST /api/dispatch/loads/<id>/end-load` — the deterministic trigger: builds the packet, persists it, creates the `LOAD-<id>`-anchored Publisher action, marks the packet `ROUTED`. Idempotent — re-calling on an already-ended load returns the existing packet (`already_ended: true`) rather than creating a duplicate | `portal/routes/dispatch_api.py` | New orchestration route; this is exactly where existing cross-model orchestration already lives in this codebase (`/api/publisher/create` already calls `lib_model` then `publisher.create_action` inline in a route handler — same shape, not a new architectural pattern). |
| `GET /api/dispatch/loads/<id>/completion-packet` | `portal/routes/dispatch_api.py` | Read accessor for the new concept, same pattern as `GET /retention/<load_id>`. |
| "End Load" button + Completion Packet section on the load detail page, shown only when `status in (delivered, completed)`; once run, shows packet status, ready/still-needed lists, and an explicit "no email sent automatically" statement | `portal/templates/dispatch_detail.html`, `portal/routes/pages.py` | UI surface for the new concept — positioned before the existing Retention Archive section, matching the D3 ordering (End Load happens before Archive Takes Custody). |

**Human review preserved, nothing auto-sent (scope items 6/7):** End Load's Publisher action is created with status `PENDING`, `human_approval_required: True` — the same fields every other Publisher action already carries. No code path in this build calls `update_action_status(..., "APPROVED")` or sends anything. Moving the action forward (DRAFT → READY → APPROVED) remains a manual step through the existing Publisher queue UI, unchanged.

**Explicitly not built this pass, and why:** the "Email Helper review package" step named in D3/D5. The scope instruction says "route the result toward the future Email Helper review step" — read as *toward*, not *build it*. Publisher's existing queue is the review surface right now; the richer review-package UI implied by D3 (rendering the drafted broker/customer emails themselves) doesn't exist as a component anywhere in this codebase yet and would be new scope beyond what was asked. Actual invoice/broker-email/customer-email *document generation* (D5's "Generate Invoice," "Generate Broker Email," "Generate Customer Email") is likewise not built — the packet's `available`/`missing` lists identify what's ready to draft from, but no drafting happens yet. Flagged here as the honest boundary of this pass, matching how §12 flagged its own "not done."

**A real regression caught by the full-suite run, and reverted:** the first version of this change added `"Completion Packet Ready"` to `publisher.py`'s `ACTION_TYPES` list, purely for documentation consistency (`create_action()` doesn't validate against that list — confirmed by reading it before adding). This broke a real, pre-existing, passing test (`test_portal.py::TestPublisherAllTypes::test_all_nine_action_types_exist`) which asserts `ACTION_TYPES` equals an exact nine-item list. The addition wasn't functionally necessary, so it was reverted rather than the test changed — `publisher.py` ships from this branch **completely unmodified**, which is a stronger form of "reuse, don't duplicate" than originally planned.

**Tests:** `tests/test_completion_packet.py` — 13 new tests (packet assembly + eligibility gate, artifact pickup, broker-contact matching, the `/end-load` route's status gate/idempotency/never-auto-approves behavior, and the load-detail page's conditional button/summary rendering).

**Full suite regression check:** run twice. First run (with the `ACTION_TYPES` addition still in place): 1 pre-existing test failed (above) — reverted. Second run, clean: **2,427/2,427 pass, exit 0** (the 2,414-test `main`-baseline plus these 13; this branch does not include Load Search's 6, since it branches from `main` directly, not from `claude/driver-load-search`).

---

## 14. Email Helper Review Package — Build Report

Same branch, `claude/end-load-completion-packet` (continuation, not a new branch — this is the next stage of the one D3/D5 pipeline §13 already scoped and explicitly deferred, not a separate feature). Authorized implementation ("Build the Email Helper review-package step next"), not blueprint mode.

**What was proven to exist before anything was written (rule 10):** this pass surfaced one real gap between what §4 documented and what this branch actually contains. §4 records a `dispatch/customer_notifications.py` boundary as already built — **but that file lives only on the unmerged `claude/freight-core-defect-fixes` branch.** This branch (`claude/end-load-completion-packet`) forks from clean `main`, which does not include it — confirmed by `git branch --show-current` + a direct file glob before writing anything, not assumed from the blueprint text. Reusing or duplicating that file was therefore not an option without either merging that branch first (a merge-to-shared-lineage decision, not obviously "routine") or building a second, divergent copy (a direct violation of rule 9). Went one layer lower instead:

| Existing piece | File | How it's reused |
|---|---|---|
| `cin_lite.email_delivery.send(subject, body, to, fallback_id)` — a generic, already-built, already-tested "SMTP if configured, else write to `Archive/Outbox` as `.eml`, never raise" function | `cin_lite/email_delivery.py` | Called directly for Submit. Not new or SAM-specific — `dispatch/notifications.py` (freight's own reviewer-notification module) already imports `_build`/`_send_or_write`/`from_address` from this exact module, so freight code depending on this shared transport layer is an established pattern, not a program-separation violation (rules 10-15: "Dispatch = Freight, SAM = SAM" governs contract/business data and Sandbox/Archive concepts, not a shared SMTP-or-local-file utility both programs' own notification code already depends on). |
| `portal/models/publisher.py::RESERVED_SYSTEM_IDENTITIES` and its non-self-approval rule | `portal/models/publisher.py` | Imported and reused directly for the Submit gate, rather than redefining the same identity list a second time. `publisher.py` is **not modified** by this pass either — imported from, never edited, continuing §13's stronger reuse posture. |
| Completion Packet's `closeout_data` (load, broker_contact, pods, settlement) | `portal/models/completion_packet.py` (§13) | Seeds the draft directly — no new querying of `store`/`dispatch/services.py` at all in this pass. |
| `portal/helpers.py`'s `INQUIRY_TEMPLATE_BODY` signature style ("Mike Zachary / Level 1 Transport Inc.") | `portal/helpers.py` | Matched for voice/tone consistency, not imported — that constant is a different email's content (a SAM/GovCon load-board inquiry, wired to `cin_lite.acquisition`/`processing`), not a completion email; importing it would have been a false reuse (right shape, wrong purpose) rather than a real one. |

**What was actually built:**

| Component | File | Why it's new |
|---|---|---|
| `portal/models/email_helper.py` — drafts broker/customer completion emails from the Completion Packet, holds them in `DRAFT → REVIEWED → SUBMITTED`, gates `submit_package()` on a real `submitted_by` identity, sends via `cin_lite.email_delivery.send()` | new file | The review-package concept itself doesn't exist anywhere — same file-backed pattern as `publisher.py`/`completion_packet.py`, not a new architectural shape. |
| `POST .../email-package/draft`, `GET .../email-package`, `PATCH .../email-package`, `POST .../email-package/submit` | `portal/routes/dispatch_api.py` | Same inline cross-model orchestration shape already used for `/api/publisher/create` and `/api/dispatch/loads/<id>/end-load` (§13). |
| Review-package UI (editable broker/customer email fields, Save Edits, Submit — locked read-only once `SUBMITTED`, with each recipient's real send result shown) | `dispatch_detail.html`, `pages.py` | Positioned directly below the Completion Packet section, matching D3's ordering. |

**Human review preserved, nothing auto-sent:** `submit_package()` raises `EmailHelperSubmitError` (mapped to HTTP 403) if `submitted_by` is missing or is a reserved system identity (`PUBLISHER`/`SYSTEM`/`AUTOMATION`/`INTELLIGENCE`/`LIBRARY`) — the exact same check `publisher.py` already enforces for its own `APPROVED` transition, applied here rather than re-invented. Also raises if there are zero recipient addresses filled in, so a silent no-op submit can't be mistaken for a sent package. The UI's Submit button prompts for that identity by name, mirroring `updatePublisherStatus()`'s existing `prompt('Approving identity...')` pattern exactly.

**An honest limitation carried forward from §12, not fixed here:** customer email is drafted with a blank `to` address every time. `Load` has no customer-contact field anywhere in this schema (D2, not yet built) — there is nowhere to pull a real address from. A human must type one in during review before Submit will send it; if left blank, Submit still proceeds as long as the broker address is filled in.

**Explicitly not built this pass, and why:** D10 (Email Cluster Archived → Archive Takes Custody) — rendering the sent email to a business document, clustering it with the Completion Packet, and handing custody to the Archive layer. `submit_package()` stops at a recorded send result; it does not touch `completion_packet`'s status or call `archive_load()`. Two reasons: (1) it's explicitly the next, separate item in §11's sequence, not part of "the Email Helper review-package step" as asked; (2) auto-archiving a load as a side effect of sending email would be a real behavior change to when/how the Archive layer takes custody — closer to "changing core architecture" than a contained addition, so it's left as its own decision point rather than folded in silently.

**Tests:** `tests/test_email_helper.py` — 16 new tests (draft idempotency and content assembly, the submit approval gate — missing identity, system identity, zero recipients — the local-fallback send path, submit idempotency, the can't-edit-after-submit guard, and the full draft→edit→submit route flow end to end).

**Full suite regression check:** clean on the first run this time — no repeat of §13's regression. **2,443/2,443 pass, exit 0** (2,427 + these 16).

---

## 15. D10 Email Archive Handling — Build Report

New branch, `claude/d10-email-archive-handling`, off merged `main` (`cc6c467` — this is the first branch of the engagement created *after* the §9 merge round, so unlike §13/§14 it did not need to fork from a stale commit). PR **#93 opened and subscribed**, per the standing "one PR per branch as each section completes" policy from §9 — not re-asked, since that policy reads as forward-looking, not scoped only to the four branches open when it was set.

**What was proven to exist before anything was written:** `dispatch/models.py::RetentionArchive` and `dispatch/store.py::create_retention()` — read in full before deciding how "Archive Takes Custody" should be implemented. `create_retention()` does an explicit `INSERT` against a fixed SQL column list, not a generic dataclass dump — confirming that adding a new field to `RetentionArchive` (e.g. an `email_cluster` column) would require a real schema migration, not a contained code change.

**The design question that had to be resolved before writing code:** D10 ends in "Archive Takes Custody," which could mean either (a) `RetentionArchive` itself grows a field to hold the Email Cluster, or (b) the custody relationship is recorded as a cross-reference on the Completion Packet instead, pointing at the retention record's `archive_id` without the SQL table knowing anything changed. **Chose (b)** — no SQL schema touched, `dispatch/models.py` and `dispatch/store.py` are untouched by this branch, and the Completion Packet (already a file-backed, portal-layer record this engagement created) is the natural place per D10's own wording ("Store With Completion Package").

**A second design question, resolved the same way as §14 deferred it:** does D10 mean Submit should auto-trigger `archive_load()`? Re-read D10 as describing what happens to a sent email once Archive Load runs, not a new trigger for when it runs — auto-archiving as a side effect of sending email would silently change an existing, deliberate, human-clicked action (`archiveLoad()` in the UI, unchanged since before this engagement). Kept `archive_load()`'s only trigger as the existing button; the new code only checks, when that button is clicked, whether a clustered packet exists to take custody of.

**What was actually built:**

| Component | File | Why it's new |
|---|---|---|
| `completion_packet.create_email_cluster(load_id, email_package)` — renders each sent email in a `SUBMITTED` package into a `{type, to, subject, body, send_result}` document, attaches evidence/POD/invoice references already present in the packet's own `closeout_data`, stores the cluster on the packet (`status` → `CLUSTERED`). Idempotent. | `portal/models/completion_packet.py` | The rendering/clustering concept didn't exist; extends the packet record this engagement already owns rather than creating a fourth parallel JSON-file model. |
| `completion_packet.mark_archived(load_id, retention_archive_id)` — records custody (`status` → `ARCHIVED`). Idempotent — a second call with a different `archive_id` doesn't overwrite the first. | `portal/models/completion_packet.py` | Same reasoning; also closes the `STATUSES` list I'd pre-declared in §13 (`ASSEMBLED`/`ROUTED`/…/`ARCHIVED`) but never implemented the last transition for — extended to `ASSEMBLED → ROUTED → CLUSTERED → ARCHIVED` to give the intermediate "clustered, not yet in custody" state its own name. |
| `submit_email_package` route now calls `create_email_cluster()` automatically after a real submit | `portal/routes/dispatch_api.py` | Matches D10's own framing — clustering is part of what "Email Sent" already implies, not a separate manual step. |
| `archive_load` route now calls `mark_archived()` if a clustered packet exists for the load | `portal/routes/dispatch_api.py` | This is where "Archive Takes Custody" actually happens — inside the existing, unchanged archive trigger, not a new one. A load with no completion packet, or one that's only `ROUTED` (drafted/reviewed but never submitted), archives exactly as it did before this branch. |
| Email Cluster + custody status shown on the load detail page, linking to the Retention Archive section once custody is taken | `dispatch_detail.html` | UI surface for the new concept, same placement pattern as §13/§14. |

**Tests:** `tests/test_email_archive_handling.py` — 11 new tests: cluster rendering and file-attachment content, cluster-creation idempotency, confirming a `DRAFT`/`REVIEWED` (not yet submitted) package produces no cluster, custody marking on Archive Load, archiving a load with an un-clustered packet or no completion packet at all still working exactly as before, custody-marking idempotency, and — the test that most directly checks the "stays manual" design choice — that submitting an email package alone never changes the load's status to `archived` or creates a `RetentionArchive`.

**Full suite regression check:** clean on the first run. **2,480/2,480 pass, exit 0** (2,469 post-merge baseline + these 11).

---

## 16. Status Review & Parallel Build Matrix

**Where things stand.** All six branches from this engagement are merged to `main` (§9): HOLD/Sandbox scoping (#88), deploy docs (#90), freight-core defect fixes + boundaries (#91), Load Search (#89), End Load/Completion Packet/Email Helper (#92), D10 Email Archive Handling (#93). `main` is at `57a7701`. Full suite confirmed clean directly on merged `main`, twice: 2,469/2,469 after the first five merges, then **2,480/2,480, exit 0** after #93 — the entire D3/D5/D10 completion pipeline described in the original decision register is now live and verified: run load → end load → assemble Completion Packet → route to Publisher → draft/review/submit via Email Helper → render and cluster the sent email → Archive Load takes custody.

**What's genuinely left, reclassified by what's actually blocking each item** — not just restated from §2/§11, but sorted by whether it can move today:

| # | Item | Decision status | Blocking constraint | Can build now? |
|---|---|---|---|---|
| M1 | D1 — enforce `cancelled → archived` in `_VALID_TRANSITIONS`; flip `archive_load()`'s existing non-blocking check to a real gate | Decided (§6) | None — checked `dispatch/services.py` directly just now: `"cancelled": set()` is still exactly as it was before D1 was answered. Decided but never implemented. | **Yes** |
| M2 | `publisher_adapter.py`'s stale `is_approval_enforced=False` | Identified defect (§2) | None — unwired stub (confirmed: no route/UI reachability), one-line factual correction | **Yes** |
| M3 | D4 — System Keys Card integrations registry (the generic container: Accounting/ELD/Scanner/Printer/DAT/TruckSmart/Other, each holding API Key/Credentials/Token/Config) | Decided (§6) | None for the *container* — it's a settings/config store, same shape as Publisher/Library's own JSON-file models. Only the individual vendor integrations behind it need real credentials. | **Yes, the registry itself** |
| M4 | Actual document generation for Email Helper (invoice/broker-packet content beyond the current plain-text email body) | Flagged as deferred (§14) | None architecturally — extends the existing Email Helper draft, same pattern | **Yes** |
| M5 | Stricter read-only Load Search detail view | Flagged as a real scoping choice, not built (§12) | None — but genuinely optional; only worth building if wanted | **Yes, if wanted** |
| A1 | Finding #5 — `archive_load()`/`add_milestone()` bypass `validate_status_transition()` | Attempted once, reverted (§1/§2) | Needs a correct design (distinguish legitimate milestone skip-ahead from reviving a terminal state) before a second attempt — not a parallel-safe item, same files as M1 | **Careful, solo** |
| A2 | Archive atomicity (`archive_load()`'s 3-step write isn't transactional) | Identified (§2) | Requires giving `store.py`'s ~50 functions a shared-connection pattern — genuine core-architecture change per rule 3, needs your explicit approval before starting, not just before merging | **Needs approval to start** |
| B1 | D7 — `DISPATCH_ARCHIVE_PATH` vs `DISPATCH_ARCHIVE_ROOT` naming | Still open (§2, §6) | Needs your answer — nothing to build until decided | **Blocked on you** |
| B2 | Double-booking prevention (driver/equipment already on another open load) | Identified, correctly left as a business-rule question (§2) | Needs your answer: can one driver legitimately run two loads at once in some workflow? | **Blocked on you** |
| B3 | DAT/Truckstop load-board vendor wiring (the specific API behind M3's registry) | Partially scaffolded (§4) | Needs your vendor choice + real response-shape confirmation | **Blocked on you** |
| C1 | TOCTOU race in `update_load()` | Identified, correctly deferred (§2) | Not reachable today (single-threaded dev server); becomes real only behind a multi-worker WSGI deployment | **Correctly not building yet** |

**The parallel-build matrix — what M1-M5 look like run concurrently, if authorized:**

| Lane | Item | Primary file(s) touched | Overlaps with another lane? | Branch |
|---|---|---|---|---|
| 1 | M1 (D1 transition fix) | `dispatch/services.py` (`_VALID_TRANSITIONS`, `archive_load()`) | **Yes — A1** touches the exact same function and is explicitly not parallel-safe with it. M1 alone is safe; don't run A1 alongside it. | `claude/d1-status-transition-gate` |
| 2 | M2 (adapter fix) | `reconciliation/adapters/publisher_adapter.py` | None | `claude/publisher-adapter-flag-fix` |
| 3 | M3 (registry container) | New `portal/models/integrations_registry.py` + routes + UI | None | `claude/system-keys-registry` |
| 4 | M4 (document generation) | `portal/models/email_helper.py`, `dispatch_detail.html` | None — M4 extends Email Helper, M1/M2/M3 don't touch it | `claude/email-helper-document-generation` |
| 5 | M5 (read-only search detail view, only if wanted) | New template + route | None | `claude/load-search-readonly-detail` |

Lanes 2-5 touch entirely disjoint files and have no dependency on each other — genuinely parallelizable, same reasoning §9 already proved out across the last six branches (five of six merges had zero conflicts). Lane 1 (M1) is parallel-safe with 2-5 but must not run alongside A1 (finding #5) on the same branch or the same work session, since both touch `_VALID_TRANSITIONS`/`archive_load()` and the second attempt at A1 needs the lessons from the first failed attempt applied deliberately, not raced against an unrelated concurrent edit to the same function.

**Not on this matrix on purpose:** A2 (archive atomicity) and B1-B3 — none of them are safe or possible to just start building; each needs either your explicit go-ahead (A2, since it's core architecture) or your answer to an open question (B1-B3) before there's anything to build.

**Recommendation, not a decision:** Lanes 2-5 (M2-M5) plus Lane 1 (M1) alone are ready to build in parallel right now with no further input needed from you — say the word and I'll branch and build all five concurrently, reporting back per-branch same as this session's established pattern. A1 (finding #5) is worth doing next but solo, after the M1 lane lands, not alongside it.

---

## 17. Parallel Build Matrix (M1-M5) — Build Report

Authorized ("do it") after §16's matrix. All five lanes were dispatched as independent subagents, each cloning fresh, branching off the then-current merged `main`, and working in full isolation from this main session — a genuine parallel build, not a sequential one narrated as parallel.

### A real infrastructure problem, caught and worked around

Three of the five agents (M3, M4, M5) independently discovered mid-task that their initial scratch clone directory was shared with a sibling agent's concurrent, uncommitted work — each detected foreign file changes via `git status`/`git diff` before committing, and self-corrected by re-cloning into a freshly isolated path, verifying the final diff against `origin/main` contained only their own intended files before pushing. None of the five contaminated commits reached `origin`. This was independently verified from this session's side too: every branch's actual pushed diff was re-checked with `git diff main..origin/<branch> --stat` before any PR was opened, and every one came back clean and matched what its agent reported. Worth fixing at the harness level for any future multi-agent build of this shape — each parallel build lane should get an unambiguous, pre-assigned isolated working directory rather than relying on each agent to detect and route around a collision on its own.

### A second real problem: agent self-reported test counts weren't always trustworthy

Given the above contamination risk, no agent's own final-suite pass count was taken at face value. Every branch was independently re-verified from this session: fetched, diffed against `main` to confirm the pushed commit was clean, then run in its own fresh, dedicated clone. One agent (M1) reported two different counts from two different counting methods within its own run (a `--collect-only` tally that matched the expected number, and a raw dot-count that didn't) and explicitly flagged the discrepancy rather than picking one silently — independent re-verification confirmed the `--collect-only`-matching number was correct and the dot-count was a counting artifact (this session's own dot-counting method earlier in the engagement carries the same theoretical risk, worth remembering).

### The lanes

| Lane | PR | What it does | Key judgment call |
|---|---|---|---|
| **M1** | #95 | D1: `archive_load()` now calls `validate_status_transition()` before archiving; `cancelled -> archived` added to `_VALID_TRANSITIONS`. `add_milestone()` deliberately untouched (that's finding #5 / A1, not this). | 7 pre-existing tests that archived straight from `"created"` had their setup (not assertions) fixed to drive a valid lifecycle first. |
| **M2** | #97 | Corrected `reconciliation/adapters/publisher_adapter.py`'s stale `is_approval_enforced=False` to `True` — a real code-path gate now exists in `publisher.py`. | Chose unconditional `True` over a per-record computation, to avoid duplicating the module's separate `would_pass_tri_department_gate()` function, which answers a genuinely different question. |
| **M3** | #94 | Built the D4 System Keys Card registry container (`portal/models/integrations_registry.py`, 7 integration types, Settings-page UI) — no existing vendor migrated to it. | Flagged, not silently decided: credentials are stored in plaintext JSON, same pattern as every other `portal/models/` file, genuinely different from every other secret in this codebase (all env-var-based). Accepted per the repo's documented single-admin/local-only model; not encrypted. |
| **M4** | #98 | Enriched Email Helper's drafted emails with real closeout data (pickup/delivery/rate/invoice/POD) instead of a generic placeholder. | Flagged, then **resolved by D11** (§6): the customer email includes the same rate/invoice figures as the broker email. Manufacturer/Shipper/Broker/Level 1 Transport (carrier) are genuinely distinct parties in this chain, but the law requires open rate/fee/cost disclosure across it — withholding figures was never required, so no code change needed. |
| **M5** | #96 | Built a genuinely read-only load detail view (`/search/loads/<load_id>`) and pointed Load Search's results at it instead of the full editable `/dispatch/<load_id>` page, closing a gap flagged but not built in the original Load Search PR (#89). | Search's separate Settlements results table still links to the editable page — scoped the fix to the Loads table specifically, flagged the Settlements table as a possible follow-up. |

### A real cross-lane conflict, found during merge and fixed

M1 (#95) and M5 (#96) were both built independently against the same starting `main` and were individually correct and fully green in isolation. Once #96 merged first and #95's branch was updated to include it (routine, per the merge sequence), CI on #95 failed: M5's `test_renders_retention` archived a freshly created load straight from `"created"` status — exactly the pattern D1 (#95) exists to reject, and a pattern M1's own PR had already fixed in 7 *other* pre-existing tests, but couldn't have known about this *new* one written in a sibling, isolated branch. This is the one genuine integration issue this batch produced, and it's structural, not a mistake by either agent — two correct, independently-tested changes that only conflict once combined. Fixed directly on #95 (since it was this session's own PR): drove the test's load through a valid lifecycle before archiving, same pattern already used elsewhere, no assertion changed. Full suite re-confirmed green (2,527/2,527) before re-pushing.

### Tests and final verification

54 new tests across the five lanes (M1: 7, M2: 2 net-new, M3: 27, M4: 5, M5: 13), each independently re-run in an isolated clone before its PR was opened, plus the one cross-lane fix. **Final confirmation, fresh clone of `main` @ `43f4185`: 2,534/2,534 pass, exit 0** — reconciles exactly against the running baseline (2,480 + 27 + 13 + 2 + 5 + 7).

---

## 18. Jules Sandbox Discovery Report — NOT AUTHORITATIVE, reference only

Per explicit instruction: `jax1313-outlook/Jules` is a sandbox artifact, not part of Dispatch's architecture. This section records the findings so they aren't lost, not as doctrine, not as a decision, and not as a build authorization. No code merged. Nothing here overrides §0/§0b or any Dx decision.

**What Jules actually is:** a single-file Flask presentation-layer prototype (`app.py` + `dispatch_spine.py`, ~620 lines, plus 5 templates) with one hardcoded `ActiveTrip` and a handful of sample cards, entirely in-memory — no persistence, no SQLite, no real Publisher/Library/Archive/Intelligence backend. It exists to visualize UI/IA concepts, not to compete with or replace real Dispatch's implementation. Its own repo (`README.md`) describes a *different, parallel* governance-document stack (`DISPATCH_CONSTITUTION_v3.md`, `MANAGER.md`, `DISPATCH_SPINE_SPECIFICATION_v1.md`, an "Intelligence Analyst" role) that uses different vocabulary than what's already locked in real Dispatch (§0, §0b, D1-D12) — that document stack is explicitly out of scope here and not adopted.

**Valuable, doctrine-aligned concepts worth harvesting as design reference (not code):**
| Concept | What it actually is in Jules | Why it's worth keeping as a reference |
|---|---|---|
| Consequence-level card taxonomy (0-5: Silent Log/Status/Review/Decision/Conflict/Authority) with a non-optional `"This is a recommendation only. No action is authorized. Mike decides."` closing baked into the data model | `PortalCard` dataclass, `dispatch_spine.py` | Operationalizes the "Mike decides" posture as a literal unbypassable field rather than only prose doctrine — aligns tightly with the 70-MPH-test filtering already in §0. |
| Role-based stakeholder sanitization | One function, `sanitize_stakeholder_shipment()`, explicit allow-list per role (Broker/Shipper get route risk + BOL status; Customer gets less), explicit "exclude internal scoring/notes" boundary | Real Dispatch has no broker/shipper/customer-facing portal yet — Vision #3v2 §8/§10 asked for exactly this. The pattern (one explicit function, not ad hoc per-field filtering) is the right shape for a real version. |
| Unified, consequence-sorted "everything Mike needs to decide" single-screen Operations view | `/operations` route pulling decision/conflict/authority/review/status cards into one feed | Real Dispatch spreads decisions across separate Publisher/Library/Archive/Pipeline/Queues/Conflicts pages — no equivalent unified feed exists yet. |
| Route Risk data shape (`route_risk_level`/`route_risk_summary` internal vs. a sanitized public notice) | `ActiveTrip` fields + `sanitize_stakeholder_shipment()` | Not a working risk engine (hardcoded), but a clean target schema matching Vision #3v2 §10's not-yet-built Route Risk requirement. |
| "COMI" naming and card-shape (`COMICommunicationCard`: channel/recipient_role/status) | `dispatch_spine.py` | Independently corroborates COMI Doctrine v1 (§0b) rather than conflicting with it — reinforcing signal, not new information. Real Dispatch's already-built COMI component (Freight Closeout Communications) is more behaviorally mature (real draft/review/submit/track/archive state) than this card-list mockup. |

**Discarded / not harvested:**
- All actual code — in-memory only, one hardcoded trip, no real store; not safely mergeable regardless of the explicit "do not merge" instruction.
- "Driver-First Retrieval" here is a 3-record hardcoded search stub — real Dispatch's already-merged Load Search (SQL-backed, multi-entity) is already more capable; nothing to harvest but the naming.
- The public marketing site (index/about/capabilities/contact) and trademark styling (™ on "Mission Visibility"/"Route Risk") — branding/marketing decisions, out of scope for the operating system itself, not adopted.
- Jules's own parallel governance-document stack (Constitution v3, Manager, Dispatch Spine, Intelligence Analyst) — a separate architecture exploration using different vocabulary than what's locked in real Dispatch; not merged conceptually, kept fully separate.

**Faster path to completion? Honest answer: not to code, but yes to design clarity** on three not-yet-built items Vision #3v2 already called for: the stakeholder/broker portal, a consequence-sorted decision feed, and Route Risk's data shape. None of Jules's code ports — real Dispatch's data model (SQLite `Load`/`BrokerContact`/settlement records, `portal/models/*.py` JSON stores) is entirely different from Jules's in-memory dataclasses. Any future build of these three items starts from scratch against real data, using Jules only as a worked visual/IA reference.

**Not built this pass — this is a discovery report, not a build authorization**, per explicit instruction.
