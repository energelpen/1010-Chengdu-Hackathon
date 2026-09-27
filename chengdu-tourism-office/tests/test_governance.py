"""Behavioral checks for persisted scope, review gates and management escalation."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.governance import (DEFAULT_SETTINGS, authorize_email, case_fingerprint,
                                create_proposal, load_settings, review_proposal,
                                revise_proposal, save_settings, send_approved_email, validate_settings)


def sample_case() -> dict:
    return {
        "simulation": True, "request": {"request_id": "SIM-REVIEW-1", "message": "A tourism quotation"},
        "inquiry": {"status": "ok", "data": {}},
        "selected_option": {"id": "balanced", "quote_cny": 160000},
        "hierarchy": {"status": "ok", "data": {"task_lead": "lead", "assignments": {"pricing": "lead"}}},
        "workload": {"status": "ok", "data": {"tasks": [{"id": "PRICING", "owner_id": "lead"}]}},
        "people_snapshot": [
            {"id": "boss", "name": "Director Chen", "role": "Director", "reports_to": None},
            {"id": "lead", "name": "Manager Wang", "role": "Sales", "reports_to": "boss"},
        ],
        "execution": {"status": "ok", "data": {"incidents": []}},
        "outcome": {"status": "blocked", "data": {"decision": "hold", "open_gates": ["FINANCE"]}},
    }


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.case = sample_case()
        self.policy = copy.deepcopy(DEFAULT_SETTINGS)

    def test_default_settings_are_independent_and_persist_partial_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = load_settings(root)
            first["allowed_recipients"].append("private@example.com")
            self.assertEqual(load_settings(root)["allowed_recipients"], [])
            save_settings(root, {"send_email": True, "allowed_recipients": [" Buyer@Example.COM "]})
            saved = save_settings(root, {"autonomy_mode": "autonomous"})
            self.assertTrue(saved["send_email"])
            self.assertEqual(saved["allowed_recipients"], ["buyer@example.com"])
            self.assertEqual(load_settings(root), saved)
            self.assertEqual(list(root.glob("*.tmp")), [])

    def test_invalid_scope_and_credentials_are_rejected(self):
        for changes in ({"send_email": "yes"}, {"allowed_recipients": ["*@example.com", "bad"]},
                        {"max_auto_quote_cny": True}, {"max_auto_quote_cny": float("nan")},
                        {"max_auto_quote_cny": -1}, {"openai_api_key": "secret"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_settings(changes)

    def test_normal_preexecution_gates_do_not_trigger_escalation(self):
        proposal = create_proposal(self.case, self.policy)
        self.assertEqual(proposal["status"], "pending_review")
        self.assertEqual(proposal["issues"], [])
        self.assertEqual(proposal["manager"]["id"], "boss")

    def test_autonomy_obeys_execution_switch_and_budget(self):
        self.policy["autonomy_mode"] = "autonomous"
        self.assertEqual(create_proposal(self.case, self.policy)["status"], "approved")
        self.policy["execute_plan"] = False
        self.assertEqual(create_proposal(self.case, self.policy)["status"], "pending_review")
        self.policy.update(execute_plan=True, max_auto_quote_cny=100000)
        proposal = create_proposal(self.case, self.policy)
        self.assertEqual(proposal["status"], "pending_review")
        self.assertTrue(proposal["review_notes"])

    def test_return_comments_revision_and_approval_preserve_history(self):
        proposal = create_proposal(self.case, self.policy)
        returned = review_proposal(proposal, "request_changes", "Use a smaller group option.", self.case)
        self.assertEqual(proposal["status"], "pending_review")
        self.assertEqual(returned["status"], "changes_requested")
        with self.assertRaises(ValueError):
            review_proposal(returned, "approve", "", self.case)
        revised = review_proposal(returned, "resubmit", "Repriced the group option.", self.case)
        approved = review_proposal(revised, "approve", "Ready to proceed.", self.case)
        self.assertEqual(approved["revision"], 2)
        self.assertEqual(approved["approval_source"], "human")
        self.assertEqual(len(approved["audit"]), 4)
        self.assertEqual(approved["comments"][0]["text"], "Use a smaller group option.")

    def test_blocked_request_routes_to_manager_and_requires_fix_before_resolution(self):
        self.case["flights"] = {"status": "blocked", "issues": ["No flights have enough seats."]}
        proposal = create_proposal(self.case, self.policy)
        self.assertEqual(proposal["status"], "escalated")
        self.assertIn("Director Chen", proposal["manager_message"])
        self.assertIn("alternative date", proposal["suggested_resolution"])
        with self.assertRaises(ValueError):
            review_proposal(proposal, "approve", "Go", self.case)
        with self.assertRaises(ValueError):
            review_proposal(proposal, "resolve", "Supplier said yes.", self.case)
        self.case["flights"] = {"status": "ok", "issues": []}
        with self.assertRaises(ValueError):
            review_proposal(proposal, "resolve", "  ", self.case)
        resolved = review_proposal(proposal, "resolve", "Supplier updated the group capacity.", self.case)
        self.assertEqual(resolved["status"], "ready_to_resubmit")
        self.assertEqual(resolved["manager_message"], "")
        revised = review_proposal(resolved, "resubmit", "Capacity verified.", self.case)
        self.assertEqual(revised["status"], "pending_review")

    def test_new_quote_cannot_reuse_old_approval(self):
        proposal = create_proposal(self.case, self.policy)
        self.case["selected_option"]["quote_cny"] = 170000
        with self.assertRaises(ValueError):
            review_proposal(proposal, "approve", "", self.case)
        revised = review_proposal(proposal, "request_changes", "Recheck the revised price.", self.case)
        revised = review_proposal(revised, "resubmit", "New price included.", self.case)
        self.assertEqual(revised["case_fingerprint"], case_fingerprint(self.case))

    def test_revised_request_preserves_identity_feedback_and_previous_delivery(self):
        proposal = create_proposal(self.case, self.policy)
        proposal = review_proposal(proposal, "request_changes", "Please reduce the price.", self.case)
        proposal["delivery"] = {"status": "draft", "message": "Old draft"}
        original = copy.deepcopy(proposal)
        self.case["request"]["request_id"] = "SIM-REVIEW-2"
        self.case["selected_option"]["quote_cny"] = 150000
        self.policy["autonomy_mode"] = "autonomous"
        revised = revise_proposal(proposal, self.case, self.policy, "I have revised the quotation.")
        self.assertEqual(revised["id"], original["id"])
        self.assertEqual(revised["created_at"], original["created_at"])
        self.assertEqual(revised["revision"], 2)
        self.assertEqual(revised["status"], "pending_review")
        self.assertEqual(revised["request_id"], "SIM-REVIEW-2")
        self.assertIsNone(revised["approval_source"])
        self.assertEqual(revised["comments"][0]["text"], "Please reduce the price.")
        self.assertEqual(revised["previous_revisions"][0]["request_id"], "SIM-REVIEW-1")
        self.assertEqual(revised["previous_revisions"][0]["delivery"]["message"], "Old draft")
        self.assertEqual(revised["audit"][-1]["action"], "revised_request")
        self.assertEqual(proposal, original)

    def test_in_place_plan_edit_reopens_completed_without_increment_until_resubmission(self):
        proposal = review_proposal(create_proposal(self.case, self.policy), "approve", "", self.case)
        self.case["outcome"]["data"]["decision"] = "ready_for_human_review"
        proposal = review_proposal(proposal, "complete", "", self.case, internal=True)
        proposal.update(email_approved=True, delivery={"status": "sent", "recipient": "buyer@example.com"})
        self.case["selected_option"]["quote_cny"] = 140000
        revised = revise_proposal(proposal, self.case, self.policy, "Selected the lower cost option.", submit=False)
        self.assertEqual(revised["status"], "changes_requested")
        self.assertEqual(revised["revision"], 1)
        self.assertEqual(revised["delivery"]["status"], "draft")
        self.assertFalse(revised["email_approved"])
        self.assertEqual(revised["quote_cny"], 140000)
        self.assertEqual(revised["previous_revisions"][0]["status"], "completed")
        self.assertEqual(revised["previous_revisions"][0]["delivery"]["status"], "sent")
        self.assertEqual(revised["audit"][-1]["action"], "plan_changed")
        submitted = review_proposal(revised, "resubmit", "Price comparison updated.", self.case)
        self.assertEqual(submitted["revision"], 2)
        self.assertEqual(submitted["status"], "pending_review")

    def test_editing_an_escalated_plan_does_not_silently_resolve_manager_issue(self):
        proposal = create_proposal(self.case, self.policy)
        proposal = review_proposal(proposal, "escalate", "The email connection failed.", self.case)
        self.case["selected_option"]["quote_cny"] = 150000
        revised = revise_proposal(proposal, self.case, self.policy, "Changed the package.", submit=False)
        self.assertEqual(revised["status"], "escalated")
        self.assertIn("The email connection failed.", revised["issues"])
        self.assertIn("Director Chen", revised["manager_message"])

    def test_completed_proposal_can_be_returned_with_comments(self):
        proposal = review_proposal(create_proposal(self.case, self.policy), "approve", "", self.case)
        self.case["outcome"]["data"]["decision"] = "ready_for_human_review"
        proposal = review_proposal(proposal, "complete", "", self.case, internal=True)
        returned = review_proposal(proposal, "request_changes", "Customer changed the itinerary.", self.case)
        self.assertEqual(returned["status"], "changes_requested")
        self.assertIsNone(returned["approval_source"])

    def test_completion_requires_controller_and_evidenced_outcome(self):
        proposal = review_proposal(create_proposal(self.case, self.policy), "approve", "", self.case)
        with self.assertRaises(ValueError):
            review_proposal(proposal, "complete", "", self.case)
        with self.assertRaises(ValueError):
            review_proposal(proposal, "complete", "", self.case, internal=True)
        self.case["outcome"]["data"]["decision"] = "ready_for_human_review"
        complete = review_proposal(proposal, "complete", "Work evidenced in simulation.", self.case, internal=True)
        self.assertEqual(complete["status"], "completed")
        escalated = review_proposal(complete, "escalate", "Email connection failed.", self.case)
        self.assertEqual(escalated["status"], "escalated")

    def test_email_needs_optin_allowlist_and_review(self):
        proposal = review_proposal(create_proposal(self.case, self.policy), "approve", "", self.case)
        with self.assertRaises(PermissionError):
            authorize_email(self.policy, "buyer@example.com", 160000, proposal)
        self.policy.update(send_email=True, allowed_recipients=["buyer@example.com"])
        with self.assertRaises(PermissionError):
            authorize_email(self.policy, "stranger@example.com", 160000, proposal)
        with self.assertRaises(PermissionError):
            authorize_email(self.policy, "buyer@example.com", 160000, {**proposal, "status": "escalated"})
        self.assertTrue(authorize_email(self.policy, "buyer@example.com", 160000, proposal)["allowed"])

    def test_delivery_review_mode_requires_separate_approval(self):
        self.policy.update(autonomy_mode="approval_required", send_email=True, allowed_recipients=["buyer@example.com"])
        proposal = review_proposal(create_proposal(self.case, self.policy), "approve", "", self.case)
        with self.assertRaises(PermissionError):
            authorize_email(self.policy, "buyer@example.com", 160000, proposal)
        proposal = review_proposal(proposal, "approve_email", "Send the reviewed draft.", self.case)
        self.assertTrue(authorize_email(self.policy, "buyer@example.com", 160000, proposal)["allowed"])

    def test_autonomous_delivery_has_no_hidden_manual_code(self):
        self.policy.update(autonomy_mode="autonomous", send_email=True, allowed_recipients=["buyer@example.com"])
        proposal = create_proposal(self.case, self.policy)
        self.assertEqual(proposal["approval_source"], "policy")
        self.assertTrue(authorize_email(self.policy, "buyer@example.com", 160000, proposal)["allowed"])
        with self.assertRaises(PermissionError):
            authorize_email(self.policy, "buyer@example.com", 250000, proposal)

    def test_sender_is_scoped_and_success_is_idempotent(self):
        self.policy.update(autonomy_mode="autonomous", send_email=True,
                           allowed_recipients=["amonsk007@gmail.com"], generate_reports=False)
        self.case["outcome"]["data"].update(decision="ready_for_human_review", customer_email_draft={
            "to": "amonsk007@gmail.com", "subject": "Tour quotation", "body": "Your indicative quote.", "send_allowed": True})
        proposal = create_proposal(self.case, self.policy)
        smtp = MagicMock()
        smtp.__enter__.return_value.send_message.return_value = {}
        env = {"TOURISM_SMTP_HOST": "smtp.example.com", "TOURISM_SMTP_FROM": "office@example.com",
               "TOURISM_SMTP_USER": "office", "TOURISM_SMTP_PASSWORD": "test-only"}
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", env), patch("scripts.governance.smtplib.SMTP", return_value=smtp):
            first = send_approved_email(self.case, proposal, self.policy, Path(folder))
            second = send_approved_email(self.case, proposal, self.policy, Path(folder))
            self.assertEqual(first["status"], "sent")
            self.assertTrue(second["already_sent"])
            smtp.__enter__.return_value.send_message.assert_called_once()
            sent = smtp.__enter__.return_value.send_message.call_args.args[0]
            self.assertIn("prices, availability and task evidence", sent.get_content())

    def test_uncertain_smtp_delivery_is_not_blindly_retried(self):
        self.policy.update(autonomy_mode="autonomous", send_email=True,
                           allowed_recipients=["amonsk007@gmail.com"], generate_reports=False)
        self.case["outcome"]["data"].update(decision="ready_for_human_review", customer_email_draft={
            "to": "amonsk007@gmail.com", "subject": "Quote", "body": "Quote.", "send_allowed": True})
        proposal = create_proposal(self.case, self.policy)
        smtp = MagicMock()
        smtp.__enter__.return_value.send_message.side_effect = TimeoutError("Uncertain SMTP result")
        env = {"TOURISM_SMTP_HOST": "smtp.example.com", "TOURISM_SMTP_FROM": "office@example.com",
               "TOURISM_SMTP_USER": "office", "TOURISM_SMTP_PASSWORD": "test-only"}
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", env), patch("scripts.governance.smtplib.SMTP", return_value=smtp):
            with self.assertRaisesRegex(RuntimeError, "did not confirm"):
                send_approved_email(self.case, proposal, self.policy, Path(folder))
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                send_approved_email(self.case, proposal, self.policy, Path(folder))
            smtp.__enter__.return_value.send_message.assert_called_once()
            receipt = json.loads(next(Path(folder).glob("*-email.json")).read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "delivery_unknown")


if __name__ == "__main__":
    unittest.main()
