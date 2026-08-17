"""Sandbox — active work, not storage.

Dispatch's real Sandbox is shared infrastructure: freight loads and SAM /
CIN-Lite opportunities both live in it, distinguished only by a
source_type tag. This class is written to that reality on purpose, even
though this build never itself creates a non-freight entry — every
operation that could cross-affect entries (commit side-effects, the HOLD
sweep) filters on source_type explicitly, so a promoted version of this
code cannot silently touch SAM entries just because they happen to share
the same store.

Sandbox does not know about Load objects. Freight-specific side effects
(marking a Load ACTIVE or RUNNER_UP) belong to the caller (see
store.py), not to this shared, program-agnostic class.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .models import HOLD_HOURS, SANDBOX_SOURCE_FREIGHT, SandboxEntry, SandboxStatus

_sandbox_ids = itertools.count(1)


def _next_sandbox_id(source_type: str) -> str:
    # Matches Dispatch's real convention: SBX-{SOURCE_TYPE}-{n}
    return f"SBX-{source_type.upper()}-{next(_sandbox_ids):06d}"


class Sandbox:
    def __init__(self):
        self._entries: Dict[str, SandboxEntry] = {}

    def add(self, load_id: str, source_type: str = SANDBOX_SOURCE_FREIGHT, now: datetime | None = None) -> SandboxEntry:
        now = now or datetime.utcnow()
        entry = SandboxEntry(
            id=_next_sandbox_id(source_type),
            load_id=load_id,
            source_type=source_type,
            status=SandboxStatus.OPEN,
            entered_at=now,
        )
        self._entries[entry.id] = entry
        return entry

    def siblings_of(self, entry: SandboxEntry) -> List[SandboxEntry]:
        """Every other still-open entry in the SAME program — the runner-up
        pool for a commit decision. A freight commit must never be able to
        flip a SAM entry (or vice versa) into runner-up status just because
        they happen to be open at the same time."""
        return [
            e for e in self._entries.values()
            if e.id != entry.id
            and e.status == SandboxStatus.OPEN
            and e.source_type == entry.source_type
        ]

    def commit(self, entry_id: str, now: datetime | None = None) -> Tuple[SandboxEntry, List[SandboxEntry]]:
        """Commit one entry; every same-program sibling becomes a runner-up
        with a HOLD clock started. Returns (committed_entry, runner_ups) —
        the caller applies any domain-specific side effects (e.g. marking
        a freight Load ACTIVE or RUNNER_UP)."""
        now = now or datetime.utcnow()
        entry = self._entries[entry_id]
        if entry.status != SandboxStatus.OPEN:
            raise ValueError(f"Sandbox entry {entry_id} is not open (status={entry.status})")

        runner_ups = self.siblings_of(entry)
        for sibling in runner_ups:
            sibling.status = SandboxStatus.RUNNER_UP
            sibling.hold_started_at = now
            sibling.hold_expires_at = now + timedelta(hours=HOLD_HOURS)

        entry.status = SandboxStatus.COMMITTED
        return entry, runner_ups

    def run_hold_sweep(self, source_type: str = SANDBOX_SOURCE_FREIGHT, now: datetime | None = None) -> List[str]:
        """Delete (not archive) every runner-up entry, IN THE GIVEN PROGRAM
        ONLY, whose HOLD has expired. Defaults to freight — a caller must
        explicitly opt in to sweep any other program's entries, rather than
        the sweep silently touching whatever happens to be in the store.

        Returns the ids of deleted entries.
        """
        now = now or datetime.utcnow()
        expired_ids = [
            e.id for e in self._entries.values()
            if e.status == SandboxStatus.RUNNER_UP
            and e.source_type == source_type
            and e.hold_expires_at and now >= e.hold_expires_at
        ]
        for entry_id in expired_ids:
            del self._entries[entry_id]
        return expired_ids

    def get(self, entry_id: str) -> SandboxEntry:
        return self._entries[entry_id]

    def all(self, source_type: str | None = None) -> List[SandboxEntry]:
        """All entries, or all entries for one program if source_type is given."""
        entries = list(self._entries.values())
        if source_type is not None:
            entries = [e for e in entries if e.source_type == source_type]
        return entries
