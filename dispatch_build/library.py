"""Library — supplies approved templates and reusable company assets.

Library does not create truth. Everything returned here is a fixed,
pre-approved asset; nothing is generated on the fly.
"""

from __future__ import annotations

TEMPLATES = {
    "completion_message": (
        "Hi {broker},\n\n"
        "Load {load_id} ({origin} -> {destination}) has been delivered and closed out.\n"
        "Completion Packet (invoice, signed BOL, POD) is attached.\n\n"
        "Thank you for using Level 1 Transport."
    ),
}

# Standard onboarding document set. Per the Onboarding Packet rule: if a
# broker asks for one setup document, the full packet is sent — documents
# are not micromanaged individually.
ONBOARDING_PACKET_DOCUMENTS = (
    "Insurance Certificate",
    "W9",
    "Authority Letter",
    "Carrier Packet",
    "Company Information",
)


class Library:
    """Read-only supplier of approved templates and company assets."""

    def get_template(self, name: str) -> str:
        if name not in TEMPLATES:
            raise KeyError(f"No approved Library template named {name!r}")
        return TEMPLATES[name]

    def get_onboarding_packet_documents(self) -> tuple:
        return ONBOARDING_PACKET_DOCUMENTS
