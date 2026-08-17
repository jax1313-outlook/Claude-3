"""Accounting handoff — mocked. Accounting stays external per doctrine.

This adapter never becomes an accounting system. It produces a receipt
proving a handoff occurred, so downstream code and tests can verify the
step happened, without requiring a live QuickBooks (or any other)
integration. Vendor choice (QBO vs Desktop vs CSV export) is an open
implementation decision, deliberately not forced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import CompletionPacket, next_id


@dataclass
class AccountingHandoffReceipt:
    id: str
    completion_packet_id: str
    handed_off_at: datetime
    mocked: bool


class AccountingAdapter:
    def handoff(self, completion_packet: CompletionPacket) -> AccountingHandoffReceipt:
        return AccountingHandoffReceipt(
            id=next_id("ACCT"),
            completion_packet_id=completion_packet.id,
            handed_off_at=datetime.utcnow(),
            mocked=True,
        )
