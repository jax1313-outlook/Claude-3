#!/usr/bin/env python3
"""Runnable demo: one freight load, intake through archive.

    python demo_first_live_load.py

Every step of the required First Live Load workflow is printed as it
happens, followed by a snapshot of the Operations Cockpit view.
"""

from datetime import datetime

from dispatch_build.models import TripCardItemName
from dispatch_build.store import DispatchStore

import json


def step(n, description):
    print(f"\n[{n:>2}] {description}")


def main():
    now = datetime(2026, 8, 17, 8, 0, 0)
    store = DispatchStore()

    step(1, "Load enters Dispatch")
    load = store.intake_load(
        origin="Jacksonville, FL", destination="Atlanta, GA", broker="Acme Freight Co", rate=1450.0, now=now
    )
    runner_up = store.intake_load(
        origin="Jacksonville, FL", destination="Atlanta, GA", broker="Acme Freight Co", rate=1300.0, now=now
    )
    print(f"    Load {load.id} intaken ({load.origin} -> {load.destination}, ${load.rate})")
    print(f"    Competing option {runner_up.id} intaken as well (${runner_up.rate})")

    step(2, "Load can be evaluated")
    store.evaluate_load(load.id, score=0.82)
    store.evaluate_load(runner_up.id, score=0.61)
    print(f"    {load.id} scored 0.82, {runner_up.id} scored 0.61")

    step(3, "Load can move to Sandbox")
    entry = store.send_to_sandbox(load.id, now=now)
    runner_up_entry = store.send_to_sandbox(runner_up.id, now=now)
    print(f"    Both options sitting in Sandbox: {entry.id}, {runner_up_entry.id}")

    step(4, "Mike commits the load")
    store.commit_load(entry.id, now=now)
    print(f"    {load.id} committed. {runner_up.id} becomes runner-up, HOLD clock started (3h).")

    step(5, "Active Load created")
    print(f"    {load.id} status: {load.status.value}")

    step(6, "Trip Card opens")
    trip_card = store.trip_card_board.get(load.trip_card_id)
    print(f"    Trip Card {trip_card.id} opened with {len(trip_card.items)} checklist items, all empty")

    step(7, "Trip Card tracks deterministic driver events")
    for item_name, evidence in [
        (TripCardItemName.ARRIVAL, "gps-ping-1"),
        (TripCardItemName.PICKUP, "driver-checkin-1"),
        (TripCardItemName.BOL, "bol-scan-001.pdf"),
        (TripCardItemName.LOAD_CHECK, "load-check-ok"),
        (TripCardItemName.DELIVERY, "gps-ping-2"),
        (TripCardItemName.POD, "pod-scan-001.pdf"),
    ]:
        store.record_trip_event(load.id, item_name, evidence_ref=evidence, now=now)
        print(f"    {item_name.value}: recorded ({evidence})")
    print("    delay: left empty (no delay on this load)")

    step(8, "Empty Trip Card item means unfinished work")
    ready, missing = trip_card.is_ready_to_close()
    print(f"    Ready to close: {ready}. Missing required items: {[m.name.value for m in missing]}")

    step(9, "Mike manually selects Close Load")
    archived_load = store.close_load(load.id, now=now)
    print(f"    {load.id} status: {archived_load.status.value}")

    step(10, "Close Load triggered Completion Packet")
    packet = store.completion_packets[archived_load.completion_packet_id]
    print(f"    Completion Packet {packet.id} created")

    step(11, "Completion Packet contents")
    print(f"    Invoice: {packet.invoice_ref}  BOL: {packet.bol_ref}  POD: {packet.pod_ref}")

    step(12, "Publisher prepared the completion message from the Library template")
    print("    ---")
    print("    " + packet.publisher_message.replace("\n", "\n    "))
    print("    ---")

    step(13, "Email Helper transported the packet through the (mocked) Outlook boundary")
    print(f"    Mock send receipt: {packet.email_receipt_id}")

    step(14, "Accounting handoff (mocked)")
    print(f"    Accounting receipt: {packet.accounting_receipt_id}")

    step(15, "Archive received the completed load record")
    record = store.archive.get(load.id)
    print(f"    Archive record {record.id} stored for {record.load_id}")

    print("\n--- HOLD sweep, 3 hours + 1 minute later ---")
    from datetime import timedelta

    later = now + timedelta(hours=3, minutes=1)
    deleted = store.run_hold_sweep(now=later)
    print(f"Deleted expired runner-up sandbox entries (not archived): {deleted}")

    print("\n--- Operations Cockpit snapshot ---")
    print(json.dumps(store.cockpit_view(now=later), indent=2, default=str))


if __name__ == "__main__":
    main()
