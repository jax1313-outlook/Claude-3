"""Archive — receives completed load records. Freight-only.

This is a separate archive from any SAM / CIN-Lite archive engine.
Nothing here reads or writes contract-intelligence data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from .models import ArchiveRecord, CompletionPacket, Load, TripCard, next_id


class Archive:
    def __init__(self):
        self._records: Dict[str, ArchiveRecord] = {}

    def store(self, load: Load, trip_card: TripCard, completion_packet: CompletionPacket) -> ArchiveRecord:
        record = ArchiveRecord(
            id=next_id("ARCH"),
            load_id=load.id,
            load=load,
            trip_card=trip_card,
            completion_packet=completion_packet,
            archived_at=datetime.utcnow(),
        )
        self._records[load.id] = record
        return record

    def get(self, load_id: str) -> Optional[ArchiveRecord]:
        return self._records.get(load_id)

    def all(self):
        return list(self._records.values())
