from __future__ import annotations

from copy import deepcopy

_CONTROLS = {
    "phishing": {
        "title": "Phishing and suspicious messages",
        "actions": [
            "Use a separate trusted channel to verify unusual payment, login, or document requests.",
            "Report suspicious messages through the organisation's agreed process.",
            "Use phishing-resistant multi-factor authentication where feasible.",
            "Provide short, regular awareness training that includes reporting rather than blame.",
        ],
    },
    "account_security": {
        "title": "Account and identity security",
        "actions": [
            "Enable multi-factor authentication, prioritising administrator and email accounts.",
            "Review unusual sign-ins and reset credentials only through an approved process.",
            "Remove accounts that are no longer needed and limit administrator privileges.",
            "Use a password manager and unique, strong passwords for important accounts.",
        ],
    },
    "device_security": {
        "title": "Device security",
        "actions": [
            "Ensure screen lock, supported operating systems, and endpoint protection are enabled.",
            "Separate shared and administrator use where possible.",
            "Ask authorised IT staff to check affected devices before they return to normal use.",
            "Keep an inventory of organisation-owned devices and their responsible owners.",
        ],
    },
    "patching": {
        "title": "Patching and application control",
        "actions": [
            "Apply security updates promptly using an approved maintenance process.",
            "Prioritise internet-facing, email, browser, and remote-access software.",
            "Remove unsupported software when a supported alternative is available.",
            "Document exceptions and assign an owner with a review date.",
        ],
    },
    "backup": {
        "title": "Backups and recovery",
        "actions": [
            "Maintain protected backups of important business data.",
            "Test restoration regularly; a backup is only useful when recovery works.",
            "Limit who can delete or modify backup settings.",
            "Keep recovery contacts and priorities documented offline or in a protected location.",
        ],
    },
    "incident_response": {
        "title": "Incident response and escalation",
        "actions": [
            "Record the time, affected service, and observable facts without collecting secrets.",
            "Notify the nominated manager, IT contact, or incident-response provider.",
            "Escalate promptly when fraud, sensitive data, active compromise, or service disruption is suspected.",
            "After the immediate issue, document lessons learned and improve the relevant control.",
        ],
    },
}


def list_control_categories() -> dict:
    """Return the read-only defensive control categories available in CyberGuard AI."""
    return {"categories": sorted(_CONTROLS.keys())}


def get_control_guidance(category: str) -> dict:
    """Return defensive guidance for one approved control category.

    Args:
        category: One of phishing, account_security, device_security, patching,
            backup, or incident_response.
    """
    key = category.strip().lower()
    if key not in _CONTROLS:
        return {
            "status": "error",
            "message": "Unknown category. Use list_control_categories first.",
        }
    result = deepcopy(_CONTROLS[key])
    result["status"] = "success"
    result["category"] = key
    return result
