#!/usr/bin/env python3
"""Local-only web application for the SP-D tourism office simulation."""
from __future__ import annotations

import copy
import os
import json
import re
import sys
import threading
import uuid
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from tourism_core import COMPANY, FLIGHTS, inquiry_intake, run_case, reporting_route
from render_reports import render
from search_store import index_case, search_cases
from assistant_service import public_config, save_api_key, reply as assistant_response
from conversation_store import ConversationStore

STATIC = ROOT / "web"
DATA = Path(os.environ.get("ATLAS_DATA_DIR", str(ROOT / "output")))
COMPANY_FILE = DATA / "company.json"
VALID_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
VALID_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
VALID_VOICE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z]{2,4})?$")
CHAT_LOCK = threading.Lock()


def history_store() -> ConversationStore:
    store = ConversationStore(DATA / "conversations.sqlite")
    store.import_cases(DATA)
    return store


def assistant_person(person_id: str, company: dict, case: dict | None = None) -> dict:
    if person_id == "atlas":
        return {"id": "atlas", "name": "Atlas", "role": "Company Assistant", "voice": "en-US",
                "skills": ["coordination", "planning", "reporting"],
                "agent_instructions": "Help users understand the company, choose the right people and review outcomes."}
    roster = case.get("people_snapshot", company["people"]) if case else company["people"]
    person = next((p for p in roster if p["id"] == person_id), None)
    if person is None:
        raise ValueError("That staff member is not available in this conversation. Choose someone from People.")
    return person


def execute_approved_case(case: dict, generate_reports: bool = True) -> dict:
    """Run the existing simulated evidence pipeline for a reviewed proposal."""
    updated = run_case(case["request"], flight_snapshot=case["flight_snapshot"],
                       people=case["people_snapshot"], auto_execute=True,
                       preferred_option=case.get("selected_option", {}).get("id"),
                       overrides=case.get("overrides", {}))
    for key in ("people_snapshot", "flight_snapshot", "assumptions", "overrides"):
        updated[key] = case.get(key, [] if key in ("people_snapshot", "assumptions") else {})
    return save_case(updated, generate_reports=generate_reports)


def chat(body: dict) -> dict:
    from governance import create_proposal, load_settings, revise_proposal
    message = body.get("message")
    if not isinstance(message, str) or not 1 <= len(message.strip()) <= 6000:
        raise ValueError("Write a message between 1 and 6,000 characters.")
    for key in ("run_workflow", "auto_execute"):
        if key in body and not isinstance(body[key], bool):
            raise ValueError(f"{key} must be true or false.")
    with CHAT_LOCK:
        store = history_store()
        company = load_company()
        cid = body.get("conversation_id")
        conversation = store.get(cid) if cid else None
        request_id = (conversation.get("request_id") if conversation else None) or body.get("request_id")
        case = load_case(request_id) if request_id else None
        person_id = body.get("person_id") or (conversation["person_id"] if conversation else "atlas")
        person = assistant_person(person_id, company, case)
        if conversation is None:
            conversation = store.create(message, person_id)
            if request_id:
                store.link_case(conversation["id"], request_id)
        cid = conversation["id"]
        conversation = store.append(cid, "user", message.strip(), mode="user", request_id=request_id)
        workflow_ran = False
        if body.get("run_workflow", False):
            if company.get("template", "tourism") != "tourism":
                raise ValueError("Choose the Chengdu tourism company template in Settings before running the tourism pipeline. General business tasks run through Skills or chat tools.")
            policy = load_settings(DATA)
            # Planning occurs before policy approval; client flags cannot bypass it.
            try:
                workflow_body = revised_workflow_body(body, case) if case else body
                case = simulate({**workflow_body, "auto_execute": False}, generate_reports=policy.get("generate_reports", True))
                request_id = case["request"]["request_id"]
                store.link_case(cid, request_id)
                prior_proposal = conversation.get("proposal")
                proposal = (revise_proposal(prior_proposal, case, policy, message[:3000], submit=True)
                            if prior_proposal else create_proposal(case, policy))
                store.save_proposal(cid, proposal)
                workflow_ran = True
                if proposal["status"] == "approved":
                    case, proposal = complete_proposal(case, proposal, policy)
                    store.save_proposal(cid, proposal)
                conversation = store.get(cid)
            except (ValueError, FileNotFoundError) as exc:
                conversation = store.append(cid, "assistant", f"The request needs a little more detail: {exc}",
                                            person_id=person_id, name=person["name"], mode="local")
                return {"conversation": conversation, **({"case": case} if case else {})}
        if not case and not workflow_ran:
            from company_chat import reply as company_response
            from skill_runtime import Runtime
            answer = company_response(Runtime(DATA), conversation, person, company,
                                      progress=lambda actor, stage, detail: store.append_event(cid, actor, stage, detail),
                                      telemetry=lambda snapshot: store.save_agent_run(cid, snapshot),
                                      root=ROOT)
            if answer.get("agent_run"):
                store.save_agent_run(cid, answer["agent_run"])
        else:
            answer = assistant_response(ROOT, conversation, person, company, case, workflow_ran)
        if workflow_ran:
            proposal = conversation.get("proposal") or {}
            status = proposal.get("status")
            if status == "pending_review":
                answer["content"] += "\n\nYour proposal is ready for review. Approve it to run the simulated team, or return it with comments."
            elif status == "escalated":
                manager = proposal.get("manager") or {}
                manager_name = manager.get("name", "the responsible manager") if isinstance(manager, dict) else str(manager)
                answer["content"] += f"\n\nThis proposal has been escalated to {manager_name}. Review the listed issues before resubmitting."
        conversation = store.append(cid, "assistant", answer["content"], person_id=person_id,
                                    name=person["name"], mode=answer["mode"], request_id=request_id)
        return {"conversation": conversation, **({"case": case} if case else {}),
                **({"proposal": conversation["proposal"]} if conversation.get("proposal") else {})}


def complete_proposal(case: dict, proposal: dict, policy: dict) -> tuple[dict, dict]:
    """Finish permitted simulation work and any explicitly enabled delivery."""
    from governance import review_proposal
    if policy.get("execute_plan", True):
        case = execute_approved_case(case, generate_reports=policy.get("generate_reports", True))
        proposal = review_proposal(proposal, "complete", "Simulated task evidence has been recorded.", case, internal=True)
    return case, deliver_proposal(case, proposal, policy)


def deliver_proposal(case: dict, proposal: dict, policy: dict) -> dict:
    from governance import review_proposal, send_approved_email
    if not policy.get("send_email"):
        proposal["delivery"] = {"status": "draft", "message": "Email delivery is off in company settings."}
        return proposal
    if policy.get("autonomy_mode") == "approval_required" and not proposal.get("email_approved"):
        proposal["delivery"] = {"status": "awaiting_approval", "message": "Approve email delivery separately after reviewing the draft."}
        return proposal
    try:
        proposal["delivery"] = send_approved_email(case, proposal, policy, DATA)
    except (PermissionError, ValueError, RuntimeError, OSError) as exc:
        # Sender errors contain only intentional, user-facing messages, not SMTP secrets.
        reason = str(exc) if isinstance(exc, (PermissionError, ValueError, RuntimeError)) else "Email delivery could not be completed. Check the server's email connection."
        proposal = review_proposal(proposal, "escalate", reason, case)
        proposal["delivery"] = {"status": "needs_attention", "message": reason}
    return proposal


def review(body: dict) -> dict:
    from governance import load_settings, review_proposal
    with CHAT_LOCK:
        store = history_store()
        conversation = store.get(body.get("conversation_id"))
        proposal = conversation.get("proposal")
        if not proposal or not conversation.get("request_id"):
            raise ValueError("This conversation has no proposal to review. Run a company workflow first.")
        action, comment = body.get("action"), body.get("comment", "")
        if action not in ("approve", "request_changes", "escalate", "resolve", "resubmit", "approve_email"):
            raise ValueError("Choose a supported review action.")
        if not isinstance(comment, str) or len(comment) > 3000:
            raise ValueError("Review comments must be at most 3,000 characters.")
        case = load_case(conversation["request_id"])
        proposal = review_proposal(proposal, action, comment, case)
        policy = load_settings(DATA)
        if action == "approve" and proposal["status"] == "approved":
            case, proposal = complete_proposal(case, proposal, policy)
        elif action == "approve_email":
            proposal = deliver_proposal(case, proposal, policy)
        store.save_proposal(conversation["id"], proposal)
        messages = {
            "approve": ("The proposal has been approved. The permitted simulated team work is now recorded in the linked case."
                        if policy.get("execute_plan", True) else
                        "The proposal has been approved. Task execution remains disabled in company settings; no team tasks were run."),
            "request_changes": "The proposal has been returned with your comments. Update the request or case, then resubmit it for review.",
            "escalate": "The proposal has been escalated to the responsible manager. The issue and comment are recorded for resolution.",
            "resolve": "The resolution is recorded. Resubmit the proposal for a fresh review.",
            "resubmit": "The updated proposal has been resubmitted for review. Its revision and comment history are preserved.",
            "approve_email": "The email delivery approval is recorded. Delivery still follows the saved recipient and connection settings.",
        }
        content = messages[action] + (f"\n\nComment: {comment.strip()}" if comment.strip() else "")
        if proposal.get("status") == "escalated":
            content += "\n\n" + proposal.get("manager_message", "The manager needs to resolve the listed issue before this can proceed.")
        elif proposal.get("delivery", {}).get("status") == "sent":
            content += "\n\nThe reviewed email and permitted attachments were sent to " + proposal["delivery"]["recipient"] + "."
        conversation = store.append(conversation["id"], "assistant", content,
                                    person_id="atlas", name="Atlas", mode="local", request_id=conversation["request_id"])
        return {"conversation": conversation, "case": case, "proposal": proposal}


def load_company() -> dict:
    return json.loads((COMPANY_FILE if COMPANY_FILE.exists() else ROOT / "resources/company-general.json").read_text(encoding="utf-8"))


def save_company(body: dict) -> dict:
    validate_company(body)
    DATA.mkdir(parents=True, exist_ok=True)
    temporary = DATA / ("company-" + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, COMPANY_FILE)
    from skill_runtime import Runtime
    Runtime(DATA).audit("company.saved", "company", {"people": len(body["people"]), "name": body.get("company")})
    return body


def validate_company(data: dict) -> None:
    if not isinstance(data.get("company"), str) or not 1 <= len(data["company"].strip()) <= 150:
        raise ValueError("Company name must be 1–150 characters.")
    people = data.get("people")
    if not isinstance(people, list) or not people or len(people) > 100: raise ValueError("Use 1–100 staff members.")
    ids = [p.get("id") for p in people if isinstance(p, dict)]
    if len(ids) != len(people) or len(set(ids)) != len(ids) or any(not isinstance(x, str) or not VALID_ID.fullmatch(x) for x in ids):
        raise ValueError("Each staff member needs a unique ID of letters, numbers, _ or -.")
    by_id = {p["id"]: p for p in people}
    if sum(p.get("reports_to") is None for p in people) != 1: raise ValueError("The company needs exactly one top-level leader.")
    for person in people:
        portrait = person.get("portrait", person["id"])
        if not isinstance(portrait, str) or not VALID_ID.fullmatch(portrait): raise ValueError("Choose a valid portrait preset.")
        if "department" in person and (not isinstance(person["department"],str) or len(person["department"])>100): raise ValueError("Department must be at most 100 characters.")
        if not isinstance(person.get("name"), str) or not person["name"].strip(): raise ValueError("Every staff member needs a name.")
        if not isinstance(person.get("role"), str) or not person["role"].strip(): raise ValueError("Every staff member needs a role.")
        if not isinstance(person.get("skills"), list) or any(not isinstance(s, str) or not s.strip() for s in person["skills"]):
            raise ValueError("Skills must be a list of nonempty names.")
        if not isinstance(person.get("capacity_hours"), int) or not 1 <= person["capacity_hours"] <= 168:
            raise ValueError("Capacity must be 1–168 hours.")
        if not isinstance(person.get("assigned_hours"), int) or not 0 <= person["assigned_hours"] <= person["capacity_hours"]:
            raise ValueError("Assigned hours must be between zero and capacity.")
        if not isinstance(person.get("available"), bool): raise ValueError("Availability must be true or false.")
        follows = person.get("follows", [])
        if not isinstance(follows, list) or len(follows) > 100 or any(
            not isinstance(target, str) or target not in by_id or target == person["id"] for target in follows
        ): raise ValueError("Follows must reference other existing staff.")
        if not VALID_COLOR.fullmatch(person.get("avatar_color", "#087f7a")):
            raise ValueError("Avatar color must be a six-digit hex color.")
        if not VALID_VOICE.fullmatch(person.get("voice", "en-US")):
            raise ValueError("Voice must be a language tag such as en-US.")
        if person.get("decision_style", "balanced") not in ("balanced", "price", "experience"):
            raise ValueError("Decision style must be balanced, price or experience.")
        guidance = person.get("agent_instructions", "")
        if not isinstance(guidance, str) or len(guidance) > 500:
            raise ValueError("Agent guidance must be at most 500 characters.")
        reporting_route(person["id"], next(iter(by_id)), by_id)


def agent_reply(body: dict) -> dict:
    person_id = body.get("person_id")
    question = str(body.get("question", "")).strip()
    if not question or len(question) > 500: raise ValueError("Ask a question of 1–500 characters.")
    request_id = body.get("request_id")
    case = load_case(request_id) if request_id else None
    roster = case.get("people_snapshot", []) if case else load_company()["people"]
    person = next((p for p in roster if p["id"] == person_id), None)
    if person is None: raise ValueError("Unknown staff member.")
    updates = [u for u in (case.get("agent_updates", []) if case else []) if u["person_id"] == person_id]
    q = question.lower()
    if case and any(word in q for word in ("price", "cost", "budget", "quote", "option")):
        option = case.get("selected_option", {})
        response = (f"The selected {option.get('id', 'option')} is an indicative CNY {option.get('quote_cny', 0):,} "
                    "for the group. Flights and supplier rates are synthetic here; confirm availability and price before a binding offer.")
    elif case and any(word in q for word in ("who", "lead", "report", "manager", "collaborat")):
        hierarchy = case.get("hierarchy", {}).get("data", {})
        duties = [duty for duty, owner in hierarchy.get("assignments", {}).items() if owner == person_id]
        response = (f"I report to {person.get('reports_to') or 'no manager'}. The task lead is "
                    f"{hierarchy.get('task_lead', 'not assigned')}. My assigned duties are {', '.join(duties) or 'none for this case'}.")
    elif case and any(word in q for word in ("status", "done", "next", "task", "progress")):
        response = " ".join(f"{u['task_id']}: {u['state']}. {u['message']}" for u in updates) or "I have no task on this case."
    elif case and any(word in q for word in ("schedule", "day", "itinerary")):
        days = case.get("schedule", {}).get("data", {}).get("days", [])
        response = " ".join(f"Day {day['day_number']} ({day['date']}): " +
                            (", ".join(a["title"] for a in day.get("activities", [])) or "open for planning")
                            for day in days) or "The itinerary is not ready."
    elif case and any(word in q for word in ("risk", "safe", "incident", "approval")):
        execution = case.get("execution", {}).get("data", {})
        count = len(execution.get("incidents", []))
        response = f"There are {count} open incidents. Approval gates and evidence are tracked on the execution board."
    elif updates:
        response = " ".join(u["message"] for u in updates)
    else:
        response = (f"I am {person['name']}, the {person['role']}. My configured skills are "
                    f"{', '.join(person['skills']) or 'none yet'}. Give the company a request to see my work on a case.")
    if person.get("agent_instructions"):
        response += f" My configured focus is: {person['agent_instructions']}"
    return {"person_id": person_id, "name": person["name"], "role": person["role"],
            "answer": response, "voice": person.get("voice", "en-US"),
            "mode": "rule-based simulation; no autonomous external action", "case_id": request_id}


def dated_snapshot(request: dict) -> dict:
    snapshot = copy.deepcopy(FLIGHTS)
    travel = date.fromisoformat(request["travel_start"])
    duration = int(request["duration_days"])
    snapshot["observed_at"] = datetime.now(timezone.utc).isoformat()
    snapshot["source"] = "SYNTHETIC_DEMO_ADAPTED_TO_REQUEST"
    for item in snapshot["offers"]:
        item["origin"] = request.get("origin_airport", "SIN")
        item["depart_date"] = travel.isoformat()
        item["return_date"] = (travel + timedelta(days=duration)).isoformat()
    return snapshot


def prepare_request(body: dict) -> tuple[dict, list[str]]:
    message = body.get("message")
    if not isinstance(message, str) or len(message.strip()) < 15: raise ValueError("Write a task of at least 15 characters.")
    request = {key: body[key] for key in ("message", "type", "group_size", "duration_days", "budget_cny",
                                            "travel_start", "origin_airport", "customer_name", "customer_email") if key in body and body[key] not in (None, "")}
    request["request_id"] = "SIM-" + uuid.uuid4().hex[:10].upper()
    if not request.get("customer_email"):
        email = re.search(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}", message)
        if email:
            request["customer_email"] = email.group(0)
    parsed = inquiry_intake(request)
    assumptions = []
    defaults = {"group_size": 30, "duration_days": 3, "budget_cny": 200000,
                "travel_start": (date.today() + timedelta(days=30)).isoformat()}
    source = parsed.get("data", {}).get("source", {})
    for key, value in defaults.items():
        # Never overwrite a value extracted from the sentence, including an invalid one.
        if source.get(key) == "missing":
            request[key] = value
            assumptions.append(f"{key}={value} (simulation assumption)")
    if "origin_airport" not in request:
        origin = re.search(r"\b(?:from|departing|departure)\s+([A-Z]{3})\b", message)
        request["origin_airport"] = origin.group(1) if origin else "SIN"
        if not origin:
            assumptions.append("origin_airport=SIN (simulation assumption)")
    final = inquiry_intake(request)
    if final["status"] != "ok":
        raise ValueError("; ".join(final["issues"]))
    original = body.get("original_message", message)
    if isinstance(original, str):
        request["original_message"] = original[:6000]
    return request, assumptions


def revised_workflow_body(body: dict, case: dict) -> dict:
    """Apply a partial revision while retaining the linked plan's known facts."""
    message = body["message"]
    prior = case.get("inquiry", {}).get("data", {})
    fields = ("group_size", "duration_days", "budget_cny", "travel_start", "origin_airport",
              "customer_name", "customer_email", "type")
    merged = {key: prior[key] for key in fields if prior.get(key) is not None}
    parsed = inquiry_intake({"message": message})
    extracted = parsed.get("data", {})
    for key, source in extracted.get("source", {}).items():
        if source == "extracted":
            if extracted.get(key) is None:
                raise ValueError(f"The revised {key} is invalid. Correct it before resubmitting.")
            merged[key] = extracted[key]
    origin = re.search(r"\b(?:from|departing|departure)\s+([A-Z]{3})\b", message)
    if origin:
        merged["origin_airport"] = origin.group(1)
    email = re.search(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}", message)
    if email:
        merged["customer_email"] = email.group(0)
    merged.update({key: body[key] for key in fields if key in body and body[key] not in (None, "")})
    original = case.get("request", {}).get("original_message", case.get("request", {}).get("message", ""))
    return {**body, **merged, "message": message + "\nPrevious request: " + original,
            "original_message": original}


def save_case(case: dict, generate_reports: bool = True) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    rid = case["request"]["request_id"]
    if not VALID_ID.fullmatch(rid): raise ValueError("Invalid request ID.")
    path = DATA / f"{rid}-trace.json"
    case["reports_generated"] = bool(generate_reports and "outcome" in case)
    path.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    if "outcome" in case:
        if generate_reports:
            render(case, DATA)
        index_case(DATA / "cases.sqlite", case)
    return case


def load_case(request_id: str) -> dict:
    if not VALID_ID.fullmatch(request_id): raise ValueError("Invalid request ID.")
    path = DATA / f"{request_id}-trace.json"
    if not path.exists(): raise FileNotFoundError("Case not found.")
    return json.loads(path.read_text(encoding="utf-8"))


def simulate(body: dict, generate_reports: bool = True) -> dict:
    request, assumptions = prepare_request(body)
    people = copy.deepcopy(load_company()["people"])
    snapshot = dated_snapshot({**request, **inquiry_intake(request)["data"]})
    case = run_case(request, flight_snapshot=snapshot, people=people,
                    auto_execute=body.get("auto_execute", True),
                    preferred_option=body.get("preferred_option"))
    case.update({"people_snapshot": people, "flight_snapshot": snapshot, "assumptions": assumptions, "overrides": {}})
    return save_case(case, generate_reports=generate_reports)


def update_case(body: dict, operation: str) -> dict:
    # Review and task-board changes must see the same current proposal state.
    with CHAT_LOCK:
        return _update_case(body, operation)


def _update_case(body: dict, operation: str) -> dict:
    from governance import case_fingerprint, case_issues, load_settings, review_proposal, revise_proposal
    case = load_case(str(body.get("request_id", "")))
    store = history_store()
    linked = store.for_case(case["request"]["request_id"])
    policy = load_settings(DATA)
    events = list(case.get("events", []))
    overrides = dict(case.get("overrides", {}))
    preferred_option = case["selected_option"]["id"]
    invalidated_tasks = []
    if operation == "event":
        task_id = body.get("task_id")
        task = next((x for x in case["workload"]["data"]["tasks"] if x["id"] == task_id), None)
        if not task: raise ValueError("Unknown task.")
        action = body.get("action", "complete")
        if action == "complete":
            if linked and not policy.get("execute_plan", True):
                raise PermissionError("Task execution is disabled in company settings. Enable it before completing work.")
            for conversation in linked:
                proposal = conversation["proposal"]
                if proposal.get("status") not in ("approved", "completed"):
                    raise PermissionError("Approve this proposal before completing its tasks.")
                if proposal.get("case_fingerprint") != case_fingerprint(case):
                    raise PermissionError("The plan changed after approval. Resubmit it for review before completing tasks.")
                if proposal.get("issues") or case_issues(case):
                    raise PermissionError("Resolve the proposal's open issues before completing tasks.")
            event = {"task_id": task_id, "actor_id": task["owner_id"], "action": "complete",
                     "evidence_ref": f"SIM:{uuid.uuid4().hex[:8].upper()}"}
            if task["gate"]: event[task["gate"]] = True
        elif action == "incident":
            event = {"task_id": task_id, "action": "incident", "reason": str(body.get("reason") or "Simulated incident")}
        elif action == "resolve_incident":
            event = {"task_id": task_id, "actor_id": task["owner_id"], "action": "resolve_incident",
                     "evidence_ref": f"SIM:RESOLVE:{uuid.uuid4().hex[:8].upper()}"}
        else: raise ValueError("Unknown event action.")
        events.append(event)
    elif operation == "reassign":
        duty, person_id = body.get("duty"), body.get("person_id")
        people = {p["id"]: p for p in case["people_snapshot"]}
        if duty not in case["hierarchy"]["data"]["assignments"] or person_id not in people:
            raise ValueError("Unknown duty or person.")
        skill_needed = {"intake": "intake", "itinerary": "itinerary", "supplier": "supplier", "pricing": "pricing",
                        "safety": "safety", "finance": "financial_approval", "response": "client_email",
                        "report": "reporting", "executive": "executive_approval"}[duty]
        person = people[person_id]
        if skill_needed not in person["skills"] or not person["available"] or person["assigned_hours"] >= person["capacity_hours"]:
            raise ValueError("Selected person lacks this skill or available capacity.")
        if case["hierarchy"]["data"]["assignments"][duty] != person_id:
            affected = {task["id"] for task in case["workload"]["data"]["tasks"] if task["duty"] == duty}
            for task in case["workload"]["data"]["tasks"]:
                if affected.intersection(task["depends_on"]):
                    affected.add(task["id"])
            invalidated_tasks = [task["id"] for task in case["workload"]["data"]["tasks"] if task["id"] in affected]
            events = [event for event in events if event.get("task_id") not in affected]
        overrides[duty] = person_id
    elif operation == "option":
        option_id = body.get("option_id")
        available = [case["comparison"]["data"]["recommended"], *case["comparison"]["data"]["alternatives"]]
        if option_id not in [item["id"] for item in available]: raise ValueError("Unknown or infeasible option.")
        if option_id != preferred_option:
            preferred_option = option_id
            invalidated_tasks = ["PRICING", "FINANCE", "EXECUTIVE", "CLIENT_DRAFT", "REPORT"]
            events = [event for event in events if event.get("task_id") not in invalidated_tasks]
    else:
        raise ValueError("Unknown case operation.")
    updated = run_case(case["request"], flight_snapshot=case["flight_snapshot"], people=case["people_snapshot"],
                       auto_execute=False, events=events, preferred_option=preferred_option, overrides=overrides)
    updated.update({"people_snapshot": case["people_snapshot"], "flight_snapshot": case["flight_snapshot"],
                    "assumptions": case.get("assumptions", []), "overrides": overrides,
                    "invalidated_tasks": invalidated_tasks})
    updated = save_case(updated, generate_reports=policy.get("generate_reports", True))
    plan_changed = case_fingerprint(updated) != case_fingerprint(case)
    for conversation in linked:
        proposal = conversation["proposal"]
        if plan_changed:
            reason = ("The selected option changed; review the updated quotation."
                      if operation == "option" else "The task assignment changed; review the updated workload.")
            proposal = revise_proposal(proposal, updated, policy, reason, submit=False)
        elif operation == "event" and body.get("action", "complete") == "incident":
            proposal = review_proposal(proposal, "escalate", str(body.get("reason") or "A task incident needs management attention."), updated)
        elif (operation == "event" and body.get("action", "complete") == "complete"
              and proposal.get("status") == "approved"
              and updated.get("outcome", {}).get("data", {}).get("decision") == "ready_for_human_review"):
            proposal = review_proposal(proposal, "complete", "The task board recorded the required simulated evidence.", updated, internal=True)
            proposal = deliver_proposal(updated, proposal, policy)
        store.save_proposal(conversation["id"], proposal)
    return updated


class Handler(BaseHTTPRequestHandler):
    def trusted_request(self, mutation: bool = False) -> bool:
        """Keep the local workspace and server credential behind its own origin."""
        expected_port = self.server.server_port
        host = self.headers.get("Host", "")
        if host not in (f"127.0.0.1:{expected_port}", f"localhost:{expected_port}"):
            self.respond(403, {"error": "Open this application through its local address."})
            return False
        if mutation:
            origin = self.headers.get("Origin")
            if (origin and origin != f"http://{host}") or self.headers.get("Sec-Fetch-Site") == "cross-site":
                self.respond(403, {"error": "This action must come from the local company workspace."})
                return False
        return True

    def respond(self, code: int, data: dict | list) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        limit = 21_000_000 if self.path == "/api/files" else 1_000_000
        if not 0 < length <= limit: raise ValueError("Request is too large (1 MB JSON; 15 MB uploaded file).")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict): raise ValueError("Expected JSON object.")
        return value

    def file(self, path: Path, mime: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if not self.trusted_request():
            return
        url = urlparse(self.path)
        try:
            from workspace_api import get as workspace_get
            if workspace_get(self, url, DATA): return
            if getattr(self.server, "api_only", False) and not url.path.startswith(("/api/", "/download/")):
                return self.respond(404, {"error": "API mode is active. Open /docs for API documentation."})
            if url.path in ("/", "/index.html"): return self.file(STATIC / "index.html", "text/html; charset=utf-8")
            if url.path == "/style.css": return self.file(STATIC / "style.css", "text/css; charset=utf-8")
            if url.path == "/chat-format.css": return self.file(STATIC / "chat-format.css", "text/css; charset=utf-8")
            if url.path == "/app.js": return self.file(STATIC / "app.js", "text/javascript; charset=utf-8")
            if url.path == "/agent-run.js": return self.file(STATIC / "agent-run.js", "text/javascript; charset=utf-8")
            if url.path == "/agent-run.css": return self.file(STATIC / "agent-run.css", "text/css; charset=utf-8")
            if url.path == "/avatar.css": return self.file(STATIC / "avatar.css", "text/css; charset=utf-8")
            if url.path == "/avatar.js": return self.file(STATIC / "avatar.js", "text/javascript; charset=utf-8")
            if url.path == "/api/company": return self.respond(200, load_company())
            if url.path == "/api/config": return self.respond(200, public_config(ROOT, load_company()))
            if url.path == "/api/settings":
                from governance import load_settings
                return self.respond(200, load_settings(DATA))
            if url.path == "/api/conversations": return self.respond(200, history_store().list())
            if re.fullmatch(r"/api/conversation/[A-Za-z0-9_-]+/events", url.path):
                return self.respond(200, history_store().events(url.path.split("/")[-2]))
            if re.fullmatch(r"/api/conversation/[A-Za-z0-9_-]+/agent-run", url.path):
                return self.respond(200, history_store().get(url.path.split("/")[-2])["agent_run"])
            if url.path.startswith("/api/conversation/"):
                return self.respond(200, history_store().get(url.path.split("/")[-1]))
            if url.path == "/api/search":
                query = parse_qs(url.query).get("q", [""])[0]
                results = search_cases(DATA / "cases.sqlite", query) if (DATA / "cases.sqlite").exists() else []
                return self.respond(200, results)
            if url.path.startswith("/api/case/"): return self.respond(200, load_case(url.path.split("/")[-1]))
            if url.path.startswith("/download/"):
                name = url.path.split("/")[-1]
                if not re.fullmatch(r"SIM-[A-Za-z0-9_-]+-(?:decision-brief\.docx|management-deck\.pptx|trace\.json)", name):
                    raise ValueError("Invalid download.")
                mime = "application/octet-stream"
                return self.file(DATA / name, mime)
            self.respond(404, {"error": "Not found"})
        except FileNotFoundError as exc: self.respond(404, {"error": str(exc)})
        except (ValueError, TypeError) as exc: self.respond(400, {"error": str(exc)})
        except Exception: self.respond(500, {"error": "The workspace could not load that item. Try again."})

    def do_POST(self) -> None:
        if not self.trusted_request(mutation=True):
            return
        try:
            body = self.body()
            from workspace_api import post as workspace_post
            if workspace_post(self, self.path, body, DATA, load_company, save_company): return
            if self.path == "/api/chat": return self.respond(200, chat(body))
            if self.path == "/api/conversations/new":
                if set(body) != {"title", "person_id"}: raise ValueError("Provide a title and person_id.")
                title, actor = body["title"], body["person_id"]
                if not isinstance(title, str) or not title.strip() or len(title) > 6000: raise ValueError("Write a short conversation title.")
                assistant_person(actor, load_company())
                return self.respond(200, history_store().create(title, actor))
            if self.path == "/api/review": return self.respond(200, review(body))
            if self.path == "/api/settings":
                from governance import save_settings
                return self.respond(200, save_settings(DATA, body))
            if self.path == "/api/config/key":
                if set(body) != {"api_key"}: raise ValueError("Provide only the new API key.")
                save_api_key(ROOT, body["api_key"])
                return self.respond(200, public_config(ROOT, load_company()))
            if self.path == "/api/company":
                return self.respond(200, save_company(body))
            if self.path == "/api/simulate": return self.respond(200, simulate(body))
            if self.path == "/api/event": return self.respond(200, update_case(body, "event"))
            if self.path == "/api/reassign": return self.respond(200, update_case(body, "reassign"))
            if self.path == "/api/option": return self.respond(200, update_case(body, "option"))
            if self.path == "/api/agent": return self.respond(200, agent_reply(body))
            self.respond(404, {"error": "Not found"})
        except FileNotFoundError as exc: self.respond(404, {"error": str(exc)})
        except PermissionError as exc: self.respond(403, {"error": str(exc)})
        except (ValueError, TypeError) as exc: self.respond(400, {"error": str(exc)})
        except Exception: self.respond(500, {"error": "The workspace could not finish that action. Your saved history is preserved."})


def main() -> None:
    global DATA, COMPANY_FILE
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--mode", choices=("gui", "api"), default="gui")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    args = parser.parse_args()
    DATA = args.data_dir.resolve()
    COMPANY_FILE = DATA / "company.json"
    os.environ["ATLAS_DATA_DIR"] = str(DATA)
    print(f"Atlas Company Workspace ({args.mode}) at http://127.0.0.1:{args.port} — API docs: /docs")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.api_only = args.mode == "api"
    server.serve_forever()


if __name__ == "__main__": main()
