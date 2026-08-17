"""Proves the SAM/freight Sandbox scoping requirement flagged in
DISPATCH_PROMOTION_PLAN_FIRST_LIVE_LOAD.md item 4 and item 6.

Dispatch's real Sandbox is shared between freight loads and SAM/CIN-Lite
opportunities. This build stays freight-only and never itself creates a
non-freight entry -- but these tests construct one directly (exactly as
Dispatch's real shared Sandbox would receive from the SAM side) to prove
that freight operations (commit side-effects, the HOLD sweep, the
Operations Cockpit) can never see or touch it, even when it sits in the
same store as freight entries.
"""

from datetime import datetime, timedelta

from dispatch_build.models import SandboxStatus
from dispatch_build.store import DispatchStore

FOREIGN_SOURCE = "sam"  # stand-in for a SAM/CIN-Lite sandbox entry; no SAM logic is implemented or assumed


def test_sandbox_ids_carry_the_dispatch_source_convention():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    load = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    entry = store.send_to_sandbox(load.id, now=now)
    assert entry.id.startswith("SBX-DISPATCH-")
    assert entry.source_type == "dispatch"


def test_commit_never_flips_a_foreign_sibling_to_runner_up():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    freight_load = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    freight_entry = store.send_to_sandbox(freight_load.id, now=now)

    # A SAM-sourced entry sitting OPEN in the same sandbox at the same time,
    # exactly as it would in Dispatch's real shared Sandbox.
    foreign_entry = store.sandbox.add("CONTRACT-9999", source_type=FOREIGN_SOURCE, now=now)

    store.commit_load(freight_entry.id, now=now)

    refreshed_foreign = store.sandbox.get(foreign_entry.id)
    assert refreshed_foreign.status == SandboxStatus.OPEN  # untouched
    assert refreshed_foreign.hold_expires_at is None  # HOLD clock never started for it


def test_commit_load_refuses_a_non_freight_sandbox_id():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    foreign_entry = store.sandbox.add("CONTRACT-9999", source_type=FOREIGN_SOURCE, now=now)

    try:
        store.commit_load(foreign_entry.id, now=now)
        assert False, "expected commit_load to refuse a non-freight sandbox entry"
    except ValueError as exc:
        assert "freight-sourced" in str(exc)


def test_hold_sweep_never_deletes_a_foreign_entry_even_if_it_reaches_runner_up():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    # Simulate a hypothetical bug elsewhere that got a foreign entry into
    # RUNNER_UP with an expired HOLD clock -- the sweep's own source_type
    # filter must still refuse to touch it, not merely rely on it never
    # reaching this state through normal freight code paths.
    foreign_entry = store.sandbox.add("CONTRACT-9999", source_type=FOREIGN_SOURCE, now=now)
    foreign_entry.status = SandboxStatus.RUNNER_UP
    foreign_entry.hold_expires_at = now - timedelta(minutes=1)

    deleted = store.run_hold_sweep(now=now)

    assert deleted == []
    assert store.sandbox.get(foreign_entry.id) is not None  # still present, untouched


def test_cockpit_never_surfaces_a_foreign_sandbox_entry():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    freight_load = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    store.send_to_sandbox(freight_load.id, now=now)
    foreign_entry = store.sandbox.add("CONTRACT-9999", source_type=FOREIGN_SOURCE, now=now)

    view = store.cockpit_view(now=now)

    assert all(c["sandbox_id"] != foreign_entry.id for c in view["sandbox"])
    assert all(d.get("sandbox_id") != foreign_entry.id for d in view["decisions"])

    # Also true once the foreign entry is (hypothetically) runner-up and near expiry.
    foreign_entry.status = SandboxStatus.RUNNER_UP
    foreign_entry.hold_expires_at = now + timedelta(minutes=30)
    view = store.cockpit_view(now=now)
    assert all(a.get("sandbox_id") != foreign_entry.id for a in view["awareness"])
