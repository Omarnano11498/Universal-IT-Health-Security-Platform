from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import uuid

ALLOWED_ACTIONS = {
    "refresh_diagnostics": {
        "risk": "LOW",
        "description": "Run the read-only diagnostic collection again.",
        "requires_admin": False,
    }
}


@dataclass
class ApprovalRequest:
    request_id: str
    action_id: str
    description: str
    risk: str
    status: str
    created_at: str


def create_approval_request(action_id: str) -> dict:
    if action_id not in ALLOWED_ACTIONS:
        raise ValueError("Action is not in the approved action catalog.")
    action = ALLOWED_ACTIONS[action_id]
    request = ApprovalRequest(
        request_id=str(uuid.uuid4()),
        action_id=action_id,
        description=action["description"],
        risk=action["risk"],
        status="PENDING_APPROVAL",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return asdict(request)


def approve_request(request: dict, approved_by: str) -> dict:
    if not approved_by or not approved_by.strip():
        raise ValueError("An approver identity is required.")
    if request.get("status") != "PENDING_APPROVAL":
        raise ValueError("Only pending requests can be approved.")
    if request.get("action_id") not in ALLOWED_ACTIONS:
        raise ValueError("Action is not in the approved action catalog.")
    approved = dict(request)
    approved.update({
        "status": "APPROVED_NOT_EXECUTED",
        "approved_by": approved_by.strip(),
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "note": "Approval recorded. This application does not execute repair commands.",
    })
    return approved
