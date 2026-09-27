"""Company preferences and review state for proposals; this module never sends mail.

Execution evidence in the tourism simulator describes simulated work. A reviewed
proposal is permission to run that workflow, not evidence of a real booking.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import smtplib
import ssl
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


DEFAULT_SETTINGS = {
    "autonomy_mode": "proposal_first",
    "execute_plan": True,
    "send_email": False,
    "generate_reports": True,
    "allowed_recipients": [],
    "max_auto_quote_cny": 200000,
}
MODES = ("proposal_first", "approval_required", "autonomous")
STATUSES = ("pending_review", "approved", "changes_requested", "escalated",
            "ready_to_resubmit", "completed")
_LOCK = threading.RLock()
_SEND_LOCK = threading.RLock()
_EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}$")


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_settings(value: dict) -> dict:
    """Normalize nonsecret settings. Unknown fields, including credentials, fail."""
    if not isinstance(value, dict):
        raise ValueError("Settings must be an object.")
    unknown = set(value) - set(DEFAULT_SETTINGS)
    if unknown:
        raise ValueError("Unknown setting: " + ", ".join(sorted(unknown)))
    result = {**copy.deepcopy(DEFAULT_SETTINGS), **copy.deepcopy(value)}
    if result["autonomy_mode"] not in MODES:
        raise ValueError("Choose proposal_first, approval_required or autonomous.")
    for key in ("execute_plan", "send_email", "generate_reports"):
        if not isinstance(result[key], bool):
            raise ValueError(f"{key} must be true or false.")
    amount = result["max_auto_quote_cny"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
        raise ValueError("Automatic quotation limit must be a finite nonnegative CNY amount.")
    addresses = result["allowed_recipients"]
    if not isinstance(addresses, list) or len(addresses) > 200:
        raise ValueError("Allowed recipients must be a list of at most 200 email addresses.")
    if any(not isinstance(address, str) or not _EMAIL.fullmatch(address.strip()) for address in addresses):
        raise ValueError("Use complete email addresses in the allowed-recipient list.")
    result["allowed_recipients"] = sorted({address.strip().lower() for address in addresses})
    return result


def load_settings(data: Path) -> dict:
    with _LOCK:
        path = Path(data) / "settings.json"
        if not path.exists():
            return copy.deepcopy(DEFAULT_SETTINGS)
        return validate_settings(json.loads(path.read_text(encoding="utf-8")))


def save_settings(data: Path, updates: dict) -> dict:
    """Merge preferences and atomically replace only settings.json."""
    with _LOCK:
        if not isinstance(updates, dict):
            raise ValueError("Settings must be an object.")
        result = validate_settings({**load_settings(data), **updates})
        folder = Path(data)
        folder.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder,
                                             prefix="settings-", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, folder / "settings.json")
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        return result


def quote_amount(case: dict) -> int | float | None:
    amount = case.get("selected_option", {}).get("quote_cny")
    if amount is None:
        amount = case.get("outcome", {}).get("data", {}).get("quote_cny")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
        return None
    return amount


def case_fingerprint(case: dict) -> str:
    """Bind review to the submitted request, option, assignment and schedule."""
    content = {"request": case.get("request"), "selected_option": case.get("selected_option"),
               "assignments": case.get("hierarchy", {}).get("data", {}).get("assignments"),
               "tasks": case.get("workload", {}).get("data", {}).get("tasks"),
               "schedule": case.get("schedule", {}).get("data")}
    raw = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def case_issues(case: dict) -> list[str]:
    """Find actual blockers, excluding the normal unexecuted approval gates."""
    issues = []
    for key in ("inquiry", "flights", "tours", "comparison", "hierarchy", "workload", "schedule"):
        stage = case.get(key)
        if isinstance(stage, dict) and stage.get("status") in ("needs_input", "blocked", "escalated"):
            issues.extend(str(issue) for issue in stage.get("issues", []) if issue)
            if not stage.get("issues"):
                issues.append(f"The {key} step needs attention before the plan can proceed.")
    for incident in case.get("execution", {}).get("data", {}).get("incidents", []):
        issues.append(f"{incident.get('task_id', 'Task')}: {incident.get('reason', 'open incident')}")
    if quote_amount(case) is None and not issues:
        issues.append("The team has not produced a valid quotation yet.")
    return list(dict.fromkeys(issues))


def manager_for(case: dict, people: list[dict] | None = None) -> dict:
    roster = people if people is not None else case.get("people_snapshot", [])
    staff = {person["id"]: person for person in roster if isinstance(person, dict) and person.get("id")}
    lead_id = case.get("hierarchy", {}).get("data", {}).get("task_lead")
    lead = staff.get(lead_id, {})
    manager = staff.get(lead.get("reports_to"))
    if not manager:
        manager = next((person for person in staff.values() if person.get("reports_to") is None), None)
    if not manager:
        return {"id": None, "name": "Company manager", "role": "Manager", "delivery": "in_app"}
    return {"id": manager["id"], "name": manager.get("name", manager["id"]),
            "role": manager.get("role", "Manager"), "delivery": "in_app"}


def _suggestion(issues: list[str]) -> str:
    text = " ".join(issues).lower()
    if any(word in text for word in ("seat", "flight", "supplier", "availability")):
        return "Ask the supplier for an alternative date, capacity or offer, update the plan, then resubmit for review."
    if any(word in text for word in ("budget", "price", "quotation", "quote")):
        return "Compare a lower-cost option or agree a revised budget, update the quotation, then resubmit."
    if any(word in text for word in ("capacity", "staff", "assign", "skill")):
        return "Ask the manager to reassign work or add qualified capacity, then rebuild and resubmit the plan."
    if any(word in text for word in ("email", "smtp", "recipient", "deliver")):
        return "Check the delivery address and email connection, record the fix, then retry delivery."
    return "Ask the manager to review the issue, update the affected plan or task, record the resolution, then resubmit."


def _refresh_manager_message(proposal: dict) -> None:
    if proposal["status"] != "escalated":
        proposal["manager_message"] = ""
        return
    issues = "; ".join(proposal.get("issues", [])) or "The team needs a management decision."
    proposal["manager_message"] = (
        f"{proposal['manager']['name']}, I cannot submit {proposal.get('request_id') or 'this request'} yet. "
        f"Issue: {issues} Next step: {proposal['suggested_resolution']}"
    )


def _record(proposal: dict, action: str, previous: str | None, comment: str = "", actor: str = "user") -> None:
    now = timestamp()
    proposal["updated_at"] = now
    proposal["audit"].append({"at": now, "action": action, "from_status": previous,
                              "to_status": proposal["status"], "revision": proposal["revision"],
                              "actor": actor, "comment": comment})
    if comment:
        proposal["comments"].append({"at": now, "action": action, "revision": proposal["revision"],
                                    "actor": actor, "text": comment})
    _refresh_manager_message(proposal)


def create_proposal(case: dict, settings: dict) -> dict:
    policy = validate_settings(settings)
    issues = case_issues(case)
    amount = quote_amount(case)
    automatic = (policy["autonomy_mode"] == "autonomous" and policy["execute_plan"]
                 and amount is not None and amount <= policy["max_auto_quote_cny"] and not issues)
    status = "escalated" if issues else "approved" if automatic else "pending_review"
    now = timestamp()
    proposal = {
        "id": "proposal-" + uuid.uuid4().hex[:12], "request_id": case.get("request", {}).get("request_id"),
        "status": status, "revision": 1, "created_at": now, "updated_at": now,
        "comments": [], "audit": [], "policy_snapshot": policy,
        "manager": manager_for(case), "issues": issues, "suggested_resolution": _suggestion(issues) if issues else "",
        "manager_message": "", "quote_cny": amount, "case_fingerprint": case_fingerprint(case),
        "approval_source": "policy" if automatic else None, "email_approved": False,
        "simulation": bool(case.get("simulation", True)),
        "review_notes": ["The quotation exceeds the automatic limit; a person must approve it."]
            if amount is not None and amount > policy["max_auto_quote_cny"] else [],
    }
    _record(proposal, "created", None, actor="company_assistant")
    return proposal


def revise_proposal(proposal: dict, case: dict, policy: dict, comment: str, *, submit: bool = True) -> dict:
    """Reopen the same proposal after edits without losing its review history.

    Submitted replacement requests start a new revision. An in-place plan edit
    remains on the current revision until the team explicitly resubmits it.
    """
    if not isinstance(proposal, dict) or proposal.get("status") not in STATUSES:
        raise ValueError("The proposal has no valid review state.")
    if not isinstance(comment, str) or len(comment) > 5000:
        raise ValueError("Revision comments must be text of at most 5,000 characters.")
    if not isinstance(submit, bool):
        raise ValueError("Submit must be true or false.")
    result = copy.deepcopy(proposal)
    previous = result["status"]
    fresh = create_proposal(case, policy)
    snapshot = {key: copy.deepcopy(proposal.get(key)) for key in
                ("request_id", "revision", "status", "quote_cny", "case_fingerprint", "delivery")}
    snapshot["archived_at"] = timestamp()
    result.setdefault("previous_revisions", []).append(snapshot)
    for key in ("request_id", "policy_snapshot", "manager", "issues", "suggested_resolution",
                "quote_cny", "case_fingerprint", "simulation", "review_notes"):
        result[key] = fresh[key]
    if not submit and previous == "escalated":
        result["issues"] = list(dict.fromkeys([*proposal.get("issues", []), *fresh["issues"]]))
        result["suggested_resolution"] = _suggestion(result["issues"])
    result["revision"] += int(submit)
    result["status"] = "escalated" if result["issues"] else "pending_review" if submit else "changes_requested"
    result.update(approval_source=None, email_approved=False,
                  delivery={"status": "draft", "message": "The revised plan needs review before delivery."})
    if not submit and comment.strip():
        result["change_request"] = comment.strip()
    _record(result, "revised_request" if submit else "plan_changed", previous, comment.strip(), actor="company_assistant")
    return result


def review_proposal(proposal: dict, action: str, comment: str, case: dict,
                    people: list[dict] | None = None, *, internal: bool = False) -> dict:
    """Return a reviewed copy, preserving feedback and all previous audit events."""
    if not isinstance(proposal, dict) or proposal.get("status") not in STATUSES:
        raise ValueError("The proposal has no valid review state.")
    if not isinstance(comment, str) or len(comment) > 5000:
        raise ValueError("Review comments must be text of at most 5,000 characters.")
    comment = comment.strip()
    result = copy.deepcopy(proposal)
    previous = result["status"]
    issues = case_issues(case)
    result["manager"] = manager_for(case, people)
    if action == "approve":
        if previous != "pending_review":
            raise ValueError("Only a submitted proposal awaiting review can be approved.")
        if issues or result.get("issues"):
            raise ValueError("Resolve the open issues and resubmit before approving.")
        if result.get("case_fingerprint") != case_fingerprint(case):
            raise ValueError("The plan changed after submission. Send it back for changes and resubmit it.")
        result.update(status="approved", approval_source="human")
    elif action == "approve_email":
        if previous not in ("approved", "completed") or issues:
            raise ValueError("Approve and resolve the plan before approving delivery.")
        if result.get("case_fingerprint") != case_fingerprint(case):
            raise ValueError("The plan changed; resubmit it before approving delivery.")
        result["email_approved"] = True
    elif action == "request_changes":
        if previous not in ("pending_review", "approved", "ready_to_resubmit", "completed"):
            raise ValueError("This proposal cannot currently be returned for changes.")
        if not comment:
            raise ValueError("Add comments so the team knows what to change.")
        result.update(status="changes_requested", approval_source=None, email_approved=False,
                      change_request=comment)
    elif action == "escalate":
        if not comment and not issues:
            raise ValueError("Describe the issue that the manager needs to resolve.")
        combined = list(dict.fromkeys([*issues, *result.get("issues", []), *([comment] if comment else [])]))
        result.update(status="escalated", issues=combined, suggested_resolution=_suggestion(combined),
                      approval_source=None, email_approved=False)
    elif action == "resolve":
        if previous != "escalated":
            raise ValueError("Only an escalated issue can be resolved.")
        if not comment:
            raise ValueError("Explain what resolved the issue before returning it to the team.")
        if issues:
            raise ValueError("The plan still has unresolved issues: " + "; ".join(issues))
        result.update(status="ready_to_resubmit", issues=[], suggested_resolution="",
                      resolution=comment, approval_source=None, email_approved=False)
    elif action == "resubmit":
        if previous not in ("changes_requested", "ready_to_resubmit"):
            raise ValueError("Only a revised or resolved proposal can be resubmitted.")
        if previous == "changes_requested" and not comment:
            raise ValueError("Explain how the team addressed the review comments.")
        result.update(revision=result["revision"] + 1, status="escalated" if issues else "pending_review",
                      issues=issues, suggested_resolution=_suggestion(issues) if issues else "",
                      quote_cny=quote_amount(case), case_fingerprint=case_fingerprint(case),
                      approval_source=None, email_approved=False)
    elif action == "complete":
        if not internal:
            raise ValueError("Completion is recorded by the execution controller.")
        if previous != "approved" or issues:
            raise ValueError("The approved plan must have no unresolved issues before completion.")
        if case.get("outcome", {}).get("data", {}).get("decision") != "ready_for_human_review":
            raise ValueError("The required workflow evidence is not complete.")
        if result.get("case_fingerprint") != case_fingerprint(case):
            raise ValueError("The plan changed during execution and needs review again.")
        result["status"] = "completed"
    else:
        raise ValueError("Unknown review action.")
    _record(result, action, previous, comment, actor="company_assistant" if internal else "user")
    return result


def authorize_email(policy: dict, recipient: str, quote: int | float,
                    approval: dict | None = None) -> dict:
    """Check delivery authority. SMTP credentials and workflow evidence are separate.

    The caller must verify the reviewed case fingerprint and real workflow readiness
    before invoking its sender. This function does not establish either condition.
    """
    settings = validate_settings(policy)
    if not settings["send_email"]:
        raise PermissionError("Email delivery is disabled in company settings.")
    if not isinstance(recipient, str) or not _EMAIL.fullmatch(recipient.strip()):
        raise PermissionError("A valid customer email address is required.")
    recipient = recipient.strip().lower()
    if recipient not in settings["allowed_recipients"]:
        raise PermissionError("The recipient is outside the allowed delivery list.")
    if isinstance(quote, bool) or not isinstance(quote, (int, float)) or not math.isfinite(quote) or quote < 0:
        raise PermissionError("A valid quotation amount is required for delivery.")
    if not isinstance(approval, dict) or approval.get("status") not in ("approved", "completed"):
        raise PermissionError("The proposal needs approval before email delivery.")
    if approval.get("issues"):
        raise PermissionError("Open proposal issues block delivery.")
    mode = settings["autonomy_mode"]
    if mode != "autonomous" and approval.get("approval_source") != "human":
        raise PermissionError("This mode requires a person to approve the proposal.")
    if mode == "approval_required" and approval.get("email_approved") is not True:
        raise PermissionError("This mode requires a separate delivery approval.")
    if quote > settings["max_auto_quote_cny"] and approval.get("approval_source") != "human":
        raise PermissionError("The quotation exceeds the automatic delivery limit.")
    return {"allowed": True, "recipient": recipient, "mode": mode,
            "approval_source": approval.get("approval_source"), "proposal_id": approval.get("id")}


def send_approved_email(case: dict, proposal: dict, policy: dict, output_dir: Path) -> dict:
    """Send one reviewed indicative quotation using environment-based SMTP.

    A receipt prevents replay of a successful or uncertain send for this revision.
    Real mail is possible only after explicit delivery opt-in and scoped authority.
    """
    if proposal.get("case_fingerprint") != case_fingerprint(case):
        raise PermissionError("The case changed after review; resubmit it before sending.")
    outcome = case.get("outcome", {}).get("data", {})
    draft = outcome.get("customer_email_draft", {})
    if (case_issues(case) or outcome.get("decision") != "ready_for_human_review"
            or not draft.get("send_allowed")):
        raise PermissionError("Finish the required workflow evidence before email delivery.")
    allowed = authorize_email(policy, draft.get("to"), quote_amount(case), proposal)
    recipient = allowed["recipient"]
    if recipient.casefold() != "amonsk007@gmail.com":
        raise PermissionError("Demo delivery is restricted to amonsk007@gmail.com. No message was sent.")
    if recipient.rsplit("@", 1)[-1].endswith(".test"):
        raise PermissionError("Replace the demonstration .test address with a real allowed recipient.")
    host = os.environ.get("TOURISM_SMTP_HOST", "").strip()
    sender = os.environ.get("TOURISM_SMTP_FROM", "").strip()
    user = os.environ.get("TOURISM_SMTP_USER", "")
    password = os.environ.get("TOURISM_SMTP_PASSWORD", "")
    if not all((host, sender, user, password)):
        raise RuntimeError("Email connection is incomplete. Configure the SMTP host, sender, user and password.")
    if not _EMAIL.fullmatch(sender):
        raise ValueError("The configured SMTP sender must be a valid email address.")
    try:
        port = int(os.environ.get("TOURISM_SMTP_PORT", "587"))
    except ValueError as exc:
        raise ValueError("SMTP port must be a number.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("SMTP port must be between 1 and 65535.")
    request_id = str(case.get("request", {}).get("request_id", ""))
    proposal_id = str(proposal.get("id", ""))
    if any(not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value) for value in (request_id, proposal_id)):
        raise ValueError("The case and proposal need valid identifiers.")
    revision = proposal.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("The proposal needs a valid revision.")
    message = EmailMessage()
    message["From"], message["To"] = sender, recipient
    message["Subject"] = draft.get("subject", "Indicative tourism quotation")
    message["Message-ID"] = f"<{proposal_id}.{revision}@{sender.rsplit('@', 1)[-1]}>"
    body = draft.get("body", "")
    if case.get("simulation"):
        body += "\n\nDemonstration: prices, availability and task evidence in this proposal are simulated. This is not a confirmed booking."
    message.set_content(body)
    folder = Path(output_dir)
    attachments = []
    if policy.get("generate_reports", True):
        for suffix, subtype in (("decision-brief.docx", "vnd.openxmlformats-officedocument.wordprocessingml.document"),
                                ("management-deck.pptx", "vnd.openxmlformats-officedocument.presentationml.presentation")):
            path = folder / f"{request_id}-{suffix}"
            if not path.is_file():
                raise RuntimeError("Generate the Word and PowerPoint reports before sending this proposal.")
            message.add_attachment(path.read_bytes(), maintype="application", subtype=subtype, filename=path.name)
            attachments.append(path.name)
    receipt_path = folder / f"{proposal_id}-r{revision}-email.json"
    with _SEND_LOCK:
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if receipt.get("status") == "sent":
                return {**receipt, "already_sent": True}
            if receipt.get("status") in ("sending", "delivery_unknown"):
                raise RuntimeError("The prior delivery outcome is uncertain. Ask the manager to check the sender's outbox before submitting a new revision.")
        receipt = {"status": "sending", "request_id": request_id, "proposal_id": proposal_id,
                   "revision": revision, "recipient": recipient, "attachments": attachments, "at": timestamp()}
        folder.mkdir(parents=True, exist_ok=True)
        _write_receipt(receipt_path, receipt)
        attempting_delivery = False
        try:
            with smtplib.SMTP(host, port, timeout=15) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(user, password)
                attempting_delivery = True
                refused = smtp.send_message(message)
                if refused:
                    attempting_delivery = False
                    raise RuntimeError("The mail service declined the recipient.")
                receipt.update(status="sent", at=timestamp())
                _write_receipt(receipt_path, receipt)
        except Exception as exc:
            if receipt["status"] == "sent":
                return receipt
            receipt.update(status="delivery_unknown" if attempting_delivery else "failed", at=timestamp())
            _write_receipt(receipt_path, receipt)
            if attempting_delivery:
                raise RuntimeError("The mail service did not confirm delivery. Ask the manager to check the outbox before retrying.") from exc
            raise RuntimeError("Email delivery failed before the message was sent. Check the email connection and resolve the issue.") from exc
        return receipt


def _write_receipt(path: Path, receipt: dict) -> None:
    """Use a same-folder replacement so a crash cannot leave a partial JSON receipt."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="email-receipt-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(receipt, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
