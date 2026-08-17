"""HOLD: runner-up loads get a 3-hour clock, then are deleted, not archived."""

from datetime import datetime, timedelta

from dispatch_build.models import LoadStatus, SandboxStatus
from dispatch_build.store import DispatchStore


def test_runner_up_starts_hold_clock_on_commit():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    winner = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    loser = store.intake_load("A", "B", "Broker A", 950.0, now=now)
    store.evaluate_load(winner.id, score=0.9)
    store.evaluate_load(loser.id, score=0.6)

    winner_entry = store.send_to_sandbox(winner.id, now=now)
    loser_entry = store.send_to_sandbox(loser.id, now=now)

    store.commit_load(winner_entry.id, now=now)

    refreshed_loser_entry = store.sandbox.get(loser_entry.id)
    assert refreshed_loser_entry.status == SandboxStatus.RUNNER_UP
    assert loser.status == LoadStatus.RUNNER_UP
    assert refreshed_loser_entry.hold_expires_at == now + timedelta(hours=3)


def test_hold_sweep_does_not_delete_before_expiry():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    winner = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    loser = store.intake_load("A", "B", "Broker A", 950.0, now=now)
    winner_entry = store.send_to_sandbox(winner.id, now=now)
    loser_entry = store.send_to_sandbox(loser.id, now=now)
    store.commit_load(winner_entry.id, now=now)

    two_hours_later = now + timedelta(hours=2)
    deleted = store.run_hold_sweep(now=two_hours_later)

    assert deleted == []
    assert store.sandbox.get(loser_entry.id) is not None  # still present


def test_hold_sweep_deletes_after_expiry_and_does_not_archive():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    winner = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    loser = store.intake_load("A", "B", "Broker A", 950.0, now=now)
    winner_entry = store.send_to_sandbox(winner.id, now=now)
    loser_entry = store.send_to_sandbox(loser.id, now=now)
    store.commit_load(winner_entry.id, now=now)

    three_hours_one_minute_later = now + timedelta(hours=3, minutes=1)
    deleted = store.run_hold_sweep(now=three_hours_one_minute_later)

    assert deleted == [loser_entry.id]
    try:
        store.sandbox.get(loser_entry.id)
        assert False, "expected expired runner-up entry to be deleted"
    except KeyError:
        pass

    # Deleted, not archived: no archive record should exist for the loser.
    assert store.archive.get(loser.id) is None
