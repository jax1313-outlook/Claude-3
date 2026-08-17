"""Operations Cockpit: proves the six required work-queues can be built
from live state, and that they read Mike-facing decisions/awareness
correctly — not a UI test, a shape test."""

from datetime import datetime, timedelta

from dispatch_build.models import CommunicationAction, TripCardItemName
from dispatch_build.store import DispatchStore


def test_cockpit_has_all_required_queues():
    store = DispatchStore()
    view = store.cockpit_view()
    assert set(view.keys()) == {
        "awareness",
        "decisions",
        "communications",
        "trip_cards",
        "active_loads",
        "sandbox",
    }


def test_cockpit_surfaces_open_sandbox_decision():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    load = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    entry = store.send_to_sandbox(load.id, now=now)

    view = store.cockpit_view(now=now)
    assert any(d["type"] == "commit_load" and d["sandbox_id"] == entry.id for d in view["decisions"])


def test_cockpit_surfaces_ready_to_close_decision_and_active_load():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    load = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    entry = store.send_to_sandbox(load.id, now=now)
    store.commit_load(entry.id, now=now)
    for item in (
        TripCardItemName.ARRIVAL,
        TripCardItemName.PICKUP,
        TripCardItemName.BOL,
        TripCardItemName.LOAD_CHECK,
        TripCardItemName.DELIVERY,
        TripCardItemName.POD,
    ):
        store.record_trip_event(load.id, item, now=now)

    view = store.cockpit_view(now=now)
    assert any(d["type"] == "close_load" and d["load_id"] == load.id for d in view["decisions"])
    assert any(a["load_id"] == load.id for a in view["active_loads"])


def test_cockpit_surfaces_hold_expiring_soon_awareness():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    winner = store.intake_load("A", "B", "Broker A", 1000.0, now=now)
    loser = store.intake_load("A", "B", "Broker A", 950.0, now=now)
    winner_entry = store.send_to_sandbox(winner.id, now=now)
    store.send_to_sandbox(loser.id, now=now)
    store.commit_load(winner_entry.id, now=now)

    almost_expired = now + timedelta(hours=2, minutes=30)
    view = store.cockpit_view(now=almost_expired)
    assert any(a["type"] == "hold_expiring_soon" and a["load_id"] == loser.id for a in view["awareness"])


def test_cockpit_surfaces_open_communication_card():
    store = DispatchStore()
    card = store.create_communication_card(
        CommunicationAction.CAPABILITY_STATEMENT, subject="New broker ask", requested_by="broker@example.com"
    )
    view = store.cockpit_view()
    assert any(c["communication_id"] == card.id for c in view["communications"])
