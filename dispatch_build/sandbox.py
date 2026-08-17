"""Sandbox — active work, not storage.

A load lives in Sandbox while it's being evaluated against competing
options. When Mike commits one entry, every sibling entry for the same
decision becomes a runner-up and starts a 3-hour HOLD clock. Expired
runner-ups are deleted, not archived — HOLD is for stale options, not
for records worth keeping.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from .models import HOLD_HOURS, Load, LoadStatus, SandboxEntry, SandboxStatus, next_id


class Sandbox:
    def __init__(self):
        self._entries: Dict[str, SandboxEntry] = {}

    def add(self, load: Load, now: datetime | None = None) -> SandboxEntry:
        now = now or datetime.utcnow()
        entry = SandboxEntry(id=next_id("SBX"), load_id=load.id, status=SandboxStatus.OPEN, entered_at=now)
        self._entries[entry.id] = entry
        load.sandbox_id = entry.id
        load.status = LoadStatus.SANDBOX
        return entry

    def siblings_of(self, entry: SandboxEntry) -> List[SandboxEntry]:
        """Every other still-open entry — the runner-up pool for a commit decision."""
        return [
            e for e in self._entries.values()
            if e.id != entry.id and e.status == SandboxStatus.OPEN
        ]

    def commit(self, entry_id: str, loads: Dict[str, Load], now: datetime | None = None) -> SandboxEntry:
        now = now or datetime.utcnow()
        entry = self._entries[entry_id]
        if entry.status != SandboxStatus.OPEN:
            raise ValueError(f"Sandbox entry {entry_id} is not open (status={entry.status})")

        for sibling in self.siblings_of(entry):
            sibling.status = SandboxStatus.RUNNER_UP
            sibling.hold_started_at = now
            sibling.hold_expires_at = now + timedelta(hours=HOLD_HOURS)
            sibling_load = loads.get(sibling.load_id)
            if sibling_load:
                sibling_load.status = LoadStatus.RUNNER_UP

        entry.status = SandboxStatus.COMMITTED
        committed_load = loads[entry.load_id]
        committed_load.status = LoadStatus.ACTIVE
        return entry

    def run_hold_sweep(self, now: datetime | None = None) -> List[str]:
        """Delete (not archive) every runner-up entry whose HOLD has expired.

        Returns the ids of deleted entries.
        """
        now = now or datetime.utcnow()
        expired_ids = [
            e.id for e in self._entries.values()
            if e.status == SandboxStatus.RUNNER_UP and e.hold_expires_at and now >= e.hold_expires_at
        ]
        for entry_id in expired_ids:
            del self._entries[entry_id]
        return expired_ids

    def get(self, entry_id: str) -> SandboxEntry:
        return self._entries[entry_id]

    def all(self) -> List[SandboxEntry]:
        return list(self._entries.values())
