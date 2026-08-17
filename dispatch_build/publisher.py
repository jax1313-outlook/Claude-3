"""Publisher — drafts documents and messages from approved Library input.

Publisher creates. Publisher never sends (Email Helper transports) and
never decides (Mike decides). Every draft here is built only from
Library templates / approved assets, never invented.
"""

from __future__ import annotations

from datetime import datetime

from .library import Library
from .models import (
    CommunicationAction,
    CommunicationCard,
    CommunicationStatus,
    Load,
    TripCard,
    next_id,
)


class Publisher:
    def __init__(self, library: Library):
        self._library = library

    def assemble_completion_message(self, load: Load, trip_card: TripCard) -> str:
        ready, missing = trip_card.is_ready_to_close()
        if not ready and not trip_card.override:
            raise ValueError(
                f"Publisher cannot assemble a completion message for an open "
                f"Trip Card; missing required items: {[m.name.value for m in missing]}"
            )
        template = self._library.get_template("completion_message")
        return template.format(
            broker=load.broker,
            load_id=load.id,
            origin=load.origin,
            destination=load.destination,
        )

    def create_communication_card(
        self, action: CommunicationAction, subject: str, requested_by: str
    ) -> CommunicationCard:
        return CommunicationCard(
            id=next_id("COMM"),
            action=action,
            subject=subject,
            requested_by=requested_by,
            created_at=datetime.utcnow(),
            status=CommunicationStatus.DRAFT_NEEDED,
        )

    def draft_communication(self, card: CommunicationCard) -> CommunicationCard:
        """Draft the card's body from approved Library material only."""
        if card.action == CommunicationAction.ONBOARDING_PACKET:
            # Operational simplicity rule: always attach the full standard
            # packet, regardless of which single document was requested.
            docs = self._library.get_onboarding_packet_documents()
            card.attachments = list(docs)
            card.draft_body = (
                f"Attached: {', '.join(docs)}.\n\nThank you for using Level 1 Transport."
            )
        elif card.action == CommunicationAction.BROKER_INTEREST:
            card.draft_body = f"Level 1 Transport is interested in: {card.subject}."
        elif card.action == CommunicationAction.RATE_CON:
            card.draft_body = f"Please find the rate confirmation request for: {card.subject}."
        elif card.action == CommunicationAction.CAPABILITY_STATEMENT:
            card.draft_body = "Level 1 Transport capability statement attached."
            card.attachments = ["Capability Statement"]
        elif card.action == CommunicationAction.COMPANY_HELP:
            card.draft_body = f"Company support request: {card.subject}."
        else:  # pragma: no cover - exhaustive over CommunicationAction
            raise ValueError(f"Unapproved communication action: {card.action}")

        card.status = CommunicationStatus.DRAFT_READY
        return card
