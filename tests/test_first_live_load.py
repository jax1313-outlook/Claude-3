"""End-to-end proof: one load moves from intake through archive
under Mike-controlled workflow. This is the Definition of Done test."""

from datetime import datetime

from dispatch_build.models import LoadStatus, TripCardItemName
from dispatch_build.store import DispatchStore


def test_first_live_load_end_to_end():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    # 1. Load enters Dispatch.
    load = store.intake_load(
        origin="Jacksonville, FL", destination="Atlanta, GA", broker="Acme Freight Co", rate=1450.0, now=now
    )
    assert load.status == LoadStatus.INTAKE

    # 2. Load can be evaluated.
    store.evaluate_load(load.id, score=0.82)
    assert load.status == LoadStatus.EVALUATED

    # 3. Load can move to Sandbox.
    entry = store.send_to_sandbox(load.id, now=now)
    assert load.status == LoadStatus.SANDBOX

    # 4-5. Mike commits the load -> Active Load created, Trip Card opens.
    active_load = store.commit_load(entry.id, now=now)
    assert active_load.status == LoadStatus.ACTIVE
    assert active_load.trip_card_id is not None

    trip_card = store.trip_card_board.get(active_load.trip_card_id)
    assert trip_card.closed is False
    assert len(trip_card.items) == 7
    assert all(not item.completed for item in trip_card.items.values())

    # 7-8. Trip Card tracks deterministic driver events; empty = unfinished.
    ready, missing = trip_card.is_ready_to_close()
    assert ready is False
    assert len(missing) == 6  # all required items still open (Delay is not required)

    store.record_trip_event(load.id, TripCardItemName.ARRIVAL, evidence_ref="gps-ping-1", now=now)
    store.record_trip_event(load.id, TripCardItemName.PICKUP, evidence_ref="driver-checkin-1", now=now)
    store.record_trip_event(load.id, TripCardItemName.BOL, evidence_ref="bol-scan-001.pdf", now=now)
    store.record_trip_event(load.id, TripCardItemName.LOAD_CHECK, evidence_ref="load-check-ok", now=now)
    store.record_trip_event(load.id, TripCardItemName.DELIVERY, evidence_ref="gps-ping-2", now=now)
    store.record_trip_event(load.id, TripCardItemName.POD, evidence_ref="pod-scan-001.pdf", now=now)
    # Delay intentionally left empty — no delay occurred on this load.

    ready, missing = trip_card.is_ready_to_close()
    assert ready is True
    assert missing == []

    # 9. Mike manually selects Close Load. 10-15 cascade from it.
    archived_load = store.close_load(load.id, now=now)
    assert archived_load.status == LoadStatus.ARCHIVED

    # 10-11. Completion Packet exists and carries Invoice + Signed BOL + POD.
    packet = store.completion_packets[archived_load.completion_packet_id]
    assert packet.bol_ref == "bol-scan-001.pdf"
    assert packet.pod_ref == "pod-scan-001.pdf"
    assert packet.invoice_ref

    # 12. Publisher message uses the Library template.
    assert "Thank you for using Level 1 Transport." in packet.publisher_message
    assert load.id in packet.publisher_message

    # 13. Email Helper (mocked Outlook boundary) transported the packet.
    assert packet.email_receipt_id is not None
    sent = store.email_helper._transport.sent
    assert any(r.id == packet.email_receipt_id for r in sent)
    receipt = next(r for r in sent if r.id == packet.email_receipt_id)
    assert receipt.mocked is True
    assert receipt.to == "Acme Freight Co"

    # 14. Accounting handoff occurred (mocked).
    assert packet.accounting_receipt_id is not None

    # 15. Archive received the completed load record.
    record = store.archive.get(load.id)
    assert record is not None
    assert record.load.status == LoadStatus.ARCHIVED
    assert record.completion_packet.id == packet.id
    assert record.trip_card.closed is True


def test_close_load_blocks_on_unfinished_required_work():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    load = store.intake_load("A", "B", "Beta Logistics", 1000.0, now=now)
    store.evaluate_load(load.id, score=0.5)
    entry = store.send_to_sandbox(load.id, now=now)
    store.commit_load(entry.id, now=now)

    # Only some required items completed.
    store.record_trip_event(load.id, TripCardItemName.ARRIVAL, now=now)
    store.record_trip_event(load.id, TripCardItemName.PICKUP, now=now)

    try:
        store.close_load(load.id, now=now)
        assert False, "expected close_load to block on unfinished required work"
    except ValueError as exc:
        assert "unfinished required work" in str(exc)

    assert load.status == LoadStatus.ACTIVE  # unchanged, Close Load did not proceed


def test_close_load_with_mike_override_is_recorded():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()
    load = store.intake_load("A", "B", "Beta Logistics", 1000.0, now=now)
    store.evaluate_load(load.id, score=0.5)
    entry = store.send_to_sandbox(load.id, now=now)
    store.commit_load(entry.id, now=now)
    store.record_trip_event(load.id, TripCardItemName.ARRIVAL, now=now)

    archived_load = store.close_load(load.id, mike_override=True, now=now)
    assert archived_load.status == LoadStatus.ARCHIVED

    trip_card = store.archive.get(load.id).trip_card
    assert trip_card.override is not None
    assert trip_card.override.by == "Mike"
    assert "pickup" in trip_card.override.open_items
