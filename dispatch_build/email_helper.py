"""Email Helper — transports/routes messages through the Outlook boundary.

Email Helper does not become Outlook, does not own templates, does not
own load state, and does not decide. It receives an already-assembled
body (from Publisher) and an already-approved recipient, and hands it
to a transport. For First Live Load, the transport is mocked; a real
Outlook/Graph transport can be swapped in later behind the same
interface without touching any caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Protocol

from .models import next_id


@dataclass
class SendReceipt:
    id: str
    to: str
    subject: str
    sent_at: datetime
    mocked: bool
    attachments: List[str] = field(default_factory=list)


class Transport(Protocol):
    def send(self, to: str, subject: str, body: str, attachments: List[str]) -> SendReceipt:
        ...


class MockOutlookTransport:
    """Stands in for a live Outlook/Graph transport.

    Records every send instead of dispatching real mail, so tests and the
    demo can assert a handoff actually happened without a live mailbox.
    """

    def __init__(self):
        self.sent: List[SendReceipt] = []

    def send(self, to: str, subject: str, body: str, attachments: List[str]) -> SendReceipt:
        receipt = SendReceipt(
            id=next_id("MAIL"),
            to=to,
            subject=subject,
            sent_at=datetime.utcnow(),
            mocked=True,
            attachments=list(attachments),
        )
        self.sent.append(receipt)
        return receipt


class EmailHelper:
    def __init__(self, transport: Transport):
        self._transport = transport

    def send(self, to: str, subject: str, body: str, attachments: List[str] | None = None) -> SendReceipt:
        return self._transport.send(to, subject, body, attachments or [])
