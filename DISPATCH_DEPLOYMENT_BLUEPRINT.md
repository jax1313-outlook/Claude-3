# DISPATCH_DEPLOYMENT_BLUEPRINT

Deployment-hardening pass against `jax1313-outlook/Dispatch` `main` @ `48b953f`. Four parallel investigative workstreams (config/credentials inventory, external-system/middleware boundary map, freight-core defect sweep, readiness matrix) plus direct implementation of the safe fixes and two adapter boundaries they surfaced. Every finding below is cited to a file; nothing is invented. No file in `main` was changed directly — all code lives on branches (listed in §9), none merged.

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
| **`PORTAL_INQUIRY_MODE`** is defined, defaulted (`"HUMAN_REVIEW"`), and shown on the settings page, but never read or branched on anywhere else in the code. | Unclear whether this is dead config to remove or a planned feature never wired up — flagged as a decision-register question (§6), not guessed at. |
| **`DISPATCH_ARCHIVE_PATH` vs `DISPATCH_ARCHIVE_ROOT` naming collision** — two different env vars controlling two different trees (contract-intel vs. freight), yet freight notification `.eml` fallbacks land under the `DISPATCH_ARCHIVE_PATH` tree, not the freight-intuitive `DISPATCH_ARCHIVE_ROOT` tree. The codebase's own comments (`dispatch/services.py`) acknowledge this exact confusion for a related case. | A naming/architecture decision (should freight-domain fallback mail live under the freight archive root instead?), not a pure bug — flagged, not silently changed. |
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
| **Accounting export** | `dispatch/accounting_export.py` — `export_settlement(settlement) -> dict` | Writes a structured JSON export of a settlement's real fields (from the actual `Settlement` model — nothing invented) to a local `AccountingExport` folder, following the same local-file-fallback shape as the acquisition layer. Never raises. | Does not call QuickBooks or any live API — that's explicitly future work per governance rule 9. Does not decide what triggers an export, or which vendor/format a live integration would target — see §6. |
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

Every open question below needs Mike's answer, not an inference. Per governance rule 8, each includes exactly what's needed to decide.

| # | Question | What's needed to decide |
|---|---|---|
| D1 | Should `archive_load()` enforce the existing `_VALID_TRANSITIONS` table (only `delivered`/`completed` → `archived`)? Today any status can be archived directly, and the table doesn't even list a path for `cancelled` loads to reach `archived` at all, even though that currently works in practice. | Does Mike ever archive a load directly from `cancelled`, `created`, or another non-terminal status today? If yes, the table needs a new entry (`cancelled → archived`, etc.) before any gate is added, not the other way around. |
| D2 | Should the `Load` model gain a `broker_email`/`customer_email` field? Without one, the new customer-notification boundary (§4) has no recipient to resolve automatically — every caller must supply it by hand. | Is this data Mike already tracks somewhere (a broker contact record?), or does it need to be added to the "+New Load" form? |
| D3 | What should trigger a customer-facing completion email, and what should it say? | Which milestone (POD generated? Archive?) should fire it, and does Mike want to approve/edit each one before it sends, or should it be automatic? |
| D4 | What should trigger an accounting export, and to which system? | Per-invoice? Per-payment? A nightly batch? QuickBooks Online API, Desktop file import, or a CSV a bookkeeper handles manually? |
| D5 | Should the DAT/Truckstop load-board adapter be completed? | Which vendor, and what does their actual API response shape look like (the current code assumes a generic `{"loads": [...]}`/list shape that's never been confirmed against a real vendor)? |
| D6 | Is `PORTAL_INQUIRY_MODE` planned functionality or dead config? | It's currently read into `Config` and shown on the settings page but never branched on anywhere. |
| D7 | Should freight-domain email fallbacks move to the `DISPATCH_ARCHIVE_ROOT` tree instead of `DISPATCH_ARCHIVE_PATH` (currently the contract-intel tree)? | A naming/storage-location call, not a bug — worth a decision before Mike goes looking for freight fallback emails in the wrong folder. |
| D8 | Should `archive_load()`'s multi-step write be made atomic? | Requires deciding whether `store.py`'s connection-per-call pattern (used by ~50+ functions) should support a shared/passed-in connection for multi-step operations — a real architectural change, scoped as its own follow-up, not bundled into this pass. |

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

Full test suite (independently confirmed twice by two different workstreams, on unmodified `main`): **2,414/2,414 pass, exit 0.**

---

## 11. Recommended Deployment Sequence

1. **Merge the two pushed branches** (§9) after review — doc fixes first (zero risk), then the defect-fix/boundary branch (tested, additive, but touches more surface).
2. **Answer D1-D8** (§6) — none block a first local load except D1 indirectly (if Mike currently archives from `cancelled`, that needs the transition table updated before any future gating work touches it).
3. **Run one real load locally**, per the corrected `DEPLOY_LOCAL.md` walkthrough — this is still the fastest way to find what the doctrine/business-rule questions actually need to resolve to, rather than pre-deciding them.
4. **Scope D8 (archive atomicity) and the TOCTOU fix separately** before any networked/multi-worker deployment — neither blocks local single-user use.
5. **Build the customer-email and accounting-export triggers** (D2-D4) only after Mike answers what they should do — the boundaries are ready to receive that logic without further code archaeology.
