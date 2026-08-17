"""Domain model for the First Live Load workflow.

Freight only. Every object here represents a concept named in the
approved build doctrine (Load, Sandbox, Trip Card, Completion Packet,
Communication Card). Nothing here represents SAM / CIN-Lite / federal
contract intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import itertools

_ids = itertools.count(1)


def next_id(prefix: str) -> str:
    return f"{prefix}-{next(_ids):06d}"


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

class LoadStatus(str, Enum):
    INTAKE = "intake"
    EVALUATED = "evaluated"
    SANDBOX = "sandbox"
    RUNNER_UP = "runner_up"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Load:
    id: str
    origin: str
    destination: str
    broker: str
    rate: float
    created_at: datetime
    status: LoadStatus = LoadStatus.INTAKE
    score: Optional[float] = None
    sandbox_id: Optional[str] = None
    trip_card_id: Optional[str] = None
    completion_packet_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------

class SandboxStatus(str, Enum):
    OPEN = "open"
    RUNNER_UP = "runner_up"
    COMMITTED = "committed"
    EXPIRED = "expired"


HOLD_HOURS = 3


@dataclass
class SandboxEntry:
    id: str
    load_id: str
    status: SandboxStatus = SandboxStatus.OPEN
    entered_at: datetime = None
    hold_started_at: Optional[datetime] = None
    hold_expires_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Trip Card
# ---------------------------------------------------------------------------

class TripCardItemName(str, Enum):
    ARRIVAL = "arrival"
    PICKUP = "pickup"
    BOL = "bol"
    LOAD_CHECK = "load_check"
    DELAY = "delay"
    DELIVERY = "delivery"
    POD = "pod"


# Delay is intentionally not required — see DISPATCH_EXISTING_ASSET_PROOF.md
REQUIRED_TRIP_CARD_ITEMS = (
    TripCardItemName.ARRIVAL,
    TripCardItemName.PICKUP,
    TripCardItemName.BOL,
    TripCardItemName.LOAD_CHECK,
    TripCardItemName.DELIVERY,
    TripCardItemName.POD,
)


@dataclass
class TripCardItem:
    name: TripCardItemName
    required: bool
    completed: bool = False
    completed_at: Optional[datetime] = None
    evidence_ref: Optional[str] = None


@dataclass
class TripCardOverride:
    by: str
    at: datetime
    open_items: list


@dataclass
class TripCard:
    id: str
    load_id: str
    opened_at: datetime
    items: dict  # TripCardItemName -> TripCardItem
    closed: bool = False
    closed_at: Optional[datetime] = None
    override: Optional[TripCardOverride] = None

    def open_items(self):
        return [i for i in self.items.values() if not i.completed]

    def missing_required_items(self):
        return [i for i in self.open_items() if i.required]

    def is_ready_to_close(self):
        missing = self.missing_required_items()
        return (len(missing) == 0, missing)

    def completion_fraction(self) -> float:
        total = len(self.items)
        done = sum(1 for i in self.items.values() if i.completed)
        return done / total if total else 0.0


# ---------------------------------------------------------------------------
# Completion Packet
# ---------------------------------------------------------------------------

@dataclass
class CompletionPacket:
    id: str
    load_id: str
    trip_card_id: str
    invoice_ref: str
    bol_ref: str
    pod_ref: str
    created_at: datetime
    publisher_message: Optional[str] = None
    email_receipt_id: Optional[str] = None
    accounting_receipt_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Communication Card
# ---------------------------------------------------------------------------

class CommunicationAction(str, Enum):
    BROKER_INTEREST = "broker_interest"
    ONBOARDING_PACKET = "onboarding_packet"
    RATE_CON = "rate_con"
    CAPABILITY_STATEMENT = "capability_statement"
    COMPANY_HELP = "company_help"


class CommunicationStatus(str, Enum):
    REQUESTED = "requested"
    DRAFT_NEEDED = "draft_needed"
    DRAFT_READY = "draft_ready"
    SENT = "sent"
    WAITING_REPLY = "waiting_reply"
    COMPLETED = "completed"
    CLOSED = "closed"


@dataclass
class CommunicationCard:
    id: str
    action: CommunicationAction
    subject: str
    requested_by: str
    created_at: datetime
    status: CommunicationStatus = CommunicationStatus.REQUESTED
    draft_body: Optional[str] = None
    attachments: list = field(default_factory=list)
    email_receipt_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Archive
# ---------------------------------------------------------------------------

@dataclass
class ArchiveRecord:
    id: str
    load_id: str
    load: Load
    trip_card: TripCard
    completion_packet: CompletionPacket
    archived_at: datetime
