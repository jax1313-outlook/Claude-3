"""Trip Card — opens when a load becomes Active Load, stays open for the trip.

Closes only when Mike selects Close Load. An empty checklist item means
unfinished work; Close Load is blocked on required items unless Mike
explicitly overrides (and the override is recorded, not silent).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from .models import (
    REQUIRED_TRIP_CARD_ITEMS,
    Load,
    TripCard,
    TripCardItem,
    TripCardItemName,
    TripCardOverride,
    next_id,
)


class TripCardBoard:
    def __init__(self):
        self._cards: Dict[str, TripCard] = {}

    def open(self, load: Load, now: datetime | None = None) -> TripCard:
        now = now or datetime.utcnow()
        items = {
            name: TripCardItem(name=name, required=name in REQUIRED_TRIP_CARD_ITEMS)
            for name in TripCardItemName
        }
        card = TripCard(id=next_id("TRIP"), load_id=load.id, opened_at=now, items=items)
        self._cards[card.id] = card
        load.trip_card_id = card.id
        return card

    def record_event(
        self,
        card_id: str,
        item_name: TripCardItemName,
        evidence_ref: Optional[str] = None,
        now: datetime | None = None,
    ) -> TripCard:
        now = now or datetime.utcnow()
        card = self._cards[card_id]
        if card.closed:
            raise ValueError(f"Trip Card {card_id} is closed; cannot record new events")
        item = card.items[item_name]
        item.completed = True
        item.completed_at = now
        item.evidence_ref = evidence_ref
        return card

    def close(
        self,
        card_id: str,
        mike_override: bool = False,
        override_by: str = "Mike",
        now: datetime | None = None,
    ) -> TripCard:
        now = now or datetime.utcnow()
        card = self._cards[card_id]
        ready, missing = card.is_ready_to_close()
        if not ready:
            if not mike_override:
                names = [m.name.value for m in missing]
                raise ValueError(
                    f"Trip Card {card_id} has unfinished required work: {names}. "
                    f"Close Load must not proceed unless required items are completed "
                    f"or Mike explicitly overrides."
                )
            card.override = TripCardOverride(by=override_by, at=now, open_items=[m.name.value for m in missing])
        card.closed = True
        card.closed_at = now
        return card

    def get(self, card_id: str) -> TripCard:
        return self._cards[card_id]
