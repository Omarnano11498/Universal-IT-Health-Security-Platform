import unittest
from app.services.remediation import create_approval_request, approve_request

def test_approval_flow_does_not_execute():
    request = create_approval_request("refresh_diagnostics")
    assert request["status"] == "PENDING_APPROVAL"
    approved = approve_request(request, "test-admin")
    assert approved["status"] == "APPROVED_NOT_EXECUTED"
    assert "does not execute" in approved["note"]

def test_unknown_action_rejected():
    with unittest.TestCase().assertRaises(ValueError):
        create_approval_request("run-arbitrary-shell-command")

def test_approver_required():
    request = create_approval_request("refresh_diagnostics")
    with unittest.TestCase().assertRaises(ValueError):
        approve_request(request, "")
