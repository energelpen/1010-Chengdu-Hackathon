"""SP-D tourism-office simulation with auditable decisions and no external side effects."""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPANY = json.loads((ROOT / "resources/tourism-company.json").read_text(encoding="utf-8"))
MODEL = json.loads((ROOT / "resources/tourism-price-model.json").read_text(encoding="utf-8"))
FLIGHTS = json.loads((ROOT / "resources/flight-offers.example.json").read_text(encoding="utf-8"))
TOURS = json.loads((ROOT / "resources/tour-catalog.example.json").read_text(encoding="utf-8"))
SKILLS = ("inquiry-intake", "flight-search", "tour-search", "option-comparison", "hierarchy-router",
          "workload-splitter", "schedule-builder", "execution-controller", "outcome-reporter")


def envelope(skill: str, source: dict, status: str, data: dict | None = None, issues: list[str] | None = None, trace: list[str] | None = None) -> dict:
    return {"schema_version": "2.0", "request_id": str(source.get("request_id") or "rfq-001"),
            "skill": skill, "status": status, "data": data or {}, "issues": issues or [], "trace": trace or []}


def whole(value: Any, minimum: int = 1) -> int | None:
    if isinstance(value, bool): return None
    try:
        number = int(value)
        return number if number >= minimum and str(value).replace(",", "").strip() == str(number) else None
    except (ValueError, TypeError): return None


def day(value: Any) -> date | None:
    if not isinstance(value, str): return None
    try: return date.fromisoformat(value)
    except ValueError: return None


def inquiry_intake(source: dict) -> dict:
    skill = SKILLS[0]
    text = source.get("message")
    if not isinstance(text, str) or len(text.strip()) < 15:
        return envelope(skill, source, "needs_input", issues=["message must describe the inquiry in at least 15 characters"])
    text = text.strip()
    inferred = {}
    for key, pattern in {
        "group_size": r"\b(\d+)\s+(?:travellers|travelers|guests|people|pax)\b",
        "duration_days": r"\b(\d+)\s+days?\b",
        "budget_cny": r"(?:CNY|RMB|¥)\s*([\d,]+)",
        "travel_start": r"\b(20\d{2}-\d{2}-\d{2})\b",
    }.items():
        found = re.search(pattern, text, re.IGNORECASE)
        if found: inferred[key] = found.group(1).replace(",", "")
    values = {key: source.get(key, inferred.get(key)) for key in ("group_size", "duration_days", "budget_cny", "travel_start")}
    group = whole(values["group_size"])
    duration = whole(values["duration_days"])
    budget = whole(values["budget_cny"])
    travel = day(values["travel_start"])
    issues = []
    if group is None: issues.append("group_size must be a positive whole number")
    if duration is None or duration > 21: issues.append("duration_days must be 1 to 21")
    if budget is None: issues.append("budget_cny must be a positive whole CNY amount")
    if travel is None: issues.append("travel_start must be a valid ISO date")
    elif travel < date.today(): issues.append("travel_start is in the past")
    request_type = source.get("type", "rfq" if any(term in text.lower() for term in ("rfq", "quote", "quotation")) else "inquiry")
    if request_type not in ("rfq", "inquiry"): issues.append("type must be rfq or inquiry")
    interests = [word for word in ("panda", "food", "tea", "heritage", "museum", "nature") if word in text.lower()]
    customer_email = source.get("customer_email")
    if customer_email is not None and (not isinstance(customer_email, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", customer_email)):
        issues.append("customer_email is invalid")
    origin = source.get("origin_airport", "SIN")
    if not isinstance(origin, str) or not re.fullmatch(r"[A-Z]{3}", origin):
        issues.append("origin_airport must be a three-letter IATA code")
    data = {"type": request_type, "message": text, "group_size": group, "duration_days": duration,
            "budget_cny": budget, "travel_start": travel.isoformat() if travel else None, "interests": interests,
            "origin_airport": origin, "destination_airport": "CTU",
            "customer_email": customer_email, "customer_name": source.get("customer_name"),
            "source": {key: "provided" if key in source else "extracted" if key in inferred else "missing" for key in values},
            "customer_data_notice": "Use only for this simulated inquiry; do not send without explicit approval."}
    return envelope(skill, source, "needs_input" if issues else "ok", data, issues, ["customer:message", "rule:intake-v2"])


def flight_search(source: dict) -> dict:
    skill = "flight-search"
    inquiry = source.get("inquiry")
    if not isinstance(inquiry, dict): return envelope(skill, source, "needs_input", issues=["inquiry object required"])
    group, travel, duration = whole(inquiry.get("group_size")), day(inquiry.get("travel_start")), whole(inquiry.get("duration_days"))
    if not all((group, travel, duration)): return envelope(skill, source, "needs_input", issues=["group size, travel date and duration required"])
    snapshot = source.get("snapshot", FLIGHTS)
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("offers"), list):
        return envelope(skill, source, "needs_input", issues=["snapshot must contain offers array"])
    if snapshot.get("currency") != "CNY": return envelope(skill, source, "needs_input", issues=["flight prices must be normalized to CNY"])
    return_date = (travel + timedelta(days=duration)).isoformat()
    eligible, rejected = [], []
    for offer in snapshot["offers"]:
        if not isinstance(offer, dict): continue
        reasons = []
        if offer.get("origin") != inquiry.get("origin_airport", "SIN") or offer.get("destination") != inquiry.get("destination_airport", "CTU"): reasons.append("route mismatch")
        if offer.get("depart_date") != travel.isoformat() or offer.get("return_date") != return_date: reasons.append("date mismatch")
        if (whole(offer.get("seats")) or 0) < group: reasons.append("insufficient seats for group")
        fare, tax = whole(offer.get("fare_cny_per_person")), whole(offer.get("tax_cny_per_person"), 0)
        if fare is None or tax is None: reasons.append("invalid fare")
        if reasons:
            rejected.append({"id": offer.get("id"), "reasons": reasons}); continue
        total = (fare + tax) * group
        eligible.append({**offer, "group_total_cny": total, "fare_status": "unconfirmed group estimate",
                         "source": snapshot.get("source", "SUPPLIED"), "observed_at": snapshot.get("observed_at")})
    eligible.sort(key=lambda row: (row["group_total_cny"], row["stops"], row["duration_minutes"]))
    data = {"recommended": eligible[0] if eligible else None, "alternatives": eligible[1:],
            "rejected": rejected, "source": snapshot.get("source", "SUPPLIED"),
            "caveat": "Group inventory and final fare require provider or airline confirmation before quotation."}
    return envelope(skill, source, "ok" if eligible else "blocked", data,
                    [] if eligible else ["no flight offer meets group, route and date requirements"],
                    [f"flight-snapshot:{snapshot.get('source', 'SUPPLIED')}", f"observed:{snapshot.get('observed_at', 'unknown')}"])


def tour_search(source: dict) -> dict:
    skill = "tour-search"
    inquiry = source.get("inquiry")
    if not isinstance(inquiry, dict): return envelope(skill, source, "needs_input", issues=["inquiry object required"])
    group = whole(inquiry.get("group_size"))
    if not group: return envelope(skill, source, "needs_input", issues=["positive group size required"])
    catalog = source.get("catalog", TOURS)
    if not isinstance(catalog, dict) or not isinstance(catalog.get("activities"), list):
        return envelope(skill, source, "needs_input", issues=["catalog must contain activities array"])
    interests = set(inquiry.get("interests", []))
    accessible = inquiry.get("accessible", False)
    ranked, rejected = [], []
    for item in catalog["activities"]:
        if not isinstance(item, dict): continue
        reasons = []
        if item.get("max_group", 0) < group: reasons.append("group exceeds capacity")
        if accessible and not item.get("accessible"): reasons.append("accessibility mismatch")
        if reasons:
            rejected.append({"id": item.get("id"), "reasons": reasons}); continue
        match = len(interests & set(item.get("tags", [])))
        ranked.append({**item, "group_total_cny": item["price_cny_per_person"] * group, "interest_matches": match,
                       "availability": "unverified", "source": catalog.get("source", "SUPPLIED")})
    ranked.sort(key=lambda row: (-row["interest_matches"], row["group_total_cny"], row["id"]))
    return envelope(skill, source, "ok" if ranked else "blocked",
                    {"matches": ranked, "rejected": rejected, "source": catalog.get("source", "SUPPLIED"),
                     "caveat": "Tour times, permits and availability require supplier confirmation."},
                    [] if ranked else ["no tour fits group capacity and accessibility requirements"],
                    [f"tour-catalog:{catalog.get('source', 'SUPPLIED')}"])


def option_comparison(source: dict) -> dict:
    skill = SKILLS[1]
    inquiry = source.get("inquiry")
    if not isinstance(inquiry, dict): return envelope(skill, source, "needs_input", issues=["inquiry object required"])
    group, duration, budget, travel = whole(inquiry.get("group_size")), whole(inquiry.get("duration_days")), whole(inquiry.get("budget_cny")), day(inquiry.get("travel_start"))
    if not all((group, duration, budget, travel)): return envelope(skill, source, "needs_input", issues=["complete group, duration, budget and travel date required"])
    horizon = (travel - date.today()).days
    if horizon < 0: return envelope(skill, source, "blocked", issues=["travel date is in the past"])
    priority = source.get("priority", "balanced")
    if priority not in ("balanced", "price", "experience"): return envelope(skill, source, "needs_input", issues=["priority must be balanced, price or experience"])
    flight = source.get("flight")
    activities = source.get("activities", [])
    if flight is not None and (not isinstance(flight, dict) or whole(flight.get("group_total_cny"), 0) is None):
        return envelope(skill, source, "needs_input", issues=["flight must contain a nonnegative group_total_cny"])
    if not isinstance(activities, list) or any(not isinstance(x, dict) or whole(x.get("group_total_cny"), 0) is None for x in activities):
        return envelope(skill, source, "needs_input", issues=["activities must contain valid group totals"])
    flight_total = flight["group_total_cny"] if flight else 0
    activity_total = sum(item["group_total_cny"] for item in activities)
    offers, rejected = [], []
    for option in MODEL["options"]:
        reasons = []
        supplier = option["supplier_cost_cny_per_person_day"] * group * duration
        transport = MODEL["vehicle_cost_cny_per_day_for_groups_over_20"] * duration if group > 20 else 0
        land_quote = round((supplier + transport) * (1 + MODEL["margin_rate"]))
        quote = land_quote + flight_total + activity_total
        if quote > budget: reasons.append("exceeds customer budget")
        if group > option["max_group"]: reasons.append("group exceeds modeled capacity")
        if horizon < option["lead_days"]: reasons.append("insufficient preparation time")
        if reasons:
            rejected.append({"id": option["id"], "quote_cny": quote, "reasons": reasons})
            continue
        affordability = round(100 * (budget - quote) / budget)
        weights = {"balanced": (0.65, 0.35), "price": (0.15, 0.85), "experience": (0.85, 0.15)}[priority]
        score = round(option["experience_score"] * weights[0] + affordability * weights[1], 2)
        offers.append({**option, "supplier_estimate_cny": supplier, "transport_estimate_cny": transport,
                       "land_quote_cny": land_quote, "flight_estimate_cny": flight_total,
                       "activity_estimate_cny": activity_total, "quote_cny": quote,
                       "quote_per_person_cny": round(quote / group), "score": score,
                       "score_parts": {"experience": option["experience_score"], "affordability": affordability},
                       "inventory_status": "unverified", "quote_status": "indicative"})
    offers.sort(key=lambda row: (-row["score"], row["quote_cny"], row["id"]))
    data = {"recommended": offers[0] if offers else None, "alternatives": offers[1:], "rejected": rejected,
            "comparison_priority": priority, "assumptions": MODEL["notice"], "margin_rate": MODEL["margin_rate"],
            "flight_status": "unconfirmed" if flight else "not included",
            "activity_status": "unverified" if activities else "not included"}
    return envelope(skill, source, "ok" if offers else "blocked", data,
                    [] if offers else ["no option fits budget, group size and lead time"], ["model:tourism-price-v1", "inquiry:constraints"])


def ancestry(person_id: str, people: dict[str, dict]) -> list[str]:
    path = []
    while person_id is not None:
        if person_id in path or person_id not in people: raise ValueError("invalid or cyclic reporting hierarchy")
        path.append(person_id)
        person_id = people[person_id].get("reports_to")
    return path


def reporting_route(start: str, end: str, people: dict[str, dict]) -> list[str]:
    up, down = ancestry(start, people), ancestry(end, people)
    common = next(node for node in up if node in down)
    return up[:up.index(common) + 1] + list(reversed(down[:down.index(common)]))


def hierarchy_router(source: dict) -> dict:
    skill = SKILLS[2]
    roster = source.get("people", COMPANY["people"])
    if not isinstance(roster, list) or not roster: return envelope(skill, source, "needs_input", issues=["nonempty people roster required"])
    people = {p.get("id"): p for p in roster if isinstance(p, dict) and p.get("id")}
    if len(people) != len(roster): return envelope(skill, source, "needs_input", issues=["each person needs a unique id"])
    if sum(p.get("reports_to") is None for p in roster) != 1:
        return envelope(skill, source, "needs_input", issues=["roster needs exactly one top-level manager"])
    for person in roster:
        capacity, used = person.get("capacity_hours"), person.get("assigned_hours")
        if (not person.get("name") or not person.get("role") or not isinstance(person.get("skills"), list)
                or not isinstance(person.get("available"), bool) or not isinstance(capacity, int)
                or not isinstance(used, int) or capacity < 1 or used < 0 or used > capacity):
            return envelope(skill, source, "needs_input", issues=["each person needs name, role, skills, availability and valid capacity"])
    try:
        for person_id in people: ancestry(person_id, people)
    except ValueError as exc:
        return envelope(skill, source, "needs_input", issues=[str(exc)])
    required = {"intake": "intake", "itinerary": "itinerary", "supplier": "supplier", "pricing": "pricing",
                "safety": "safety", "finance": "financial_approval", "response": "client_email",
                "report": "reporting", "executive": "executive_approval"}
    assignments, gaps = {}, []
    load = {p["id"]: int(p.get("assigned_hours", 0)) for p in roster}
    for duty, capability in required.items():
        candidates = [p for p in roster if p.get("available", False) and capability in p.get("skills", [])
                      and int(p.get("capacity_hours", 0)) - load[p["id"]] >= 2]
        candidates.sort(key=lambda p: (load[p["id"]] / max(1, p["capacity_hours"]), len(ancestry(p["id"], people)), p["id"]))
        if candidates:
            selected = candidates[0]
            assignments[duty] = selected["id"]
            load[selected["id"]] += 2
        else: gaps.append(duty)
    preferred_lead = "product_manager" if source.get("task_kind") == "inquiry" else "sales_manager"
    coordinators = [p for p in roster if p.get("available") and "coordination" in p.get("skills", [])
                    and p.get("capacity_hours", 0) - load[p["id"]] >= 2]
    coordinators.sort(key=lambda p: ((load[p["id"]] / p["capacity_hours"]) - (0.15 if p["id"] == preferred_lead else 0), p["id"]))
    lead = coordinators[0]["id"] if coordinators else assignments.get("pricing")
    if not lead: gaps.append("accountable lead")
    routes = {duty: reporting_route(lead, person_id, people) for duty, person_id in assignments.items()} if lead else {}
    relationships = [{"from": p["reports_to"], "to": p["id"], "kind": "reports_to"}
                     for p in roster if p.get("reports_to")]
    relationships += [{"from": p["id"], "to": followed, "kind": "follows"}
                      for p in roster for followed in p.get("follows", []) if followed in people and followed != p["id"]]
    relationships += [{"from": lead, "to": person_id, "kind": "collaborates"}
                      for person_id in sorted(set(assignments.values())) if lead and person_id != lead]
    data = {"company": COMPANY["company"], "simulation": True, "formal_hierarchy": [{"id": p["id"], "reports_to": p.get("reports_to"), "role": p.get("role")} for p in roster],
            "task_lead": lead, "assignments": assignments, "routes": routes, "projected_load_hours": load,
            "relationships": relationships, "capability_gaps": gaps,
            "decision_rule": "skill match, availability and projected remaining capacity; lead affinity balanced against load; route through lowest common manager"}
    return envelope(skill, source, "escalated" if gaps else "ok", data, [f"unfilled duty: {x}" for x in gaps], ["roster:tourism-company", "rule:hierarchy-routing-v1"])


def workload_splitter(source: dict) -> dict:
    skill = SKILLS[3]
    inquiry, chosen, hierarchy = source.get("inquiry"), source.get("option"), source.get("hierarchy")
    if not all(isinstance(x, dict) for x in (inquiry, chosen, hierarchy)):
        return envelope(skill, source, "needs_input", issues=["inquiry, option and hierarchy objects required"])
    travel = day(inquiry.get("travel_start"))
    budget, price = whole(inquiry.get("budget_cny")), whole(chosen.get("quote_cny"))
    if not travel or not budget or not price: return envelope(skill, source, "needs_input", issues=["valid travel date, budget and quote required"])
    if price > budget: return envelope(skill, source, "blocked", issues=["chosen quote exceeds customer budget"])
    assigned = hierarchy.get("assignments", {})
    if not isinstance(assigned, dict): return envelope(skill, source, "needs_input", issues=["hierarchy assignments required"])
    tasks = []
    def add(task_id: str, title: str, duty: str, offset: int, effort: int, dependencies: list[str], gate: str | None = None) -> None:
        tasks.append({"id": task_id, "title": title, "owner_id": assigned.get(duty), "duty": duty,
                      "due_date": (travel - timedelta(days=offset)).isoformat(), "effort_hours": effort,
                      "depends_on": dependencies, "gate": gate,
                      "route_from_lead": hierarchy.get("routes", {}).get(duty, [])})
    add("INTAKE", "Confirm traveler needs and consent", "intake", 14, 2, [])
    add("DESIGN", "Build culturally accurate itinerary", "itinerary", 12, 6, ["INTAKE"])
    add("SUPPLIER", "Verify accommodation, guide and transport availability", "supplier", 10, 5, ["DESIGN"], "supplier_confirmed")
    add("PRICING", "Validate quote and exclusions", "pricing", 8, 3, ["SUPPLIER"])
    add("SAFETY", "Review group movement and travel safety", "safety", 7, 4, ["DESIGN"], "safety_cleared")
    add("FINANCE", "Approve margin and payment terms", "finance", 6, 2, ["PRICING"], "approved")
    approvals = ["FINANCE", "SAFETY"]
    if price >= 100000:
        add("EXECUTIVE", "Approve high-value quotation", "executive", 5, 2, ["FINANCE"], "approved")
        approvals.append("EXECUTIVE")
    add("CLIENT_DRAFT", "Draft client quotation email", "response", 3, 2, approvals)
    add("REPORT", "Prepare management outcome report", "report", 2, 2, ["CLIENT_DRAFT"])
    unassigned = [t["id"] for t in tasks if not t["owner_id"]]
    overdue = [t["id"] for t in tasks if day(t["due_date"]) < date.today()]
    critical = {}
    for task in tasks:
        critical[task["id"]] = task["effort_hours"] + max((critical[dep] for dep in task["depends_on"]), default=0)
    data = {"tasks": tasks, "unassigned": unassigned, "past_due": overdue,
            "critical_path_hours": critical["REPORT"], "total_effort_hours": sum(t["effort_hours"] for t in tasks),
            "gross_margin_cny": price - chosen.get("supplier_estimate_cny", 0) - chosen.get("transport_estimate_cny", 0),
            "client_quote_cny": price}
    issues = [f"unassigned tasks: {', '.join(unassigned)}"] if unassigned else []
    if overdue: issues.append(f"due dates already passed: {', '.join(overdue)}")
    return envelope(skill, source, "escalated" if issues else "ok", data, issues, ["rule:rfq-task-dag-v1", "hierarchy:routes", "quote:indicative"])


def schedule_builder(source: dict) -> dict:
    skill = "schedule-builder"
    inquiry, activities = source.get("inquiry"), source.get("activities", [])
    if not isinstance(inquiry, dict) or not isinstance(activities, list):
        return envelope(skill, source, "needs_input", issues=["inquiry and activities array required"])
    start, duration = day(inquiry.get("travel_start")), whole(inquiry.get("duration_days"))
    if not start or not duration: return envelope(skill, source, "needs_input", issues=["valid travel date and duration required"])
    if duration < 2 and activities: return envelope(skill, source, "blocked", issues=["one-day trip has no safe middle-day activity slot"])
    slots = ("morning", "afternoon", "evening")
    days = [{"date": (start + timedelta(days=i)).isoformat(), "day_number": i + 1, "activities": []}
            for i in range(duration + 1)]
    days[0]["activities"].append({"slot": "afternoon", "title": "Arrive in Chengdu and hotel check-in", "source": "workflow"})
    days[-1]["activities"].append({"slot": "morning", "title": "Check-out and departure", "source": "workflow"})
    unscheduled = []
    for activity in activities:
        if not isinstance(activity, dict) or not activity.get("id"):
            unscheduled.append({"id": None, "reason": "invalid activity"}); continue
        preferred = activity.get("preferred_slot", "afternoon")
        if preferred not in slots:
            unscheduled.append({"id": activity["id"], "reason": "unknown preferred slot"}); continue
        if activity.get("duration_minutes", 0) > 240:
            unscheduled.append({"id": activity["id"], "reason": "activity exceeds four-hour slot"}); continue
        placed = False
        for target in days[1:-1]:
            if all(item["slot"] != preferred for item in target["activities"]):
                target["activities"].append({"slot": preferred, "title": activity["name"], "activity_id": activity["id"],
                                             "duration_minutes": activity["duration_minutes"], "source": activity.get("source", "SUPPLIED")})
                placed = True; break
        if not placed: unscheduled.append({"id": activity["id"], "reason": "no conflict-free preferred slot"})
    for target in days: target["activities"].sort(key=lambda item: slots.index(item["slot"]))
    flight = source.get("flight")
    if flight and (flight.get("depart_date") != start.isoformat() or flight.get("return_date") != days[-1]["date"]):
        return envelope(skill, source, "blocked", {"days": days, "unscheduled": unscheduled}, ["flight dates do not match schedule"], ["schedule:date-check"])
    return envelope(skill, source, "escalated" if unscheduled else "ok",
                    {"days": days, "unscheduled": unscheduled, "timezone": "Asia/Shanghai",
                     "booking_status": "unconfirmed", "travel_days": duration + 1},
                    [f"unscheduled activities: {len(unscheduled)}"] if unscheduled else [],
                    ["inquiry:dates", "tour:activity-slots", "flight:dates"])


def execution_controller(source: dict) -> dict:
    skill = SKILLS[4]
    tasks, events = source.get("tasks"), source.get("events", [])
    if not isinstance(tasks, list) or not tasks or not isinstance(events, list):
        return envelope(skill, source, "needs_input", issues=["tasks must be nonempty and events must be a list"])
    known = {t.get("id"): t for t in tasks if isinstance(t, dict) and t.get("id")}
    if len(known) != len(tasks) or any(dep not in known for t in tasks for dep in t.get("depends_on", [])):
        return envelope(skill, source, "needs_input", issues=["task IDs must be unique and dependencies must exist"])
    completed, rejected, incidents = {}, [], []
    for event in events:
        if not isinstance(event, dict) or event.get("task_id") not in known:
            rejected.append({"event": event, "reason": "unknown task"}); continue
        task = known[event["task_id"]]
        if event.get("action") == "incident":
            incidents.append({"task_id": task["id"], "reason": event.get("reason", "unspecified")}); continue
        if event.get("action") == "resolve_incident":
            if event.get("actor_id") != task.get("owner_id") or not event.get("evidence_ref"):
                rejected.append({"event": event, "reason": "resolution needs task owner and evidence_ref"}); continue
            if not any(item["task_id"] == task["id"] for item in incidents):
                rejected.append({"event": event, "reason": "no open incident for task"}); continue
            incidents = [item for item in incidents if item["task_id"] != task["id"]]
            continue
        if event.get("action") != "complete" or not isinstance(event.get("evidence_ref"), str) or not event["evidence_ref"].strip():
            rejected.append({"event": event, "reason": "completion needs action=complete and evidence_ref"}); continue
        if event.get("actor_id") != task.get("owner_id"):
            rejected.append({"event": event, "reason": "actor is not assigned owner"}); continue
        if task["id"] in completed:
            rejected.append({"event": event, "reason": "duplicate completion"}); continue
        if any(dep not in completed for dep in task["depends_on"]):
            rejected.append({"event": event, "reason": "dependency incomplete or event out of order"}); continue
        gate = task.get("gate")
        if gate and event.get(gate) is not True:
            rejected.append({"event": event, "reason": f"missing gate: {gate}"}); continue
        completed[task["id"]] = {"evidence_ref": event["evidence_ref"], "actor_id": event["actor_id"]}
    ready = [t["id"] for t in tasks if t["id"] not in completed and t.get("owner_id") and all(dep in completed for dep in t["depends_on"])]
    blocked = [t["id"] for t in tasks if t["id"] not in completed and t["id"] not in ready]
    draft_ready = "CLIENT_DRAFT" in ready or "CLIENT_DRAFT" in completed
    if incidents: draft_ready = False
    escalations = [{"task_id": item["task_id"], "route": known[item["task_id"]].get("route_from_lead", []), "reason": item["reason"]} for item in incidents]
    data = {"completed": completed, "rejected_events": rejected, "incidents": incidents,
            "ready_tasks": ready, "blocked_tasks": blocked, "client_draft_ready": draft_ready,
            "escalations": escalations, "communication_status": "draft_only"}
    issues = [f"rejected {len(rejected)} event(s)"] if rejected else []
    if incidents: issues.append("open incident blocks client response")
    return envelope(skill, source, "blocked" if incidents else "ok", data, issues,
                    [f"event:{x['evidence_ref']}" for x in completed.values()])


def outcome_reporter(source: dict) -> dict:
    skill = SKILLS[5]
    inquiry, chosen, execution, hierarchy = source.get("inquiry"), source.get("option"), source.get("execution"), source.get("hierarchy")
    if not all(isinstance(x, dict) for x in (inquiry, chosen, execution, hierarchy)):
        return envelope(skill, source, "needs_input", issues=["inquiry, option, execution and hierarchy objects required"])
    eligible = execution.get("client_draft_ready") is True
    completed = execution.get("completed", {})
    if not isinstance(completed, dict): return envelope(skill, source, "needs_input", issues=["execution completed evidence must be an object"])
    final_tasks = ["INTAKE", "DESIGN", "SUPPLIER", "PRICING", "SAFETY", "FINANCE"]
    if chosen.get("quote_cny", 0) >= 100000: final_tasks.append("EXECUTIVE")
    missing = [task for task in final_tasks if task not in completed]
    eligible = eligible and not missing and not execution.get("incidents")
    recipient = inquiry.get("customer_email")
    chosen_name = chosen.get("id", "selected")
    quote = chosen.get("quote_cny")
    draft = {"to": recipient, "subject": f"Indicative Chengdu group tour quotation — {source.get('request_id', 'RFQ')}",
             "body": f"Thank you for your inquiry. Our indicative {chosen_name} option is CNY {quote} for {inquiry.get('group_size')} travelers over {inquiry.get('duration_days')} days. This is subject to supplier availability, final itinerary, contract and payment terms. Please reply with any accessibility or dietary requirements.",
             "status": "draft_only", "send_allowed": bool(eligible and recipient)}
    data = {"decision": "ready_for_human_review" if eligible else "hold", "quote_type": "indicative",
            "selected_option": chosen_name, "quote_cny": quote, "open_gates": missing,
            "task_lead": hierarchy.get("task_lead"), "hierarchy_routes": hierarchy.get("routes", {}),
            "evidence_register": {key: value.get("evidence_ref") for key, value in completed.items()},
            "customer_email_draft": draft, "management_summary": f"{chosen_name.title()} option: CNY {quote}; {len(completed)} tasks evidenced; {len(missing)} gates open.",
            "assumptions": MODEL["notice"], "simulation": True}
    return envelope(skill, source, "ok" if eligible else "blocked", data,
                    [] if eligible else ["quotation cannot be released until all evidence and approval gates pass"],
                    [f"event:{value.get('evidence_ref')}" for value in completed.values()])


HANDLERS = dict(zip(SKILLS, (inquiry_intake, flight_search, tour_search, option_comparison, hierarchy_router,
                            workload_splitter, schedule_builder, execution_controller, outcome_reporter)))


def agent_updates(inquiry: dict, chosen: dict, hierarchy: dict, work: dict, execution: dict,
                  schedule: dict, people: list[dict]) -> list[dict]:
    staff = {person["id"]: person for person in people}
    task_for = {"intake": "INTAKE", "itinerary": "DESIGN", "supplier": "SUPPLIER",
                "pricing": "PRICING", "safety": "SAFETY", "finance": "FINANCE",
                "executive": "EXECUTIVE", "response": "CLIENT_DRAFT", "report": "REPORT"}
    details = {
        "intake": f"I captured {inquiry['group_size']} travelers, {inquiry['duration_days']} days and a CNY {inquiry['budget_cny']:,} budget.",
        "itinerary": f"I organized a {schedule.get('travel_days', len(schedule.get('days', [])))}-day plan around {', '.join(inquiry['interests']) or 'Chengdu highlights'}.",
        "supplier": "I am checking group seats, guide capacity, accommodation and activity availability. Fixture offers are unconfirmed.",
        "pricing": f"I compared package options. The selected {chosen['id']} estimate totals CNY {chosen['quote_cny']:,}, including flights and activities.",
        "safety": "I reviewed the group-movement safety gate and will escalate any open incident.",
        "finance": f"I checked the indicative CNY {chosen['quote_cny']:,} quotation and its visible cost components.",
        "executive": "I review high-value quotations before a customer draft can leave the team.",
        "response": "I prepared a customer-facing quotation draft; it has not been emailed.",
        "report": "I prepare the management outcome, evidence register and downloadable documents.",
    }
    active = {task["id"] for task in work["tasks"]}
    updates = []
    for duty, person_id in hierarchy["assignments"].items():
        task_id = task_for[duty]
        if task_id not in active or person_id not in staff: continue
        person = staff[person_id]
        state = "evidenced" if task_id in execution["completed"] else "ready" if task_id in execution["ready_tasks"] else "waiting"
        updates.append({"person_id": person_id, "name": person["name"], "role": person["role"],
                        "duty": duty, "task_id": task_id, "state": state, "message": details[duty],
                        "source": "deterministic simulation rule", "agent_instructions": person.get("agent_instructions", "")})
    return updates


def run_case(request: dict, flight_snapshot: dict | None = None, tour_catalog: dict | None = None,
             people: list[dict] | None = None, auto_execute: bool = True,
             events: list[dict] | None = None, preferred_option: str | None = None,
             overrides: dict[str, str] | None = None) -> dict:
    inquiry = inquiry_intake(request)
    if inquiry["status"] != "ok": return {"simulation": True, "request": request, "inquiry": inquiry}
    flights = flight_search({"request_id": request["request_id"], "inquiry": inquiry["data"],
                             **({"snapshot": flight_snapshot} if flight_snapshot is not None else {})})
    tours = tour_search({"request_id": request["request_id"], "inquiry": inquiry["data"],
                         **({"catalog": tour_catalog} if tour_catalog is not None else {})})
    if flights["status"] != "ok" or tours["status"] != "ok":
        return {"simulation": True, "request": request, "inquiry": inquiry, "flights": flights, "tours": tours}
    chosen_activities = tours["data"]["matches"][:2]
    hierarchy = hierarchy_router({"request_id": request["request_id"], "task_kind": inquiry["data"]["type"],
                                  **({"people": people} if people is not None else {})})
    roster = people if people is not None else COMPANY["people"]
    leader = next((person for person in roster if person["id"] == hierarchy["data"].get("task_lead")), {})
    priority = request.get("priority", leader.get("decision_style", "balanced"))
    if priority not in ("balanced", "price", "experience"): priority = "balanced"
    comparison = option_comparison({"request_id": request["request_id"], "inquiry": inquiry["data"],
                                    "flight": flights["data"]["recommended"], "activities": chosen_activities,
                                    "priority": priority})
    if comparison["status"] != "ok":
        return {"simulation": True, "request": request, "inquiry": inquiry, "flights": flights,
                "tours": tours, "comparison": comparison, "hierarchy": hierarchy}
    available_options = [comparison["data"]["recommended"], *comparison["data"]["alternatives"]]
    selected = next((item for item in available_options if item["id"] == preferred_option), available_options[0])
    if overrides:
        hierarchy["data"]["assignments"].update(overrides)
        roster = {person["id"]: person for person in (people if people is not None else COMPANY["people"])}
        lead = hierarchy["data"]["task_lead"]
        hierarchy["data"]["routes"] = {duty: reporting_route(lead, person_id, roster)
                                       for duty, person_id in hierarchy["data"]["assignments"].items() if person_id in roster}
        hierarchy["data"]["relationships"] = [edge for edge in hierarchy["data"]["relationships"]
                                                 if edge["kind"] != "collaborates"]
        hierarchy["data"]["relationships"].extend(
            {"from": lead, "to": person_id, "kind": "collaborates"}
            for person_id in sorted(set(hierarchy["data"]["assignments"].values())) if person_id != lead)
    work = workload_splitter({"request_id": request["request_id"], "inquiry": inquiry["data"],
                              "option": selected, "hierarchy": hierarchy["data"]})
    schedule = schedule_builder({"request_id": request["request_id"], "inquiry": inquiry["data"],
                                 "activities": chosen_activities, "flight": flights["data"]["recommended"]})
    if work["status"] == "blocked":
        return {"simulation": True, "request": request, "inquiry": inquiry, "flights": flights, "tours": tours,
                "comparison": comparison, "hierarchy": hierarchy, "workload": work, "schedule": schedule}
    if events is None:
        events = ([{"task_id": t["id"], "actor_id": t["owner_id"], "action": "complete",
                    "evidence_ref": f"SIM:{t['id']}", **({t["gate"]: True} if t["gate"] else {})}
                   for t in work["data"]["tasks"] if t["id"] not in ("CLIENT_DRAFT", "REPORT")] if auto_execute else [])
    execution = execution_controller({"request_id": request["request_id"], "tasks": work["data"]["tasks"], "events": events})
    outcome = outcome_reporter({"request_id": request["request_id"], "inquiry": inquiry["data"],
                                "option": selected, "hierarchy": hierarchy["data"],
                                "execution": execution["data"]})
    updates = agent_updates(inquiry["data"], selected, hierarchy["data"], work["data"], execution["data"], schedule["data"], roster)
    return {"simulation": True, "request": request, "inquiry": inquiry, "flights": flights,
            "tours": tours, "comparison": comparison, "hierarchy": hierarchy, "workload": work,
            "schedule": schedule, "execution": execution, "outcome": outcome,
            "selected_option": selected, "events": events, "auto_execute": auto_execute,
            "agent_updates": updates}


def demo() -> dict:
    return run_case({"request_id": "SIM-RFQ-001",
                     "message": "RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage tour from 2026-10-25, budget CNY 200000.",
                     "customer_name": "Demo Buyer", "customer_email": "buyer@example.test"})
