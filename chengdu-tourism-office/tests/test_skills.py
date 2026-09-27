"""Twenty distinct decision scenarios for each independently callable skill."""
from __future__ import annotations

import copy
import unittest
from datetime import date, timedelta

from scripts.tourism_core import (COMPANY, FLIGHTS, TOURS, inquiry_intake, flight_search,
                                  tour_search, option_comparison, hierarchy_router,
                                  workload_splitter, schedule_builder, execution_controller,
                                  outcome_reporter, day)


def context() -> dict:
    start = date.today() + timedelta(days=30)
    request = {"request_id": "TEST-RFQ", "message": "RFQ for 30 travelers on a 3 day Chengdu food and tea tour.",
               "group_size": 30, "duration_days": 3, "budget_cny": 200000,
               "travel_start": start.isoformat(), "origin_airport": "SIN",
               "customer_email": "buyer@example.test"}
    inquiry = inquiry_intake(request)["data"]
    snapshot = copy.deepcopy(FLIGHTS)
    for offer in snapshot["offers"]:
        offer["depart_date"] = start.isoformat()
        offer["return_date"] = (start + timedelta(days=3)).isoformat()
    flight = flight_search({"inquiry": inquiry, "snapshot": snapshot})["data"]["recommended"]
    tours = tour_search({"inquiry": inquiry})["data"]["matches"]
    chosen = tours[:2]
    option = option_comparison({"inquiry": inquiry, "flight": flight, "activities": chosen})["data"]["recommended"]
    hierarchy = hierarchy_router({})["data"]
    tasks = workload_splitter({"inquiry": inquiry, "option": option, "hierarchy": hierarchy})["data"]["tasks"]
    events = [{"task_id": t["id"], "action": "complete", "actor_id": t["owner_id"],
               "evidence_ref": "TEST:" + t["id"], **({t["gate"]: True} if t["gate"] else {})}
              for t in tasks if t["id"] not in ("CLIENT_DRAFT", "REPORT")]
    execution = execution_controller({"tasks": tasks, "events": events})["data"]
    return locals()


def changed(source: dict, **updates) -> dict:
    value = copy.deepcopy(source)
    value.update(updates)
    return value


def choose(response: dict, path: str):
    value = response
    for key in path.split("."): value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def row(name: str, call, status: str, path: str | None = None, expected=None):
    return (name, call, status, path, expected)


def intake_cases(c):
    base = c["request"]
    run = lambda p: inquiry_intake(p)
    return [
        row("structured_valid",lambda:run(base),"ok","data.group_size",30),
        row("sentence_extract",lambda:run({"message":f"RFQ for 12 travelers on a 2 day Chengdu trip from {c['start'].isoformat()}, budget CNY 40000."}),"ok","data.budget_cny",40000),
        row("short_message",lambda:run(changed(base,message="hi")),"needs_input"),
        row("missing_group",lambda:run(changed({k:v for k,v in base.items() if k!="group_size"},message="Please arrange a cultural visit for our team.")),"needs_input"),
        row("zero_group",lambda:run(changed(base,group_size=0)),"needs_input"),
        row("negative_group",lambda:run(changed(base,group_size=-5)),"needs_input"),
        row("fractional_group",lambda:run(changed(base,group_size=2.5)),"needs_input"),
        row("missing_duration",lambda:run(changed({k:v for k,v in base.items() if k!="duration_days"},message="Please arrange a cultural visit for our team.")),"needs_input"),
        row("long_duration",lambda:run(changed(base,duration_days=22)),"needs_input"),
        row("zero_duration",lambda:run(changed(base,duration_days=0)),"needs_input"),
        row("missing_budget",lambda:run({k:v for k,v in base.items() if k!="budget_cny"}),"needs_input"),
        row("zero_budget",lambda:run(changed(base,budget_cny=0)),"needs_input"),
        row("invalid_date",lambda:run(changed(base,travel_start="2026-02-30")),"needs_input"),
        row("past_date",lambda:run(changed(base,travel_start="2020-01-01")),"needs_input"),
        row("invalid_email",lambda:run(changed(base,customer_email="not-an-email")),"needs_input"),
        row("valid_email",lambda:run(base),"ok","data.customer_email","buyer@example.test"),
        row("lowercase_iata",lambda:run(changed(base,origin_airport="sin")),"needs_input"),
        row("invalid_type",lambda:run(changed(base,type="booking")),"needs_input"),
        row("interests",lambda:run(base),"ok","data.interests",["food","tea"]),
        row("provenance",lambda:run(base),"ok","data.source.group_size","provided"),
    ]


def flight_cases(c):
    inquiry, snap = c["inquiry"], c["snapshot"]
    run=lambda i=inquiry,s=snap:flight_search({"inquiry":i,"snapshot":s})
    def one(**updates):
        snapshot=copy.deepcopy(snap);snapshot["offers"]=[changed(snapshot["offers"][0],**updates)];return snapshot
    return [
        row("group_cheapest",lambda:run(),"ok","data.recommended.id","FL-B"),
        row("missing_inquiry",lambda:flight_search({}),"needs_input"),
        row("missing_group",lambda:run(changed(inquiry,group_size=None)),"needs_input"),
        row("bad_snapshot",lambda:run(s={}),"needs_input"),
        row("currency",lambda:run(s=changed(snap,currency="USD")),"needs_input"),
        row("route",lambda:run(s=one(origin="LHR")),"blocked"),
        row("departure",lambda:run(s=one(depart_date="2030-01-01")),"blocked"),
        row("return",lambda:run(s=one(return_date="2030-01-01")),"blocked"),
        row("seats",lambda:run(s=one(seats=9)),"blocked"),
        row("fare_zero",lambda:run(s=one(fare_cny_per_person=0)),"blocked"),
        row("tax_negative",lambda:run(s=one(tax_cny_per_person=-1)),"blocked"),
        row("group_total",lambda:run(),"ok","data.recommended.group_total_cny",65400),
        row("source",lambda:run(),"ok","data.source","SYNTHETIC_DEMO"),
        row("observed",lambda:run(),"ok","data.recommended.observed_at",snap["observed_at"]),
        row("baggage",lambda:run(),"ok","data.recommended.checked_bag_kg",20),
        row("stops",lambda:run(),"ok","data.recommended.stops",1),
        row("capacity_exact",lambda:run(changed(inquiry,group_size=35),one(seats=35)),"ok"),
        row("origin_change",lambda:run(changed(inquiry,origin_airport="KUL")),"blocked"),
        row("no_offers",lambda:run(s=changed(snap,offers=[])),"blocked"),
        row("fare_caveat",lambda:run(),"ok","data.recommended.fare_status","unconfirmed group estimate"),
    ]


def tour_cases(c):
    inquiry, catalog = c["inquiry"], TOURS
    run=lambda i=inquiry,t=catalog:tour_search({"inquiry":i,"catalog":t})
    return [
        row("interest_rank",lambda:run(),"ok","data.matches.0.id","TOUR-TEA"),
        row("missing_inquiry",lambda:tour_search({}),"needs_input"),
        row("zero_group",lambda:run(changed(inquiry,group_size=0)),"needs_input"),
        row("bad_catalog",lambda:run(t={}),"needs_input"),
        row("large_group",lambda:run(changed(inquiry,group_size=100)),"blocked"),
        row("capacity_reject",lambda:run(),"ok","data.rejected.0.id","TOUR-NATURE"),
        row("accessibility",lambda:run(changed(inquiry,accessible=True)),"ok","data.matches.0.accessible",True),
        row("all_inaccessible",lambda:run(changed(inquiry,accessible=True),{"activities":[catalog["activities"][3]]}),"blocked"),
        row("group_total",lambda:run(),"ok","data.matches.0.group_total_cny",4800),
        row("source",lambda:run(),"ok","data.source","SYNTHETIC_DEMO"),
        row("availability",lambda:run(),"ok","data.matches.0.availability","unverified"),
        row("empty_catalog",lambda:run(t={"activities":[]}),"blocked"),
        row("no_interest",lambda:run(changed(inquiry,interests=[])),"ok"),
        row("panda_interest",lambda:run(changed(inquiry,interests=["panda"])),"ok","data.matches.0.id","TOUR-PANDA"),
        row("tea_interest",lambda:run(changed(inquiry,interests=["tea"])),"ok","data.matches.0.id","TOUR-TEA"),
        row("heritage_interest",lambda:run(changed(inquiry,interests=["heritage"])),"ok","data.matches.0.id","TOUR-MUSEUM"),
        row("capacity_boundary",lambda:run(changed(inquiry,group_size=40)),"ok"),
        row("capacity_41",lambda:run(changed(inquiry,group_size=41)),"blocked"),
        row("accessible_count",lambda:run(changed(inquiry,accessible=True)),"ok","data.matches",lambda x:len(x)==3),
        row("tags",lambda:run(),"ok","data.matches.0.tags",lambda x:"tea" in x),
    ]


def option_cases(c):
    inquiry, flight, acts = c["inquiry"], c["flight"], c["chosen"]
    run=lambda i=inquiry,f=flight,a=acts,p="balanced":option_comparison({"inquiry":i,"flight":f,"activities":a,"priority":p})
    return [
        row("best_balanced",lambda:run(),"ok","data.recommended.id","premium"),
        row("missing_inquiry",lambda:option_comparison({}),"needs_input"),
        row("missing_group",lambda:run(changed(inquiry,group_size=None)),"needs_input"),
        row("zero_budget",lambda:run(changed(inquiry,budget_cny=0)),"needs_input"),
        row("past_date",lambda:run(changed(inquiry,travel_start="2020-01-01")),"blocked"),
        row("invalid_priority",lambda:run(p="luxury"),"needs_input"),
        row("tiny_budget",lambda:run(changed(inquiry,budget_cny=1000)),"blocked"),
        row("over_capacity",lambda:run(changed(inquiry,group_size=46)),"blocked"),
        row("lead_time",lambda:run(changed(inquiry,travel_start=(date.today()+timedelta(days=1)).isoformat())),"blocked"),
        row("price_priority",lambda:run(p="price"),"ok","data.recommended.id","essential"),
        row("experience_priority",lambda:run(p="experience"),"ok","data.recommended.id","premium"),
        row("flight_component",lambda:run(),"ok","data.recommended.flight_estimate_cny",65400),
        row("activity_component",lambda:run(),"ok","data.recommended.activity_estimate_cny",10200),
        row("total_components",lambda:run(),"ok","data.recommended",lambda x:x["quote_cny"]==x["land_quote_cny"]+x["flight_estimate_cny"]+x["activity_estimate_cny"]),
        row("rejected_premium",lambda:run(changed(inquiry,budget_cny=160000)),"ok","data.rejected",lambda x:any(y["id"]=="premium" for y in x)),
        row("land_only",lambda:run(f=None,a=[]),"ok","data.recommended.flight_estimate_cny",0),
        row("no_activities",lambda:run(a=[]),"ok","data.recommended.activity_estimate_cny",0),
        row("invalid_flight",lambda:run(f={"group_total_cny":-1}),"needs_input"),
        row("invalid_activity",lambda:run(a=[{"group_total_cny":"bad"}]),"needs_input"),
        row("quote_status",lambda:run(),"ok","data.recommended.quote_status","indicative"),
    ]


def hierarchy_cases(c):
    roster=COMPANY["people"]
    run=lambda people=roster:hierarchy_router({"people":people})
    def mutate(person_id,**updates):
        people=copy.deepcopy(roster)
        for p in people:
            if p["id"]==person_id:p.update(updates)
        return people
    return [
        row("task_lead",lambda:run(),"ok","data.task_lead","sales_manager"),
        row("all_duties",lambda:run(),"ok","data.assignments",lambda x:len(x)==9),
        row("itinerary_route",lambda:run(),"ok","data.routes.itinerary",lambda x:"director" in x),
        row("safety_route",lambda:run(),"ok","data.routes.safety",lambda x:x[0]=="sales_manager"),
        row("projected_load",lambda:run(),"ok","data.projected_load_hours.sales_manager",lambda x:x>8),
        row("empty_roster",lambda:run([]),"needs_input"),
        row("duplicate_id",lambda:run(roster+[copy.deepcopy(roster[0])]),"needs_input"),
        row("unknown_manager",lambda:run(mutate("sales_exec",reports_to="ghost")),"needs_input"),
        row("cycle",lambda:run(mutate("director",reports_to="sales_exec")),"needs_input"),
        row("all_unavailable",lambda:run([{**p,"available":False} for p in roster]),"escalated"),
        row("missing_intake",lambda:run(mutate("sales_exec",skills=["sales"])),"escalated","data.capability_gaps",lambda x:"intake" in x),
        row("finance_overload",lambda:run(mutate("finance_manager",assigned_hours=29)),"escalated","data.capability_gaps",lambda x:"finance" in x),
        row("unavailable_supplier",lambda:run(mutate("supplier_manager",available=False)),"escalated"),
        row("available_staff",lambda:run(),"ok","data.assignments.intake","sales_exec"),
        row("formal_manager",lambda:run(),"ok","data.formal_hierarchy",lambda x:any(y["id"]=="sales_exec" and y["reports_to"]=="sales_manager" for y in x)),
        row("inquiry_lead",lambda:hierarchy_router({"task_kind":"inquiry"}),"ok","data.task_lead","product_manager"),
        row("pricing_owner",lambda:run(),"ok","data.assignments.pricing","sales_manager"),
        row("executive_owner",lambda:run(),"ok","data.assignments.executive","director"),
        row("report_owner",lambda:run(),"ok","data.assignments.report","account_exec"),
        row("invalid_member",lambda:run(roster+[{"id":"bad"}]),"needs_input"),
    ]


def workload_cases(c):
    inquiry, option, hierarchy = c["inquiry"], c["option"], c["hierarchy"]
    run=lambda i=inquiry,o=option,h=hierarchy:workload_splitter({"inquiry":i,"option":o,"hierarchy":h})
    return [
        row("task_count",lambda:run(),"ok","data.tasks",lambda x:len(x)==9),
        row("executive_gate",lambda:run(),"ok","data.tasks",lambda x:any(t["id"]=="EXECUTIVE" for t in x)),
        row("budget_overrun",lambda:run(changed(inquiry,budget_cny=100000)),"blocked"),
        row("missing_inquiry",lambda:workload_splitter({"option":option,"hierarchy":hierarchy}),"needs_input"),
        row("missing_option",lambda:workload_splitter({"inquiry":inquiry,"hierarchy":hierarchy}),"needs_input"),
        row("missing_hierarchy",lambda:workload_splitter({"inquiry":inquiry,"option":option}),"needs_input"),
        row("bad_date",lambda:run(changed(inquiry,travel_start="bad")),"needs_input"),
        row("missing_budget",lambda:run(changed(inquiry,budget_cny=None)),"needs_input"),
        row("missing_quote",lambda:run(o=changed(option,quote_cny=None)),"needs_input"),
        row("finance_owner",lambda:run(),"ok","data.tasks",lambda x:next(t for t in x if t["id"]=="FINANCE")["owner_id"]=="finance_manager"),
        row("cross_branch_route",lambda:run(),"ok","data.tasks",lambda x:"director" in next(t for t in x if t["id"]=="SAFETY")["route_from_lead"]),
        row("supplier_dependency",lambda:run(),"ok","data.tasks",lambda x:next(t for t in x if t["id"]=="SUPPLIER")["depends_on"]==["DESIGN"]),
        row("due_dates",lambda:run(),"ok","data.tasks",lambda x:all(day(t["due_date"])<=day(inquiry["travel_start"]) for t in x)),
        row("critical_path",lambda:run(),"ok","data.critical_path_hours",lambda x:x>10),
        row("total_effort",lambda:run(),"ok","data.total_effort_hours",lambda x:x>=20),
        row("gross_margin",lambda:run(),"ok","data.gross_margin_cny",lambda x:x>0),
        row("unassigned",lambda:run(h=changed(hierarchy,assignments={})),"escalated","data.unassigned",lambda x:len(x)>0),
        row("short_notice",lambda:run(changed(inquiry,travel_start=(date.today()+timedelta(days=2)).isoformat())),"escalated","data.past_due",lambda x:len(x)>0),
        row("lower_value",lambda:run(o=changed(option,quote_cny=90000)),"ok","data.tasks",lambda x:not any(t["id"]=="EXECUTIVE" for t in x)),
        row("supplier_gate",lambda:run(),"ok","data.tasks",lambda x:next(t for t in x if t["id"]=="SUPPLIER")["gate"]=="supplier_confirmed"),
    ]


def schedule_cases(c):
    inquiry, acts, flight = c["inquiry"], c["chosen"], c["flight"]
    run=lambda i=inquiry,a=acts,f=flight:schedule_builder({"inquiry":i,"activities":a,"flight":f})
    bad=changed(acts[0],preferred_slot="midnight")
    long=changed(acts[0],duration_minutes=300)
    return [
        row("four_calendar_days",lambda:run(),"ok","data.travel_days",4),
        row("arrival",lambda:run(),"ok","data.days.0.activities.0.title",lambda x:"Arrive" in x),
        row("departure",lambda:run(),"ok","data.days.3.activities.0.title",lambda x:"departure" in x),
        row("tea_placed",lambda:run(),"ok","data.days",lambda x:any(a.get("activity_id")=="TOUR-TEA" for d in x for a in d["activities"])),
        row("no_slot_collision",lambda:run(),"ok","data.days",lambda x:all(len({a["slot"] for a in d["activities"]})==len(d["activities"]) for d in x)),
        row("missing_inquiry",lambda:schedule_builder({"activities":acts}),"needs_input"),
        row("invalid_duration",lambda:run(changed(inquiry,duration_days=0)),"needs_input"),
        row("bad_activities",lambda:schedule_builder({"inquiry":inquiry,"activities":"tea"}),"needs_input"),
        row("one_day_activities",lambda:run(changed(inquiry,duration_days=1),f=None),"blocked"),
        row("one_day_empty",lambda:run(changed(inquiry,duration_days=1),a=[],f=None),"ok"),
        row("invalid_slot",lambda:run(a=[bad]),"escalated","data.unscheduled.0.reason","unknown preferred slot"),
        row("overlong",lambda:run(a=[long]),"escalated","data.unscheduled.0.reason","activity exceeds four-hour slot"),
        row("duplicate_slots",lambda:run(a=[acts[0],acts[0],acts[0]]),"escalated","data.unscheduled",lambda x:len(x)==1),
        row("flight_mismatch",lambda:run(f=changed(flight,depart_date="2030-01-01")),"blocked"),
        row("matching_flight",lambda:run(),"ok"),
        row("timezone",lambda:run(),"ok","data.timezone","Asia/Shanghai"),
        row("unconfirmed",lambda:run(),"ok","data.booking_status","unconfirmed"),
        row("slot_source",lambda:run(),"ok","data.days",lambda x:any(a.get("source")=="SYNTHETIC_DEMO" for d in x for a in d["activities"])),
        row("date_sequence",lambda:run(),"ok","data.days",lambda x:x[0]["date"]<x[-1]["date"]),
        row("empty_activities",lambda:run(a=[]),"ok","data.unscheduled",[]),
    ]


def execution_cases(c):
    tasks, events = c["tasks"], c["events"]
    run=lambda t=tasks,e=events:execution_controller({"tasks":t,"events":e})
    first=events[0]
    supplier=next(e for e in events if e["task_id"]=="SUPPLIER")
    safety=next(e for e in events if e["task_id"]=="SAFETY")
    finance=next(e for e in events if e["task_id"]=="FINANCE")
    return [
        row("draft_ready",lambda:run(),"ok","data.client_draft_ready",True),
        row("accepted_evidence",lambda:run(),"ok","data.completed.INTAKE.evidence_ref","TEST:INTAKE"),
        row("missing_tasks",lambda:run(e=[]),"ok","data.ready_tasks",["INTAKE"]),
        row("missing_tasks_input",lambda:execution_controller({}),"needs_input"),
        row("bad_events_type",lambda:execution_controller({"tasks":tasks,"events":"bad"}),"needs_input"),
        row("duplicate_task_ids",lambda:run(t=tasks+[tasks[0]]),"needs_input"),
        row("unknown_dependency",lambda:run(t=[changed(tasks[0],depends_on=["GHOST"])]),"needs_input"),
        row("unknown_task_event",lambda:run(e=[changed(first,task_id="GHOST")]),"ok","data.rejected_events.0.reason","unknown task"),
        row("missing_evidence",lambda:run(e=[changed(first,evidence_ref="")]),"ok","data.rejected_events.0.reason",lambda x:"evidence_ref" in x),
        row("wrong_actor",lambda:run(e=[changed(first,actor_id="director")]),"ok","data.rejected_events.0.reason","actor is not assigned owner"),
        row("out_of_order",lambda:run(e=[events[1]]),"ok","data.rejected_events.0.reason","dependency incomplete or event out of order"),
        row("missing_supplier_gate",lambda:run(e=[*events[:2],{k:v for k,v in supplier.items() if k!="supplier_confirmed"}]),"ok","data.rejected_events.0.reason","missing gate: supplier_confirmed"),
        row("missing_safety_gate",lambda:run(e=[*events[:2],{k:v for k,v in safety.items() if k!="safety_cleared"}]),"ok","data.rejected_events.0.reason","missing gate: safety_cleared"),
        row("missing_finance_gate",lambda:run(e=[*events[:4],{k:v for k,v in finance.items() if k!="approved"}]),"ok","data.rejected_events.0.reason",lambda x:"gate" in x),
        row("duplicate_completion",lambda:run(e=[first,first]),"ok","data.rejected_events.0.reason","duplicate completion"),
        row("incident_blocks",lambda:run(e=[*events,{"task_id":"SAFETY","action":"incident","reason":"road closure"}]),"blocked","data.client_draft_ready",False),
        row("incident_route",lambda:run(e=[*events,{"task_id":"SAFETY","action":"incident","reason":"road closure"}]),"blocked","data.escalations.0.route",lambda x:"director" in x),
        row("incident_resolution",lambda:run(e=[*events,{"task_id":"SAFETY","action":"incident"},{"task_id":"SAFETY","action":"resolve_incident","actor_id":safety["actor_id"],"evidence_ref":"RES:1"}]),"ok","data.incidents",[]),
        row("invalid_resolution",lambda:run(e=[{"task_id":"SAFETY","action":"resolve_incident","actor_id":safety["actor_id"],"evidence_ref":"RES:1"}]),"ok","data.rejected_events.0.reason","no open incident for task"),
        row("draft_only",lambda:run(),"ok","data.communication_status","draft_only"),
    ]


def outcome_cases(c):
    inquiry, option, hierarchy, execution = c["inquiry"], c["option"], c["hierarchy"], c["execution"]
    run=lambda i=inquiry,o=option,h=hierarchy,e=execution:outcome_reporter({"inquiry":i,"option":o,"hierarchy":h,"execution":e})
    return [
        row("ready",lambda:run(),"ok","data.decision","ready_for_human_review"),
        row("email_draft",lambda:run(),"ok","data.customer_email_draft.status","draft_only"),
        row("email_to",lambda:run(),"ok","data.customer_email_draft.to","buyer@example.test"),
        row("send_allowed",lambda:run(),"ok","data.customer_email_draft.send_allowed",True),
        row("quote_type",lambda:run(),"ok","data.quote_type","indicative"),
        row("quote_value",lambda:run(),"ok","data.quote_cny",option["quote_cny"]),
        row("selected_option",lambda:run(),"ok","data.selected_option",option["id"]),
        row("lead",lambda:run(),"ok","data.task_lead","sales_manager"),
        row("evidence",lambda:run(),"ok","data.evidence_register.SUPPLIER","TEST:SUPPLIER"),
        row("assumptions",lambda:run(),"ok","data.assumptions",lambda x:"Synthetic" in x),
        row("missing_inquiry",lambda:outcome_reporter({"option":option,"hierarchy":hierarchy,"execution":execution}),"needs_input"),
        row("missing_option",lambda:outcome_reporter({"inquiry":inquiry,"hierarchy":hierarchy,"execution":execution}),"needs_input"),
        row("missing_hierarchy",lambda:outcome_reporter({"inquiry":inquiry,"option":option,"execution":execution}),"needs_input"),
        row("missing_execution",lambda:outcome_reporter({"inquiry":inquiry,"option":option,"hierarchy":hierarchy}),"needs_input"),
        row("missing_supplier",lambda:run(e=changed(execution,completed={k:v for k,v in execution["completed"].items() if k!="SUPPLIER"})),"blocked","data.open_gates",lambda x:"SUPPLIER" in x),
        row("incident",lambda:run(e=changed(execution,incidents=[{"task_id":"SAFETY"}])),"blocked"),
        row("not_ready",lambda:run(e=changed(execution,client_draft_ready=False)),"blocked"),
        row("no_email",lambda:run(i=changed(inquiry,customer_email=None)),"ok","data.customer_email_draft.send_allowed",False),
        row("executive_required",lambda:run(e=changed(execution,completed={k:v for k,v in execution["completed"].items() if k!="EXECUTIVE"})),"blocked","data.open_gates",lambda x:"EXECUTIVE" in x),
        row("summary",lambda:run(),"ok","data.management_summary",lambda x:option["id"].title() in x),
    ]


BUILDERS = {
    "inquiry-intake": intake_cases, "flight-search": flight_cases, "tour-search": tour_cases,
    "option-comparison": option_cases, "hierarchy-router": hierarchy_cases,
    "workload-splitter": workload_cases, "schedule-builder": schedule_cases,
    "execution-controller": execution_cases, "outcome-reporter": outcome_cases,
}


def run_tests(target: str | None = None) -> None:
    selected = [target] if target else list(BUILDERS)
    suite = unittest.TestSuite()
    for skill in selected:
        scenarios = BUILDERS[skill](context())
        assert len(scenarios) == 20, f"{skill} needs 20 distinct cases"
        for number, (name, call, expected_status, path, expected) in enumerate(scenarios, 1):
            class ScenarioTest(unittest.TestCase):
                def runTest(self, call=call, status=expected_status, path=path, expected=expected, label=f"{skill}/{name}"):
                    response = call()
                    self.assertEqual(response["status"], status, label)
                    if path is not None:
                        actual = choose(response, path)
                        if callable(expected): self.assertTrue(expected(actual), f"{label} {path}: {actual!r}")
                        else: self.assertEqual(actual, expected, label)
                    self.assertEqual(response["schema_version"], "2.0")
            ScenarioTest.__name__ = f"test_{skill.replace('-', '_')}_{number:02d}_{name}"
            suite.addTest(ScenarioTest())
    outcome = unittest.TextTestRunner(verbosity=1).run(suite)
    if not outcome.wasSuccessful(): raise SystemExit(1)
