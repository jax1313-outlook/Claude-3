"""DispatchStore — orchestrates the First Live Load workflow end to end.

Freight only. This is the single entry point a demo, a test, or (later)
a real Portal would call. It does not import or reference SAM /
CIN-Lite / Manager.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .accounting import AccountingAdapter
from .archive import Archive
from .email_helper import EmailHelper, MockOutlookTransport
from .library import Library
from .models import (
    SANDBOX_SOURCE_FREIGHT,
    CommunicationAction,
    CommunicationCard,
    CommunicationStatus,
    CompletionPacket,
    Load,
    LoadStatus,
    TripCard,
    TripCardItemName,
    next_id,
)
from .publisher import Publisher
from .sandbox import Sandbox
from .trip_card import TripCardBoard


class DispatchStore:
    def __init__(self, email_transport=None):
        self.loads: Dict[str, Load] = {}
        self.sandbox = Sandbox()
        self.trip_card_board = TripCardBoard()
        self.communication_cards: Dict[str, CommunicationCard] = {}
        self.completion_packets: Dict[str, CompletionPacket] = {}

        self.library = Library()
        self.publisher = Publisher(self.library)
        self.email_helper = EmailHelper(email_transport or MockOutlookTransport())
        self.accounting = AccountingAdapter()
        self.archive = Archive()

    # -- Step 1: intake -----------------------------------------------------
    def intake_load(self, origin: str, destination: str, broker: str, rate: float, now=None) -> Load:
        now = now or datetime.utcnow()
        load = Load(
            id=next_id("LOAD"),
            origin=origin,
            destination=destination,
            broker=broker,
            rate=rate,
            created_at=now,
        )
        self.loads[load.id] = load
        return load

    # -- Step 2: evaluate -----------------------------------------------------
    def evaluate_load(self, load_id: str, score: float) -> Load:
        load = self.loads[load_id]
        load.score = score
        load.status = LoadStatus.EVALUATED
        return load

    # -- Step 3: move to sandbox ---------------------------------------------
    def send_to_sandbox(self, load_id: str, now=None):
        load = self.loads[load_id]
        entry = self.sandbox.add(load.id, source_type=SANDBOX_SOURCE_FREIGHT, now=now)
        load.sandbox_id = entry.id
        load.status = LoadStatus.SANDBOX
        return entry

    # -- Step 4-5: commit -> Active Load --------------------------------------
    def commit_load(self, sandbox_id: str, now=None):
        entry, runner_ups = self.sandbox.commit(sandbox_id, now=now)
        if entry.source_type != SANDBOX_SOURCE_FREIGHT:
            # Defense in depth: this call path is freight-only. A non-freight
            # sandbox_id reaching here means a caller bug upstream, not a
            # state this store should ever act on.
            raise ValueError(
                f"commit_load() can only commit freight-sourced sandbox entries; "
                f"{sandbox_id} is source_type={entry.source_type!r}"
            )

        load = self.loads[entry.load_id]
        load.status = LoadStatus.ACTIVE

        for sibling in runner_ups:
            sibling_load = self.loads.get(sibling.load_id)
            if sibling_load:
                sibling_load.status = LoadStatus.RUNNER_UP

        # -- Step 6: Trip Card opens
        self.trip_card_board.open(load, now=now)
        return load

    # -- Step 7-8: trip card events -------------------------------------------
    def record_trip_event(self, load_id: str, item_name: TripCardItemName, evidence_ref=None, now=None):
        load = self.loads[load_id]
        return self.trip_card_board.record_event(load.trip_card_id, item_name, evidence_ref, now=now)

    # -- HOLD sweep (runner-up expiration) -------------------------------------
    def run_hold_sweep(self, now=None) -> List[str]:
        """Delete expired runner-up sandbox entries. Deleted, not archived.
        Explicitly freight-scoped -- this store never sweeps any other
        program's sandbox entries, even ones sharing the same Sandbox."""
        return self.sandbox.run_hold_sweep(source_type=SANDBOX_SOURCE_FREIGHT, now=now)

    # -- Step 9-15: Close Load -> Completion Packet -> Archive -----------------
    def close_load(
        self,
        load_id: str,
        invoice_ref: Optional[str] = None,
        mike_override: bool = False,
        now=None,
    ) -> Load:
        load = self.loads[load_id]
        card: TripCard = self.trip_card_board.get(load.trip_card_id)

        # Step 9: Mike manually selects Close Load (gated by Trip Card).
        self.trip_card_board.close(card.id, mike_override=mike_override, now=now)

        # Step 10-11: Completion Packet (Invoice + Signed BOL + POD).
        packet = CompletionPacket(
            id=next_id("PKT"),
            load_id=load.id,
            trip_card_id=card.id,
            invoice_ref=invoice_ref or next_id("INV"),
            bol_ref=card.items[TripCardItemName.BOL].evidence_ref or "MISSING-BOL",
            pod_ref=card.items[TripCardItemName.POD].evidence_ref or "MISSING-POD",
            created_at=now or datetime.utcnow(),
        )

        # Step 12: Publisher assembles the completion message from a Library template.
        packet.publisher_message = self.publisher.assemble_completion_message(load, card)

        # Step 13: Email Helper transports through the (mocked) Outlook boundary.
        receipt = self.email_helper.send(
            to=load.broker,
            subject=f"Load {load.id} complete — Completion Packet attached",
            body=packet.publisher_message,
            attachments=[packet.invoice_ref, packet.bol_ref, packet.pod_ref],
        )
        packet.email_receipt_id = receipt.id

        # Step 14: Accounting handoff (mocked).
        acct_receipt = self.accounting.handoff(packet)
        packet.accounting_receipt_id = acct_receipt.id

        self.completion_packets[packet.id] = packet
        load.completion_packet_id = packet.id
        load.status = LoadStatus.COMPLETED

        # Step 15: Archive receives the completed load record.
        self.archive.store(load, card, packet)
        load.status = LoadStatus.ARCHIVED

        return load

    # -- Communication Card workflow (independent of the Load flow) -----------
    def create_communication_card(self, action: CommunicationAction, subject: str, requested_by: str) -> CommunicationCard:
        card = self.publisher.create_communication_card(action, subject, requested_by)
        self.communication_cards[card.id] = card
        return card

    def draft_communication(self, card_id: str) -> CommunicationCard:
        card = self.communication_cards[card_id]
        return self.publisher.draft_communication(card)

    def send_communication(self, card_id: str) -> CommunicationCard:
        card = self.communication_cards[card_id]
        if card.status != CommunicationStatus.DRAFT_READY:
            raise ValueError(f"Communication Card {card_id} is not draft-ready (status={card.status})")
        receipt = self.email_helper.send(
            to=card.requested_by,
            subject=f"{card.action.value}: {card.subject}",
            body=card.draft_body or "",
            attachments=card.attachments,
        )
        card.email_receipt_id = receipt.id
        card.status = CommunicationStatus.SENT
        return card

    # -- Operations Cockpit ----------------------------------------------------
    def cockpit_view(self, now=None) -> dict:
        from .cockpit import build_cockpit_view

        return build_cockpit_view(self, now=now)
