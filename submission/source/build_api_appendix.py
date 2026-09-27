"""Build a compact, source-verified 69-skill parameter reference for the PDF."""
from pathlib import Path
import json
import math
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1] / "chengdu-tourism-office"
manifests = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((PROJECT / "skills").glob("*/skill.json"))]

# The tourism manifests declare generic object schemas. These parameter details
# are read from tourism_core.py rather than represented as stricter manifest rules.
tourism = {
    "inquiry-intake": [
        "message*: string - RFQ or inquiry text, at least 15 trimmed characters. request_id: string - trace identifier (default rfq-001).",
        "group_size, duration_days, budget_cny: positive whole values, supplied explicitly or extracted from message; duration 1-21 days. travel_start: string - non-past YYYY-MM-DD date, explicit or extracted. These four business facts are required for status ok.",
        "type: string - rfq or inquiry, otherwise inferred. origin_airport: string - uppercase three-letter code (default SIN). customer_email: string/null - optional draft recipient. customer_name: value - optional retained customer label. Interests are extracted from message; destination is CTU."
    ],
    "flight-search": [
        "inquiry*: object - normalized trip. inquiry.group_size*, duration_days*: positive whole values; inquiry.travel_start*: ISO date. inquiry.origin_airport: string (default SIN); destination_airport: string (default CTU). request_id: string - trace identifier.",
        "snapshot: object - optional replacement for bundled synthetic fixture; currency must be CNY and offers must be an array. Optional source and observed_at identify provenance.",
        "snapshot.offers[]: id, origin, destination, depart_date, return_date, seats, fare_cny_per_person, tax_cny_per_person, stops, duration_minutes. Route/date/capacity/fare checks reject unsuitable offers; stops and duration sort eligible offers. Use the full fixture shape in resources/flight-offers.example.json."
    ],
    "tour-search": [
        "inquiry*: object; inquiry.group_size*: positive whole value. inquiry.interests: array<string> (default []); inquiry.accessible: boolean (default false). request_id: string - trace identifier.",
        "catalog: object - optional replacement for the bundled activity fixture; activities must be an array. Optional source identifies provenance.",
        "catalog.activities[]: id, name, max_group, accessible, tags, price_cny_per_person, preferred_slot, duration_minutes. Capacity and accessibility filter candidates; interest matches and group price determine ranking. Full fixture: resources/tour-catalog.example.json."
    ],
    "option-comparison": [
        "inquiry*: object with group_size*, duration_days*, budget_cny*: positive whole values and travel_start*: non-past ISO date. request_id: string - trace identifier.",
        "flight: object with nonnegative group_total_cny, or omitted. activities: array<object>, each with nonnegative group_total_cny (default []). priority: string - balanced, price or experience (default balanced).",
        "Uses resources/tourism-price-model.json for land cost, margin, capacity and lead-time rules. Returns blocked when no modeled option fits the supplied constraints."
    ],
    "hierarchy-router": [
        "people: array<object> - optional roster; defaults to bundled tourism staff. task_kind: string - inquiry favors the product manager; other values favor sales. request_id: string - trace identifier.",
        "people[]: id, name, role, skills (array), reports_to (staff ID or null), capacity_hours and assigned_hours (nonnegative numeric), available (boolean); follows is an optional staff-ID array. IDs must be unique with one top manager, valid acyclic reporting links and skill/capacity matches.",
        "Required roster structure is enforced by the handler, not a detailed manifest schema. Use resources/tourism-company.json as the complete roster example."
    ],
    "workload-splitter": [
        "inquiry*: object with travel_start*: ISO date and budget_cny*: positive whole value. option*: object with quote_cny*: positive whole value; supplier_estimate_cny and transport_estimate_cny optionally support margin calculation.",
        "hierarchy*: object; assignments maps duty names to owner IDs. routes optionally maps duty names to reporting paths. request_id: string - trace identifier.",
        "Pass option-comparison.data.recommended and hierarchy-router.data. Unassigned work and past due dates escalate. The executive approval task is added for quote_cny >= 100000."
    ],
    "schedule-builder": [
        "inquiry*: object with travel_start*: ISO date and duration_days*: positive whole value. activities: array<object> (default []). request_id: string - trace identifier.",
        "activities[]: id, name and duration_minutes; optional preferred_slot (morning, afternoon or evening; default afternoon) and source. Slots are limited to four hours; unplaced activities are reported.",
        "flight: optional object with depart_date and return_date matching the itinerary. The output spans duration_days + 1 dates, including arrival and departure, in Asia/Shanghai."
    ],
    "execution-controller": [
        "tasks*: nonempty array<object>. tasks[]: id*, owner_id, depends_on* (task-ID array), gate (flag name or null), route_from_lead (optional reporting path). Task IDs must be unique; dependencies must exist. request_id: string - trace identifier.",
        "events: ordered array<object> (default []). events[]: task_id, action (complete, incident or resolve_incident); complete/resolve_incident require the assigned actor_id and evidence_ref. Completion also requires true for the task's dynamic gate flag, when present.",
        "Incident events may carry reason. Dependencies must already be evidenced; duplicates, unknown tasks, missing evidence and out-of-order events are rejected in output."
    ],
    "outcome-reporter": [
        "inquiry*, option*, hierarchy*, execution*: objects. request_id: string - trace identifier. inquiry uses customer_email, group_size and duration_days; option uses id and quote_cny; hierarchy uses task_lead and routes.",
        "execution.client_draft_ready must be true for release readiness. execution.completed must be an object keyed by task IDs with evidence_ref values; execution.incidents must contain no open incident.",
        "Expected evidence: INTAKE, DESIGN, SUPPLIER, PRICING, SAFETY and FINANCE, plus EXECUTIVE for quote_cny >= 100000. Missing evidence returns hold/blocked. Output is an unsent customer email draft and management evidence register."
    ]
}

def kind(schema):
    t = schema.get("type")
    if isinstance(t, list):
        return "/".join(t)
    if t == "array":
        return "array<" + kind(schema.get("items", {})) + ">"
    if t:
        return t
    if "enum" in schema:
        return "enum"
    return "JSON value"

def constraints(schema):
    notes = []
    if "enum" in schema:
        notes.append("one of " + "/".join(str(v) for v in schema["enum"]))
    if "minimum" in schema: notes.append(">=" + str(schema["minimum"]))
    if "exclusiveMinimum" in schema: notes.append(">" + str(schema["exclusiveMinimum"]))
    if "maximum" in schema: notes.append("<=" + str(schema["maximum"]))
    if "exclusiveMaximum" in schema: notes.append("<" + str(schema["exclusiveMaximum"]))
    if "minItems" in schema or "maxItems" in schema:
        notes.append("items " + str(schema.get("minItems", 0)) + "-" + str(schema.get("maxItems", "unbounded")))
    if schema.get("format"):
        notes.append("format " + schema["format"])
    if schema.get("pattern"):
        notes.append("pattern " + schema["pattern"])
    if "minLength" in schema and schema["minLength"] > 0:
        notes.append("nonempty" if schema["minLength"] == 1 else "min " + str(schema["minLength"]) + " chars")
    # Full maximum string lengths remain in the machine-readable manifest. Include
    # short business-meaningful maxima; 10,000-char generic maxima add little here.
    if "maxLength" in schema and schema["maxLength"] < 1000:
        notes.append("max " + str(schema["maxLength"]) + " chars")
    if isinstance(schema.get("additionalProperties"), dict):
        notes.append("values " + kind(schema["additionalProperties"]))
    return ", ".join(notes)

def description(name, schema):
    title = schema.get("description") or schema.get("title") or name.replace("_", " ")
    title = title.rstrip(".")
    facts = constraints(schema)
    return title + ("; " + facts if facts else "")

def fields_text(schema, prefix=""):
    required = set(schema.get("required", []))
    output = []
    for name, field in schema.get("properties", {}).items():
        output.append(name + ("*" if name in required else "") + ": " + kind(field) + " - " + description(name, field))
    return "; ".join(output) + "." if output else "No parameters; supply {}."

def nested_text(schema, prefix=""):
    output = []
    for name, field in schema.get("properties", {}).items():
        path = prefix + name
        candidate = field
        while candidate.get("type") == "array":
            candidate = candidate.get("items", {})
            path += "[]"
        if candidate.get("properties"):
            output.append(path + " members: " + fields_text(candidate))
            output.extend(nested_text(candidate, path + "."))
    return output

def section(skill):
    id = skill["id"]
    paragraphs = [skill["description"] + " Effect: " + skill["effect"] + "."]
    if id in tourism:
        paragraphs.extend(tourism[id])
        paragraphs.append("Schema note: the manifest accepts an object; detailed business validation is in tourism_core.py.")
    else:
        schema = skill["input_schema"]
        paragraphs.append("Parameters: " + fields_text(schema))
        paragraphs.extend(nested_text(schema))
    paragraphs.append("Reference: skills/" + id + "/skill.json (#/input_schema, #/example). GET /api/skills/" + id + ".")
    return {"heading": id + " | " + skill["title"], "paragraphs": paragraphs}

assert len(manifests) == 69
for skill in manifests:
    Draft202012Validator.check_schema(skill["input_schema"])
    assert not list(Draft202012Validator(skill["input_schema"]).iter_errors(skill["example"])), skill["id"]
    base = PROJECT / "skills" / skill["id"]
    assert (base / "SKILL.md").is_file(), skill["id"]
    assert (base / "scripts" / "run.py").is_file(), skill["id"]

pages = [{
    "title": "Complete skill parameter reference",
    "kicker": "APPENDIX / 69 VERIFIED SKILL MANIFESTS",
    "sections": [{
        "heading": "How to call every skill",
        "paragraphs": [
            "The following 69 entries cover every registered skill in this submission. The first line states purpose and effect; each entry then lists input parameters, their types and required flags, nested fields, and the exact manifest and endpoint for full schema and example data.",
            "A star (*) means required in the containing object. A field without a star is optional. array<T> indicates a JSON array whose elements have type T. A union such as string/number allows either type. An empty string is still a supplied value where permitted. All numbers must be finite.",
            "Read each entry's JSON example from skills/<id>/skill.json at #/example and its complete schema at #/input_schema. GET /api/skills/<id> returns these plus SKILL.md instructions. All paths in this appendix are relative to chengdu-tourism-office/.",
            "All 69 manifests, embedded examples, SKILL.md files and CLI runners were checked. All embedded examples satisfy their declared schemas. Some examples contain placeholder file, run or record IDs, and connected-service examples need their corresponding account configuration before execution. Schema validity does not imply a completed external operation."
        ]
    }, {
        "heading": "Shared request wrapper",
        "code": "POST /api/skills/<id>/run\n{\n  \"inputs\": { \"skill-specific fields\": \"values\" },\n  \"person_id\": \"atlas\",\n  \"idempotency_key\": \"optional-unique-key\"\n}",
        "paragraphs": [
            "Only inputs is required in this wrapper. All entries below describe the object inside inputs. For MCP, pass the same object as run_skill's arguments. For CLI, save it as JSON and use python skills/<id>/scripts/run.py --input <path>.",
            "The nine tourism manifests declare generic object schemas, so their handler-level parameters are documented explicitly from tourism_core.py. The remaining skills use detailed schema properties. Their full string-length limits and any additional schema restrictions remain visible in the referenced manifest."
        ]
    }, {
        "heading": "Effect and review policy",
        "table": {
            "headers": ["Effect", "Runtime behavior"],
            "rows": [
                ["local", "Runs immediately on local data; may create files or records"],
                ["remote_read", "Reads a configured external service without a review stop"],
                ["remote_write", "Prepares awaiting_approval; review is required to execute"],
                ["reviewed_write", "Local file/finance change is held for review before execution"]
            ]
        },
        "paragraphs": ["These effects are manifest declarations enforced by the shared runtime. External MCP calls are conservatively marked remote_write even when a selected tool appears read-only. Tourism autonomy settings do not bypass general skill approvals."]
    }],
    "sources": ["scripts/skill_runtime.py", "scripts/workspace_api.py", "scripts/tourism_core.py", "skills/*/skill.json"]
}]

for i in range(0, len(manifests), 5):
    group = manifests[i:i+5]
    pages.append({
        "title": "Skill reference " + str(i+1).zfill(2) + "-" + str(i+len(group)).zfill(2),
        "kicker": "APPENDIX / PARAMETERS " + str(i+1).zfill(2) + "-" + str(i+len(group)).zfill(2) + " OF 69 | * REQUIRED",
        "sections": [section(s) for s in group],
        "sources": ["skills/" + s["id"] + "/skill.json" for s in group]
    })

document = {
    "title": "Atlas Office",
    "subtitle": "Complete skill API parameter appendix",
    "version": "69 manifests and embedded examples verified 27 September 2026",
    "pages": pages,
    "verification": {
        "manifest_count": len(manifests),
        "schema_valid_examples": len(manifests),
        "instruction_files": len(manifests),
        "cli_runners": len(manifests),
        "tourism_generic_object_schemas": list(tourism),
        "skill_ids": [s["id"] for s in manifests]
    },
    "full_manifests": manifests
}
path = HERE / "api_skill_appendix.json"
path.write_text(json.dumps(document, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"file": str(path), "pages": len(pages), "skills": len(manifests),
                  "bytes": path.stat().st_size,
                  "page_words": [sum(len(str(s).split()) for s in p["sections"]) for p in pages]}, indent=2))
