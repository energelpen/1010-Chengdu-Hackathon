# Atlas Office — source map

**Team Atlas · Singapore Polytechnic**

[GitHub repository](https://github.com/energelpen/1010-Chengdu-Hackathon)

The `chengdu-tourism-office/` directory preserves the original tracked application source. At packaging it contains **407 files**, including **78 Markdown files** and **113 Python files**. Package-level reviewer documentation and supporting submission material are additional files.

## Original Agent Skill files

| Location | What to inspect |
| --- | --- |
| [skills/](chengdu-tourism-office/skills/) | All 69 registered skill directories: 60 company skills and nine tourism stages. |
| `skills/<id>/SKILL.md` | Original instructions, purpose, inputs, constraints, handling of missing information and execution guidance. There are 69 such files. |
| `skills/<id>/skill.json` | Runtime ID, title, category, handler, effect, input schema, embedded example and version. There are 69 manifests. |
| `skills/<id>/scripts/run.py` | Independently callable CLI entry point. There are 69 runners; tourism and company runner syntax differ. |
| `skills/<id>/references/example.json` | Separate JSON examples where provided. Every manifest also contains an embedded example; not every example can run without prior state or a connection. |
| `skills/<tourism-id>/scripts/run_tests.py` | Per-stage runner for the tourism decision cases, present for all nine stages. |
| [top-level SKILL.md](chengdu-tourism-office/SKILL.md) | Original orchestration instructions for the tourism workflow. This is a 70th skill instruction file, not a 70th registered runtime skill. |
| [shared/message-schema.json](chengdu-tourism-office/shared/message-schema.json) | Tourism stage envelope contract. |

For a compact code-to-behaviour example, follow [proposal-package/SKILL.md](chengdu-tourism-office/skills/proposal-package/SKILL.md) → [skill.json](chengdu-tourism-office/skills/proposal-package/skill.json) → [run.py](chengdu-tourism-office/skills/proposal-package/scripts/run.py) → [`Runtime.submit`](chengdu-tourism-office/scripts/skill_runtime.py) → [business tool dispatch](chengdu-tourism-office/scripts/business_tools.py) → [`business_packages.proposal`](chengdu-tourism-office/scripts/business_packages.py). The original example creates a weighted comparison and editable decision artifacts without sending anything.

## How the application executes skills

| Layer | Source entry points | Responsibility |
| --- | --- | --- |
| Website and HTTP server | [app.py](chengdu-tourism-office/app.py), [web/app.js](chengdu-tourism-office/web/app.js), [web/workspace.js](chengdu-tourism-office/web/workspace.js) | Local server, conversations, organisation and staff views, skill library, files, settings and user actions. |
| Agent orchestration | [scripts/company_chat.py](chengdu-tourism-office/scripts/company_chat.py) | Model tool loop: discover and read skills, establish a plan, choose qualified profiles, execute skills and report results. |
| Execution tracking | [scripts/agent_execution.py](chengdu-tourism-office/scripts/agent_execution.py), [web/agent-run.js](chengdu-tourism-office/web/agent-run.js) | Dependency and assignment checks, actual call/run statistics, token usage, progress and restored dashboard snapshots. |
| Conversation persistence | [scripts/conversation_store.py](chengdu-tourism-office/scripts/conversation_store.py) | SQLite conversations and persisted agent-run state. |
| Shared runtime | [scripts/skill_runtime.py](chengdu-tourism-office/scripts/skill_runtime.py) | Manifest discovery, JSON schema validation, run records, local artifacts, approval status and audit trail for registered skills. |
| Business handlers | [scripts/business_tools.py](chengdu-tourism-office/scripts/business_tools.py), [scripts/business_packages.py](chengdu-tourism-office/scripts/business_packages.py), [scripts/office_operations.py](chengdu-tourism-office/scripts/office_operations.py) | Documents, spreadsheets, comparisons, plans, finance calculations, records and workflow-specific operations. |
| Tourism engine | [scripts/tourism_core.py](chengdu-tourism-office/scripts/tourism_core.py), [scripts/tourism_office.py](chengdu-tourism-office/scripts/tourism_office.py) | Nine deterministic tourism handlers and their standalone CLI, end-to-end simulation and search commands. |
| Report and case storage | [scripts/render_reports.py](chengdu-tourism-office/scripts/render_reports.py), [scripts/search_store.py](chengdu-tourism-office/scripts/search_store.py) | Tourism Word/PowerPoint reports and searchable case index. |
| Review policy | [scripts/governance.py](chengdu-tourism-office/scripts/governance.py), [references/autonomy.md](chengdu-tourism-office/references/autonomy.md) | Proposal revisions, approval invalidation, execution and delivery gates, and escalation records. |
| Workspace HTTP API | [scripts/workspace_api.py](chengdu-tourism-office/scripts/workspace_api.py) | Shared skill, run, file, record and connection endpoints and API specification. |
| MCP interfaces | [server/company_mcp.py](chengdu-tourism-office/server/company_mcp.py), [server/tourism_mcp.py](chengdu-tourism-office/server/tourism_mcp.py) | Company skill discovery/execution and specialized tourism tools over stdio. The company run tool does not approve external writes. |
| Optional connections | [scripts/assistant_service.py](chengdu-tourism-office/scripts/assistant_service.py), [scripts/google_workspace.py](chengdu-tourism-office/scripts/google_workspace.py), [scripts/telegram_service.py](chengdu-tourism-office/scripts/telegram_service.py), [scripts/mcp_bridge.py](chengdu-tourism-office/scripts/mcp_bridge.py) | Server-side model configuration and optional external service adapters. Account credentials are excluded. |
| Templates and fixtures | [resources/](chengdu-tourism-office/resources/), [examples/](chengdu-tourism-office/examples/), [config/mcp-servers.example.json](chengdu-tourism-office/config/mcp-servers.example.json) | Fictional staff assignments, company templates, synthetic supplier data, example inputs and connection configuration. |

The general-company path uses a model to decide the sequence and arguments of tool calls. The tourism path also provides a deterministic workflow that can be run directly without a model. Both are part of the entry, but a successful deterministic fixture execution is not proof that a model selected its steps.

The [model-driven demonstration](submission/evidence/launch-execution.json) records the former path: one orchestrator delegated to seven fictional profiles. Its statistics count actual completed runtime submissions, with plan steps linked to run IDs. The limits in the orchestration implementation are 48 model requests, 80 function calls and 600 seconds checked between operations; individual model requests have their own timeout. These bounds are implementation limits, not a guarantee that every task succeeds within them.

## Tests and recorded evidence

| Evidence | Purpose |
| --- | --- |
| [tests/test_agent_orchestration.py](chengdu-tourism-office/tests/test_agent_orchestration.py) | Mocked-model behavioural coverage for multi-step execution, skill reading, dependency/approval handling, actual statistics, unfinished plans and persistence. |
| [tests/test_skills.py](chengdu-tourism-office/tests/test_skills.py) | 20 decision scenarios per tourism skill, 180 cases in total. |
| [tests/](chengdu-tourism-office/tests/) | Runtime, business tool, API, governance, integration, assistant and orchestration tests. |
| [tests/trigger_eval.py](chengdu-tourism-office/tests/trigger_eval.py) | Fixed first-pass routing evaluation: 43 action prompts and five non-action prompts, with no model calls. |
| [captured validation](submission/source/verification/results.json) | Previously captured check statuses and companion console logs. |
| [launch-execution.json](submission/evidence/launch-execution.json) | Single demo prompt, measured agent state, runtime inputs/results, records, file registry and final response. |
| [agent-timeline.json](submission/evidence/agent-timeline.json) | Timestamped progress snapshots from the actual recording. |
| [generated-files/](submission/evidence/generated-files/) | Ten actual downloaded demo outputs. |
| [evidence README](submission/evidence/README.md) | Interpretation of measured execution and the separate read-only website tour. |
| [demo script](submission/demo-script.md) | Narration, chapter sequence and reproduction context for the published demo. |

Read [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) for the portable setup and check commands. The optional browser smoke script assumes Playwright, a running app and a specific Windows Edge path; it is not a prerequisite for checking the skills.

## Documentation and known scope

The [complete API Markdown](submission/source/02-api-documentation.md) and [PDF](submission/02-api-documentation.pdf) document all registered skills and the application interfaces. [The skill function description](submission/source/01-skill-function-description.md) explains the submission's intended behaviour, and [the enterprise fit statement](submission/source/04-enterprise-challenge-fit.md) distinguishes the proposed business application from measured results.

Original documentation is retained with the source. Where the existing API appendix gives `--input` as a general runner pattern, apply it to the 60 company runners; the nine tourism runners use positional JSON or `@path` as shown in the reviewer guide. Five tourism handlers retain legacy inner `skill` labels; use the requested route and the outer runtime `skill_id` as stage identity, and inspect the inner domain status.

The original [source register](chengdu-tourism-office/references/source-register.md) distinguishes public context from fictional staff, prices, policies and outcomes. Its references to the organizer's original Challenge Topics and Judging Rubric PDFs identify source materials used during development; those third-party reference documents are not the Agent Skill implementation. The GitHub repository is available for broader project context.

The source is a local single-user prototype. A deployment for real employees would need identity, authorization, secured hosting and authenticated enterprise data. The supplied simulation does not establish live bookings, payments, messages, supplier verification or real business savings.
