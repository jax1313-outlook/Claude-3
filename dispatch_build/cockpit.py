"""Operations Cockpit — the working interface, organized around work.

Not a dashboard. Not a department menu. This is a minimal, testable
representation (queue-shaped data, not a rendered UI) proving the six
required queues can be assembled from live workflow state: Awareness,
Decisions, Communications, Trip Cards, Active Loads, Sandbox.

A full UI is out of scope for First Live Load; this proves the shape
a UI would render.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .models import CommunicationStatus, LoadStatus, SandboxStatus


def build_cockpit_view(store, now: datetime | None = None) -> dict:
    now = now or datetime.utcnow()

    active_loads = [
        {"load_id": l.id, "origin": l.origin, "destination": l.destination, "broker": l.broker}
        for l in store.loads.values()
        if l.status == LoadStatus.ACTIVE
    ]

    trip_cards = [
        {
            "trip_card_id": c.id,
            "load_id": c.load_id,
            "complete_fraction": c.completion_fraction(),
            "open_required_items": [m.name.value for m in c.missing_required_items()],
            "closed": c.closed,
        }
        for c in store.trip_card_board._cards.values()
    ]

    sandbox_cards = [
        {
            "sandbox_id": e.id,
            "load_id": e.load_id,
            "status": e.status.value,
            "hold_expires_at": e.hold_expires_at.isoformat() if e.hold_expires_at else None,
        }
        for e in store.sandbox.all()
    ]

    communications = [
        {
            "communication_id": c.id,
            "action": c.action.value,
            "subject": c.subject,
            "status": c.status.value,
        }
        for c in store.communication_cards.values()
        if c.status not in (CommunicationStatus.COMPLETED, CommunicationStatus.CLOSED)
    ]

    # Decisions: things only Mike can move forward.
    decisions = []
    for e in store.sandbox.all():
        if e.status == SandboxStatus.OPEN:
            decisions.append({"type": "commit_load", "sandbox_id": e.id, "load_id": e.load_id})
    for c in store.trip_card_board._cards.values():
        if not c.closed and c.is_ready_to_close()[0]:
            decisions.append({"type": "close_load", "trip_card_id": c.id, "load_id": c.load_id})

    # Awareness: informational, non-gating signals worth Mike seeing.
    awareness = []
    for e in store.sandbox.all():
        if e.status == SandboxStatus.RUNNER_UP and e.hold_expires_at:
            remaining = e.hold_expires_at - now
            if remaining <= timedelta(hours=1):
                awareness.append(
                    {
                        "type": "hold_expiring_soon",
                        "sandbox_id": e.id,
                        "load_id": e.load_id,
                        "expires_at": e.hold_expires_at.isoformat(),
                    }
                )
    for c in store.trip_card_board._cards.values():
        for item in c.items.values():
            if item.name.value == "delay" and item.completed:
                awareness.append({"type": "delay_recorded", "trip_card_id": c.id, "load_id": c.load_id})

    return {
        "awareness": awareness,
        "decisions": decisions,
        "communications": communications,
        "trip_cards": trip_cards,
        "active_loads": active_loads,
        "sandbox": sandbox_cards,
    }
