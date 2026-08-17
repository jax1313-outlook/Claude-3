"""Communication Card: lifecycle, approved actions, and the Onboarding
Packet bundling rule (resend the full packet, don't micromanage docs)."""

from dispatch_build.models import CommunicationAction, CommunicationStatus
from dispatch_build.store import DispatchStore


def test_communication_card_lifecycle():
    store = DispatchStore()
    card = store.create_communication_card(
        CommunicationAction.BROKER_INTEREST, subject="Lane JAX->ATL", requested_by="broker@example.com"
    )
    assert card.status == CommunicationStatus.DRAFT_NEEDED

    store.draft_communication(card.id)
    assert card.status == CommunicationStatus.DRAFT_READY
    assert card.draft_body

    store.send_communication(card.id)
    assert card.status == CommunicationStatus.SENT
    assert card.email_receipt_id is not None


def test_onboarding_packet_always_sends_full_set():
    store = DispatchStore()
    # Broker asks for a single document ("Insurance Certificate") — subject
    # reflects the specific ask, but the packet action bundles everything.
    card = store.create_communication_card(
        CommunicationAction.ONBOARDING_PACKET,
        subject="Insurance Certificate",
        requested_by="newbroker@example.com",
    )
    store.draft_communication(card.id)

    assert set(card.attachments) == {
        "Insurance Certificate",
        "W9",
        "Authority Letter",
        "Carrier Packet",
        "Company Information",
    }

    store.send_communication(card.id)
    assert card.status == CommunicationStatus.SENT
    sent = store.email_helper._transport.sent
    receipt = next(r for r in sent if r.id == card.email_receipt_id)
    assert set(receipt.attachments) == set(card.attachments)


def test_cannot_send_before_draft_is_ready():
    store = DispatchStore()
    card = store.create_communication_card(
        CommunicationAction.RATE_CON, subject="Load 12345", requested_by="broker@example.com"
    )
    try:
        store.send_communication(card.id)
        assert False, "expected send to be blocked before drafting"
    except ValueError as exc:
        assert "not draft-ready" in str(exc)
