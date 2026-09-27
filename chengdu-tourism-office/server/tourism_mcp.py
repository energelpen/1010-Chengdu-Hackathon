"""Local stdio MCP tools for the tourism-office simulation and approved email delivery."""
from __future__ import annotations

import hmac
import json
import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tourism_core import demo, flight_search, run_case, tour_search
from search_store import index_case, search_cases
from render_reports import render

from mcp.server import MCPServer

server = MCPServer("chengdu-tourism-office")
OUTPUT = ROOT / "output"


def stored_case(request_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", request_id):
        raise ValueError("Invalid request_id.")
    path = OUTPUT / f"{request_id}-trace.json"
    return json.loads(path.read_text(encoding="utf-8"))


@server.tool()
def simulate_rfq(message: str, request_id: str = "SIM-RFQ-001", customer_email: str = "") -> dict:
    """Run a synthetic tourism RFQ through hierarchy, comparison, delegation and approval gates."""
    request = {"request_id": request_id, "message": message, "customer_email": customer_email or None}
    case = run_case(request)
    if "outcome" in case:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / f"{request_id}-trace.json").write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
        artifacts = render(case, OUTPUT)
        index_case(OUTPUT / "cases.sqlite", case)
        return {"outcome": case["outcome"], "artifacts": artifacts, "request_id": request_id}
    return {"request_id": request_id, "status": "needs_input", "stages": {k: v.get("issues") for k, v in case.items() if isinstance(v, dict) and v.get("issues")}}


@server.tool()
def compare_flights(group_size: int, travel_start: str, duration_days: int, origin_airport: str = "SIN") -> dict:
    """Compare dated group flight offers; built-in offers are synthetic and unconfirmed."""
    return flight_search({"inquiry": {"group_size": group_size, "travel_start": travel_start,
                                      "duration_days": duration_days, "origin_airport": origin_airport,
                                      "destination_airport": "CTU"}})


@server.tool()
def find_tours(group_size: int, interests: list[str], accessible: bool = False) -> dict:
    """Search synthetic Chengdu activities by interest, group capacity and accessibility."""
    return tour_search({"inquiry": {"group_size": group_size, "interests": interests, "accessible": accessible}})


@server.tool()
def search_prior_cases(query: str, limit: int = 10) -> list[dict]:
    """Search locally indexed RFQs, schedules and outcome reports."""
    if not (OUTPUT / "cases.sqlite").exists(): return []
    return search_cases(OUTPUT / "cases.sqlite", query, limit)


@server.tool()
def preview_report_email(request_id: str) -> dict:
    """Read the approved workflow's draft email and its generated report attachments."""
    case = stored_case(request_id)
    draft = case["outcome"]["data"]["customer_email_draft"]
    return {"draft": draft, "attachments": [f"{request_id}-decision-brief.docx",
                                             f"{request_id}-management-deck.pptx"],
            "message": "Preview only; no email has been sent."}


@server.tool()
def send_approved_report_email(request_id: str, approval_code: str) -> dict:
    """Send the stored RFQ draft and reports only after a separate human approval code is provided."""
    case = stored_case(request_id)
    outcome = case["outcome"]["data"]
    draft = outcome["customer_email_draft"]
    if outcome["decision"] != "ready_for_human_review" or not draft["send_allowed"]:
        raise ValueError("Workflow evidence and approval gates are incomplete.")
    expected = os.environ.get("TOURISM_EMAIL_APPROVAL_CODE", "")
    if not expected or not hmac.compare_digest(expected, approval_code):
        raise PermissionError("Human approval code is missing or incorrect.")
    recipient = draft["to"]
    allowlist = {x.strip().lower() for x in os.environ.get("TOURISM_EMAIL_ALLOWLIST", "").split(",") if x.strip()}
    if not recipient or recipient.lower() not in allowlist or recipient.endswith(".test"):
        raise PermissionError("Recipient is not allowed for this SMTP configuration.")
    host = os.environ.get("TOURISM_SMTP_HOST")
    sender = os.environ.get("TOURISM_SMTP_FROM")
    user = os.environ.get("TOURISM_SMTP_USER")
    password = os.environ.get("TOURISM_SMTP_PASSWORD")
    if not all((host, sender, user, password)): raise RuntimeError("SMTP configuration is incomplete.")
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, draft["subject"]
    message.set_content(draft["body"])
    for suffix, subtype in (("decision-brief.docx", "vnd.openxmlformats-officedocument.wordprocessingml.document"),
                            ("management-deck.pptx", "vnd.openxmlformats-officedocument.presentationml.presentation")):
        path = OUTPUT / f"{request_id}-{suffix}"
        message.add_attachment(path.read_bytes(), maintype="application", subtype=subtype, filename=path.name)
    port = int(os.environ.get("TOURISM_SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, password)
        smtp.send_message(message)
    return {"request_id": request_id, "recipient": recipient, "status": "sent"}


if __name__ == "__main__":
    server.run(transport="stdio")
