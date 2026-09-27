import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
def s(heading, paragraphs=None, bullets=None, table=None, code=None):
    return {k:v for k,v in locals().items() if v is not None}
def page(title, kicker, sections, sources):
    return dict(title=title,kicker=kicker,sections=sections,sources=sources)

doc = dict(title='Atlas Office', subtitle='Skill function description',
           version='SP-D Organizational Collaboration Office | 27 September 2026', pages=[
page('From a request to organized work', '01 / ENTRY OVERVIEW', [
 s('A workspace that makes collaboration inspectable', [
   'Atlas Office brings programmable staff profiles, task routing, skill execution, review gates and generated business files into one local workspace. A colleague has a manager, assigned skills, availability, capacity, follow links and role guidance. The operator can inspect who performed a task, what it produced and what still needs attention.',
   'The entry combines a general company workspace with a specialized Chengdu tourism demonstration. Its 69 registered skills include nine independently callable tourism stages. Local execution creates real draft documents and structured records; the people, supplier offers and tourism task evidence are synthetic.'
 ]),
 s('At a glance', table={'headers':['69 registered skills','9 tourism stages','4 interfaces'], 'rows':[
   ['Office tasks, analysis, governance and optional connected actions','A composable inquiry-to-outcome simulation','Browser workspace, HTTP, CLI and MCP']]}),
 s('Submission scenario: Product Launch Preparation', [
   'The supplied SP-D challenge specifies Product Launch Preparation. The accompanying recording demonstrates working launch decision support: a one-sentence options request, an assigned colleague, a generated decision brief and presentation, followed by explicit planning through the skill library.',
   'The tourism workflow is the deeper domain adaptation. The current prototype does not yet verify the whole product-launch lifecycle, across multiple people, from one sentence to completion. This distinction is preserved throughout the submission.'
 ]),
 s('Who it serves', [
   'A sales or operations lead preparing a group-travel product, proposal or internal launch decision; a specialist creating schedules and comparisons; and a manager reviewing blockers, ownership and release conditions. Public information about Sichuan Shanghai Holiday International Travel Service Co., Ltd. provides a representative travel-business context, without implying adoption or affiliation.'
 ])
], ['README.md; resources/company-general.json; resources/tourism-company.json', 'Challenge Topics.pdf, physical page 6; source-register.md']),
page('Nine skills, one tourism lifecycle', '02 / SPECIALIZED BUSINESS LOGIC', [
 s('Independently callable stages', table={'headers':['Stage / skill','Function and observable result'], 'rows':[
   ['01  inquiry-intake','Parse or validate group size, dates, duration and CNY budget; preserve supplied versus extracted fields; return missing-input issues.'],
   ['02  flight-search','Filter fixture offers by route, dates, seats and price validity; compare group totals and preserve unconfirmed-fare caveats.'],
   ['03  tour-search','Rank activities by stated interests and check capacity and accessibility; explain rejected candidates.'],
   ['04  option-comparison','Construct complete quotation alternatives with itemized cost, margin and budget checks; rank feasible options.'],
   ['05  hierarchy-router','Select a lead and duty owners using skills, availability and capacity; expose capability gaps and reporting routes.'],
   ['06  workload-splitter','Create owned tasks with dependencies, preparation dates and approval gates for supplier, safety, finance and management.'],
   ['07  schedule-builder','Place selected activities into dated slots with arrival/departure and timing constraints; surface unscheduled items.'],
   ['08  execution-controller','Accept a completion event only with the assigned owner, evidence, dependencies and gate conditions; record blockers and escalations.'],
   ['09  outcome-reporter','Assemble management status, evidence and a customer email draft; hold release when required checks remain incomplete.']
 ]}),
 s('A reproducible synthetic input', code='RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage\ntour from 2026-10-25, budget CNY 200000.'),
 s('Decision rules carry the business logic', [
   'Group capacity and the customer budget constrain the quotation. Missing supplier, safety or finance evidence blocks release. The demonstration model adds an executive task at CNY 100,000. These thresholds and approvals are authored demo rules, not the reference enterprise\'s SOP. Flight and tour options are estimates; execution records do not constitute reservations.'
 ])
], ['scripts/tourism_core.py; skills/*/SKILL.md; shared/message-schema.json', 'resources/domain-rules.md; resources/tourism-price-model.json']),
page('Prepare a launch with visible outputs', '03 / GENERAL COMPANY CAPABILITIES', [
 s('A concrete launch preparation task', [
   'The recording uses a customer-portal launch as a controlled validation example. In the tourism business setting the same preparation pattern can support the launch of a new group-travel product: compare launch approaches, assign preparation responsibilities, identify capacity constraints and deliver a management pack.'
 ]),
 s('Composable tools for the preparation team', table={'headers':['Skill','Business use / output'], 'rows':[
   ['proposal-package','Compare explicitly supplied cost, impact and risk; generate an editable PowerPoint proposal and Word decision brief.'],
   ['project-plan','Turn structured tasks and dependencies into a dated project plan; reject invalid dependency input.'],
   ['responsibility-matrix','Validate colleagues and produce a workbook identifying responsible, accountable, consulted and informed people.'],
   ['workload-rebalance','Allocate work to qualified staff within capacity; expose assignments that need manager attention.'],
   ['scenario-compare','Score options with named criteria, weights and visible component scores; reject missing measurements.'],
   ['management-handoff','Summarize progress, owners and blockers in a Word brief and unsent email draft.'],
   ['task-tracker / decision-log','Persist task status and decision rationale for subsequent inspection.'],
   ['quotation-package / finance-forecast','Create a draft commercial quotation and price schedule, or a scenario-based monthly forecast.']
 ]}),
 s('Interaction and assignment', [
   'The Assistant routes recognized requests to a qualified colleague and records progress. The Skills library offers structured input forms and examples for deliberate invocation. Activity & approvals exposes runs and pending actions; Files & knowledge retains generated artifacts. The Org chart distinguishes reporting, current collaboration and follows.',
   'OpenAI-backed conversation and bounded tool discovery are optional. No-key mode uses local responses and deterministic routing. A selected avatar is a role context, not a separate authenticated employee account. The recording uses no-key local mode.'
 ]),
 s('Current integration boundary', [
   'These preparation tools work individually and in selected packaged workflows. The recording shows the actual sequence and its operator inputs. It does not treat generated planning files as evidence that a real product launch has been executed.'
 ])
], ['scripts/intent_router.py; scripts/assistant_service.py; scripts/skill_runtime.py', 'skills/proposal-package/skill.json; skills/project-plan/skill.json; tests/test_office_skills.py']),
page('Architecture, review and traceability', '04 / IMPLEMENTATION DESIGN', [
 s('Execution path', table={'headers':['Layer','Responsibility'], 'rows':[
   ['Workspace','Assistant, colleague profiles, organization view, skill forms, run history and files.'],
   ['Routing and orchestration','Interpret a supported request, choose a qualified person, prepare inputs, invoke the registered handler and expose progress.'],
   ['Shared skill runtime','Validate input schemas; create run records; apply idempotency and approval states; register artifacts and audit events.'],
   ['Domain handlers','Tourism decision rules, office analysis and report generation, or a configured connector adapter.'],
   ['Persistence','Local SQLite stores for runs, conversations and records; an FTS5 case index; generated files in the workspace data directory.']
 ]}),
 s('Review is part of the workflow', bullets=[
   'The tourism workspace defaults to preparing a proposal for review. Return, revise, resubmit and escalate actions preserve a management history.',
   'Changing a selected option or task owner invalidates affected approvals and evidence. Task completion cannot bypass proposal approval.',
   'General skills with remote_write or reviewed_write effects stop at awaiting_approval. Approval executes the prepared action; rejection cancels it.',
   'SMTP delivery and connected services require configuration and explicit review rules. A generated email draft remains unsent in this submission.'
 ]),
 s('Inspectable results', [
   'A shared-runtime result contains the requested skill_id, person_id, status, inputs, output and timestamps. Tourism stage data adds request_id, status, issues and trace references. A completed runtime handler may still contain a blocked domain result; callers must inspect both levels.',
   'A known trace metadata defect affects the inner skill label of five tourism handlers. The requested route and outer skill_id identify the invoked stage correctly. The API reference discloses this limitation; test success is not presented as proof that every metadata field is correct.'
 ]),
 s('Operating boundary', [
   'This is a single-user local prototype bound to 127.0.0.1. Production multi-user use needs identity, authorization, protected audit access and a suitable HTTPS server. Optional supplier, Google, Telegram, SMTP and model services require their own configuration; no live supplier reservation adapter is claimed.'
 ])
], ['scripts/skill_runtime.py; scripts/governance.py; scripts/conversation_store.py', 'scripts/search_store.py; scripts/mcp_bridge.py; app.py']),
page('Evidence and reproducibility', '05 / VERIFICATION AND LIMITS', [
 s('Checks rerun for this submission on 27 September 2026', table={'headers':['Evidence','Observed result','What it establishes'], 'rows':[
   ['Tourism behavior suite','180 / 180 passed','20 decision cases per tourism stage; normal, boundary and error conditions.'],
   ['Automated suite','46 / 46 passed','Integration, assistant, governance and office-skill behaviors checked by the existing suite.'],
   ['Fixed routing corpus','43 / 43 action prompts; 5 / 5 non-action prompts','Correct first-pass routing on this predefined corpus; not arbitrary-language success.'],
   ['Manifest validation','69 manifests and examples','Each registered skill has an input schema, an embedded schema-valid example, SKILL.md and a CLI runner.'],
   ['Runtime API example','CNY 1,500; 15% variance','budget-variance executed in isolated local state with budget 10,000 and actual 11,500.']
 ]}),
 s('Reproduce the core checks', code='# In chengdu-tourism-office with dependencies installed\npython scripts/tourism_office.py test\npython -m unittest discover -s tests -p "test_*.py" -q\npython tests/trigger_eval.py\n\n# A single independently callable tourism skill\npython scripts/tourism_office.py run inquiry-intake \'@examples/rfq.json\'\n\n# Start the local workspace with fresh state\npython app.py --data-dir ./submission-demo-state'),
 s('Interpretation of the evidence', [
   'Tests were rerun locally using the repository\'s existing checks. Their captured logs are preserved with the submission sources. External-service operations are mocked or require separate credentials; no real mail, booking or payment was performed to create these materials. The 180 behavior cases are reported separately from the 46 automated tests.',
   'The demo video records actual local app interactions with synthetic inputs. It establishes the preparation features shown on screen. It does not establish enterprise deployment, measured productivity savings, marketplace publication or completion of the entire required Product Launch Preparation scenario.'
 ]),
 s('What a production pilot should establish', [
   'An authorized operator should validate the company\'s actual SOPs, replace demo rules and supplier fixtures, and measure preparation time, review rework, task ownership, evidence completeness and exception handling. Proposed pilot measures appear in the Enterprise challenge fit statement; they are targets rather than achieved outcomes.'
 ])
], ['submission/source/verification/*.txt; tests/test_skills.py; tests/trigger_eval.py', 'tests/test_integration.py; tests/test_governance.py; tests/test_office_skills.py'])
])
(OUT/'skill_description.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding='utf-8')

summary = '''Atlas Office is an organizational collaboration workspace for product-launch preparation and group-travel operations, aligned with the SP-D Organizational Collaboration Office challenge and the culture, commerce and tourism theme.

Its representative enterprise context is Sichuan Shanghai Holiday International Travel Service Co., Ltd. Public descriptions of destination services, business travel and MICE inform the workflow design; the enterprise has not endorsed, adopted or supplied private SOPs for this prototype.

Atlas Office models colleagues through their roles, managers, skills, availability, capacity and working relationships. A user can request a launch proposal, inspect the assigned colleague and execution record, compare options, and receive editable business files. The package contains 69 registered skills, including proposal generation, project planning, responsibility matrices, workload allocation, scenario comparison and management handoff.

Nine independently callable tourism skills form a specialized simulation: inquiry intake, flight search, tour search, option comparison, hierarchy routing, workload splitting, schedule building, execution control and outcome reporting. They apply capacity and budget constraints, track dependencies and evidence, and hold release when required checks are missing. The workspace preserves conversations, review decisions, files and searchable case records. External writes require review.

The demo records actual Product Launch Preparation features in a clean local workspace: a one-sentence launch-options request, staff assignment, generated Word and PowerPoint outputs, and explicit project planning. Full multi-person launch execution from one sentence remains an integration gap; the submission does not claim that this requirement is complete.

Verification on 27 September 2026 passed 180 tourism behavior checks and 46 automated tests. A fixed routing corpus matched 43 of 43 action prompts and left 5 of 5 non-action prompts unassigned. These are bounded test results, not general success rates or measured enterprise savings.

The core value is visible responsibility, inspectable decisions and reusable preparation work. Staff, supplier prices and tourism execution evidence are fictional; no real booking or payment occurs. OpenAI and external connectors are optional. The current app is a single-user local prototype; an enterprise pilot would validate real SOPs, access controls and measurable business outcomes.'''
assert len(summary) <= 3000
(OUT.parent/'06-entry-summary.txt').write_text(summary,encoding='utf-8')
(OUT/'summary-metadata.json').write_text(json.dumps({'characters':len(summary),'maximum':3000},indent=2),encoding='utf-8')
print('Wrote skill description; summary characters:',len(summary))
