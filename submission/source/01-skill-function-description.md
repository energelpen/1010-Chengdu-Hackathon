# Skill function description

SP-D Organizational Collaboration Office | 27 September 2026

Repository: https://github.com/energelpen/1010-Chengdu-Hackathon

## From a request to organized work

### A workspace that makes collaboration inspectable

Atlas Office brings programmable staff profiles, task routing, skill execution, review gates and generated business files into one local workspace. A colleague has a manager, assigned skills, availability, capacity, follow links and role guidance. The operator can inspect who performed a task, what it produced and what still needs attention.

The entry combines a general company workspace with a specialized Chengdu tourism demonstration. Its 69 registered skills include nine independently callable tourism stages. Local execution creates real draft documents and structured records; the people, supplier offers and tourism task evidence are synthetic.

### At a glance

| 69 registered skills | 9 tourism stages | 4 interfaces |
| --- | --- | --- |
| Office tasks, analysis, governance and optional connected actions | A composable inquiry-to-outcome simulation | Browser workspace, HTTP, CLI and MCP |

### Submission scenario: Product Launch Preparation

The supplied SP-D challenge specifies Product Launch Preparation. The narrated recording follows a complete operator-led preparation simulation for a Chengdu food and tea group-tour product, from one entered brief through 13 distinct skills to a completed simulated management handoff.

The recording includes options, qualified staff allocations, a dependency plan, a responsibility matrix, task status revision, budget variance, a real approval gate for a workbook copy, decision logging, PDF generation and searchable knowledge. Automatic launch completion from one sentence remains unverified; operator inputs and synthetic completion evidence are explicit.

### Who it serves

A sales or operations lead preparing a group-travel product, proposal or internal launch decision; a specialist creating schedules and comparisons; and a manager reviewing blockers, ownership and release conditions. Public information about Sichuan Shanghai Airlines Holiday International Travel Agency Co., Ltd. provides a representative travel-business context, without implying adoption or affiliation.

### Project repository

https://github.com/energelpen/1010-Chengdu-Hackathon

Sources: README.md; resources/company-general.json; resources/tourism-company.json; Challenge Topics.pdf, physical page 6; source-register.md

## Nine skills, one tourism lifecycle

### Independently callable stages

| Stage / skill | Function and observable result |
| --- | --- |
| 01  inquiry-intake | Parse or validate group size, dates, duration and CNY budget; preserve supplied versus extracted fields; return missing-input issues. |
| 02  flight-search | Filter fixture offers by route, dates, seats and price validity; compare group totals and preserve unconfirmed-fare caveats. |
| 03  tour-search | Rank activities by stated interests and check capacity and accessibility; explain rejected candidates. |
| 04  option-comparison | Construct complete quotation alternatives with itemized cost, margin and budget checks; rank feasible options. |
| 05  hierarchy-router | Select a lead and duty owners using skills, availability and capacity; expose capability gaps and reporting routes. |
| 06  workload-splitter | Create owned tasks with dependencies, preparation dates and approval gates for supplier, safety, finance and management. |
| 07  schedule-builder | Place selected activities into dated slots with arrival/departure and timing constraints; surface unscheduled items. |
| 08  execution-controller | Accept a completion event only with the assigned owner, evidence, dependencies and gate conditions; record blockers and escalations. |
| 09  outcome-reporter | Assemble management status, evidence and a customer email draft; hold release when required checks remain incomplete. |

### A reproducible synthetic input

```text
RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage
tour from 2026-10-25, budget CNY 200000.
```

### Decision rules carry the business logic

Group capacity and the customer budget constrain the quotation. Missing supplier, safety or finance evidence blocks release. The demonstration model adds an executive task at CNY 100,000. These thresholds and approvals are authored demo rules, not the reference enterprise's SOP. Flight and tour options are estimates; execution records do not constitute reservations.

Sources: scripts/tourism_core.py; skills/*/SKILL.md; shared/message-schema.json; resources/domain-rules.md; resources/tourism-price-model.json

## Prepare a launch with visible outputs

### A concrete launch preparation task

The recording prepares the launch of a fictional Chengdu food and tea group-tour product. A pilot costing CNY 50,000 is compared with a CNY 120,000 full launch. Supplied impact/risk/cost weights of 5/3/2 produce scores of 75.7 and 62.0, respectively. The executed proposal skill recommends the pilot and creates real Word and PowerPoint files.

### Composable tools for the preparation team

| Skill | Business use / output |
| --- | --- |
| proposal-package | Compare explicitly supplied cost, impact and risk; generate an editable PowerPoint proposal and Word decision brief. |
| project-plan | Turn structured tasks and dependencies into a dated project plan; reject invalid dependency input. |
| responsibility-matrix | Validate colleagues and produce a workbook identifying responsible, accountable, consulted and informed people. |
| workload-rebalance | Allocate work to qualified staff within capacity; expose assignments that need manager attention. |
| scenario-compare | Score options with named criteria, weights and visible component scores; reject missing measurements. |
| management-handoff | Summarize progress, owners and blockers in a Word brief and unsent email draft. |
| task-tracker / decision-log | Persist task status and decision rationale for subsequent inspection. |
| quotation-package / finance-forecast | Create a draft commercial quotation and price schedule, or a scenario-based monthly forecast. |

### Interaction and assignment

The Assistant routes recognized requests to a qualified colleague and records progress. The Skills library offers structured input forms and examples for deliberate invocation. Activity & approvals exposes runs and pending actions; Files & knowledge retains generated artifacts. The Org chart distinguishes reporting, current collaboration and follows.

OpenAI-backed conversation and bounded tool discovery are optional. No-key general-company chat provides local directory/help responses; it does not execute the free-form launch request. The recording uses the typed Skills library to invoke and assign real operations. A selected avatar is role context, not a separate authenticated employee account.

### Current integration boundary

The final recording exercises 13 distinct skills and supplies simulated completion evidence for the preparation tasks. The management handoff records three done tasks; the separate task register shows a blocked-to-done operator update. No real product release, supplier reservation, payment or external message is claimed.

Automatic single-sentence orchestration of the entire launch remains outside the demonstrated scope. The workflow shown is a complete operator-led preparation simulation.

Sources: scripts/intent_router.py; scripts/assistant_service.py; scripts/skill_runtime.py; skills/proposal-package/skill.json; skills/project-plan/skill.json; tests/test_office_skills.py

## Architecture, review and traceability

### Execution path

| Layer | Responsibility |
| --- | --- |
| Workspace | Assistant, colleague profiles, organization view, skill forms, run history and files. |
| Routing and orchestration | Interpret a supported request, choose a qualified person, prepare inputs, invoke the registered handler and expose progress. |
| Shared skill runtime | Validate input schemas; create run records; apply idempotency and approval states; register artifacts and audit events. |
| Domain handlers | Tourism decision rules, office analysis and report generation, or a configured connector adapter. |
| Persistence | Local SQLite stores for runs, conversations and records; an FTS5 case index; generated files in the workspace data directory. |

### Review is part of the workflow

- The tourism workspace defaults to preparing a proposal for review. Return, revise, resubmit and escalate actions preserve a management history.
- Changing a selected option or task owner invalidates affected approvals and evidence. Task completion cannot bypass proposal approval.
- General skills with remote_write or reviewed_write effects stop at awaiting_approval. Approval executes the prepared action; rejection cancels it.
- SMTP delivery and connected services require configuration and explicit review rules. A generated email draft remains unsent in this submission.

### Inspectable results

A shared-runtime result contains the requested skill_id, person_id, status, inputs, output and timestamps. Tourism stage data adds request_id, status, issues and trace references. A completed runtime handler may still contain a blocked domain result; callers must inspect both levels.

A known trace metadata defect affects the inner skill label of five tourism handlers. The requested route and outer skill_id identify the invoked stage correctly. The API reference discloses this limitation; test success is not presented as proof that every metadata field is correct.

### Operating boundary

This is a single-user local prototype bound to 127.0.0.1. Production multi-user use needs identity, authorization, protected audit access and a suitable HTTPS server. Optional supplier, Google, Telegram, SMTP and model services require their own configuration; no live supplier reservation adapter is claimed.

Sources: scripts/skill_runtime.py; scripts/governance.py; scripts/conversation_store.py; scripts/search_store.py; scripts/mcp_bridge.py; app.py

## Evidence and reproducibility

### Checks rerun for this submission on 27 September 2026

| Evidence | Observed result | What it establishes |
| --- | --- | --- |
| Tourism behavior suite | 180 / 180 passed | 20 decision cases per tourism stage; normal, boundary and error conditions. |
| Automated suite | 46 / 46 passed | Integration, assistant, governance and office-skill behaviors checked by the existing suite. |
| Fixed routing corpus | 43 / 43 action prompts; 5 / 5 non-action prompts | Correct first-pass routing on this predefined corpus; not arbitrary-language success. |
| Manifest validation | 69 manifests and examples | Each registered skill has an input schema, an embedded schema-valid example, SKILL.md and a CLI runner. |
| Runtime API example | CNY 1,500; 15% variance | budget-variance executed in isolated local state with budget 10,000 and actual 11,500. |

### Reproduce the core checks

```text
# In chengdu-tourism-office with dependencies installed
python scripts/tourism_office.py test
python -m unittest discover -s tests -p "test_*.py" -q
python tests/trigger_eval.py

# A single independently callable tourism skill
python scripts/tourism_office.py run inquiry-intake '@examples/rfq.json'

# Start the local workspace with fresh state
python app.py --data-dir ./submission-demo-state
```

### Interpretation of the evidence

Tests were rerun locally using the repository's existing checks. Their captured logs are preserved with the submission sources. External-service operations are mocked or require separate credentials; no real mail, booking or payment was performed to create these materials. The 180 behavior cases are reported separately from the 46 automated tests.

The demo video records actual application interactions and 13 completed local skill runs across six roles, with a real awaiting_approval-to-completed spreadsheet edit. Synthetic narration and chapter captions identify the operator-led simulation. This does not establish automatic launch orchestration, enterprise deployment, measured productivity savings or marketplace publication.

### What a production pilot should establish

An authorized operator should validate the company's actual SOPs, replace demo rules and supplier fixtures, and measure preparation time, review rework, task ownership, evidence completeness and exception handling. Proposed pilot measures appear in the Enterprise challenge fit statement; they are targets rather than achieved outcomes.

Sources: submission/source/verification/*.txt; tests/test_skills.py; tests/trigger_eval.py; tests/test_integration.py; tests/test_governance.py; tests/test_office_skills.py
