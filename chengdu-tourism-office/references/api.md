# Skill and application API

This page introduces the specialized tourism API. For the shared runtime, all 69 skill parameter sets, workspace routes, errors and review states, use the [complete API PDF](../../submission/02-api-documentation.pdf) or its [Markdown edition](../../submission/source/02-api-documentation.md). The source is published in the [GitHub repository](https://github.com/energelpen/1010-Chengdu-Hackathon).

Known metadata limitation: five tourism handlers retain legacy inner `skill` labels. Use the requested route and shared runtime's outer `skill_id` as the stage identity. Inspect the inner domain status even when a runtime run says `completed`.

All nine skills take one JSON object and return the [shared envelope](../shared/message-schema.json). Call one independently with:

```powershell
python scripts/tourism_office.py run inquiry-intake '@examples/rfq.json'
```

| Skill | Required input | Main output |
| --- | --- | --- |
| `inquiry-intake` | `message`; group/date/budget may be in the sentence or fields | normalized inquiry, provenance, missing fields |
| `flight-search` | `inquiry`; optional `snapshot` | eligible and rejected group fares |
| `tour-search` | `inquiry`; optional `catalog` | ranked activities and capacity rejects |
| `option-comparison` | `inquiry`; optional `flight`, `activities`, `priority` | ranked full quotes and cost breakdown |
| `hierarchy-router` | optional `people` roster | lead, skill assignments, reporting routes and gaps |
| `workload-splitter` | `inquiry`, selected `option`, `hierarchy` | dated task graph, owners and approval gates |
| `schedule-builder` | `inquiry`, `activities`; optional `flight` | daily agenda and unscheduled activities |
| `execution-controller` | `tasks`, ordered `events` | accepted evidence, rejects, ready tasks and escalations |
| `outcome-reporter` | `inquiry`, `option`, `hierarchy`, `execution` | release decision, evidence register and email draft |

The local application binds to `127.0.0.1:8765` by default:

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/company` | GET / POST | Read or replace staff, skills, capacity, avatar color, voice, decision style, follows and reporting lines |
| `/api/config` | GET | Read AI key presence, model, mode and company name; never returns a credential |
| `/api/conversations` | GET | List saved conversations, newest first, with previews and linked case IDs |
| `/api/conversation/{id}` | GET | Read a conversation, messages and current proposal review |
| `/api/conversation/{id}/agent-run` | GET | Read the persisted agent plan, calls, actual runs, artifact counts and provider token usage |
| `/api/conversation/{id}/events` | GET | Read timestamped assistant progress events |
| `/api/chat` | POST | Chat with Atlas or a staff avatar; optionally run a company workflow under saved policy |
| `/api/settings` | GET / POST | Read or update company autonomy, reports, email rules and automatic quotation limit |
| `/api/review` | POST | Approve, return with comments, escalate, resolve, resubmit, or separately approve delivery |
| `/api/simulate` | POST | Run one inquiry; `message` required, `auto_execute` optional |
| `/api/case/{id}` | GET | Read a saved trace |
| `/api/event` | POST | Complete, raise or resolve a simulated task event |
| `/api/reassign` | POST | Move a duty to a qualified, available person |
| `/api/option` | POST | Select another feasible quote option; invalidates pricing and downstream approval evidence |
| `/api/agent` | POST | Ask a staff avatar a question grounded in the saved case; accepts `person_id`, `question`, optional `request_id` |
| `/api/search?q=...` | GET | Search saved case contents |
| `/download/{filename}` | GET | Download a generated DOCX, PPTX or trace |

The app's `output/` is local state. OpenAI chat is optional and configured only on the server. Flight and tour prices remain synthetic. Real email requires saved opt-in rules, a reviewed proposal, an allowed recipient and SMTP configuration.

## Chat and history contract

General company chat uses the configured Responses model to choose and execute skills. Multi-step requests publish a model-authored dependency plan. The UI polls the agent-run endpoint while the chat POST runs and restores the saved snapshot when reopening the conversation. The execution budget is 48 model requests, 80 function calls and 600 seconds checked between operations; model requests time out after 120 seconds. Pending reviewed or remote writes do not count as completed skills. See the full API reference for the telemetry fields and status values.

`POST /api/chat` accepts:

```json
{
  "message": "What is the budget for this proposal?",
  "conversation_id": "CHAT-existing-id",
  "person_id": "finance_manager",
  "run_workflow": false
}
```

`message` is required (1–6,000 characters). Omit `conversation_id` to start a thread. `person_id` defaults to `atlas` or the thread's last selected person; switching to a staff ID preserves the linked case and conversation. An optional `request_id` can link an existing case to a new conversation. `run_workflow: true` prepares a tourism case. The server's saved review policy governs execution; the legacy `auto_execute` client flag cannot bypass it.

The response is `{ "conversation": {...}, "case": {...}, "proposal": {...} }`, with `case` and `proposal` omitted when none exist. A conversation has `id`, `title`, `created_at`, `updated_at`, `person_id`, `request_id`, `proposal` and ordered `messages`. Each message has `id`, `role`, `content`, `person_id`, `name`, `mode`, `created_at` and optional `request_id`. Assistant modes are `openai`, `local` or `error`. Provider errors return a saved conversation with an explanatory assistant message; raw provider exceptions are never exposed.

`GET /api/conversations` returns `{id,title,updated_at,person_id,request_id,preview}` items. Existing `*-trace.json` cases are imported once into history. New messages are committed to SQLite before the provider request, and SQLite connections close after every operation.

`GET /api/config` returns:

```json
{
  "ai_configured": false,
  "model": "gpt-6-astra",
  "mode": "local",
  "key_location": ".env or OPENAI_API_KEY",
  "company_name": "Company name"
}
```

## Review contract

`POST /api/review` takes `conversation_id`, `action` and `comment`. Actions are `approve`, `request_changes`, `escalate`, `resolve`, `resubmit` and `approve_email`. It returns the refreshed `{conversation,case,proposal}`. Returning, escalating or resolving a proposal requires an explanation. A returned proposal must be updated through the request or case controls before resubmission; comments alone are recorded feedback, not an implicit edit to the itinerary or quote.

Proposal fields include `status`, `revision`, `comments`, `audit`, `manager`, `issues`, `suggested_resolution`, `manager_message`, `policy_snapshot` and optional `delivery`. Case fingerprints bind approval to the reviewed request, quote, schedule and assignments. Settings and valid transitions are documented in [governance](autonomy.md).

All browser mutations must originate from the local application. The app rejects cross-origin posts and unexpected Host headers, and does not serve `.env` or arbitrary files. These local checks do not replace authentication for a multi-user deployment.
