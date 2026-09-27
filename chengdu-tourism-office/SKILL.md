---
name: chengdu-tourism-office
description: Run a simulated Chengdu tourism company through a customer inquiry or RFQ, with skill-aware hierarchy routing, flight and tour comparison, workload delegation, execution gates, schedules, searchable cases, and client and management reports.
metadata:
  short-description: Tourism-company multi-agent workflow
---

# Chengdu Tourism Office

This SP-D Organizational Collaboration Office package simulates the RFQ desk of a Chengdu tourism company. The named real company is a **public-source reference only**; the employees, reporting lines, quotes, approvals, and customer are fictional. The simulation does not claim affiliation, a live fare, a booking, or a sent email.

The workflow uses nine independently callable agent skills. Read only the skill needed for the current step:

| Stage | Skill | Output |
| --- | --- | --- |
| Understand | [inquiry-intake](skills/inquiry-intake/SKILL.md) | Validated inquiry with input provenance |
| Research | [flight-search](skills/flight-search/SKILL.md) | Group flight comparison, source and seat caveats |
| Research | [tour-search](skills/tour-search/SKILL.md) | Capacity-aware activity shortlist |
| Decide | [option-comparison](skills/option-comparison/SKILL.md) | Ranked complete quotation options |
| Organize | [hierarchy-router](skills/hierarchy-router/SKILL.md) | Skill and capacity assignments plus reporting paths |
| Delegate | [workload-splitter](skills/workload-splitter/SKILL.md) | Dependency graph, owners, dates and approval gates |
| Plan | [schedule-builder](skills/schedule-builder/SKILL.md) | Conflict-aware daily itinerary |
| Control | [execution-controller](skills/execution-controller/SKILL.md) | Accepted evidence, blockers, escalation |
| Report | [outcome-reporter](skills/outcome-reporter/SKILL.md) | Release decision and customer email draft |

Always keep the shared [message contract](shared/message-schema.json). Use the [company model](resources/tourism-company.json) to see formal managers and specialists; a task lead is selected per RFQ and handoffs can cross branches through their common manager. Treat a task event as completed only when the assigned agent supplies evidence and every predecessor and approval gate passes. If a supplier, fare, safety or finance check is missing, hold the quotation.

Run the full simulation after installing [requirements.txt](requirements.txt):

```powershell
python -m pip install -r requirements.txt
python scripts/tourism_office.py demo
python scripts/tourism_office.py search "tea premium"
python scripts/tourism_office.py test
```

The demo creates a JSON trace, Word decision brief, PowerPoint management deck, and local SQLite search index in `output/`. The [MCP server](server/tourism_mcp.py) exposes search, simulation, report preview and separately approved SMTP sending. Configure it using [MCP setup](references/mcp-setup.md). Do not call the send tool merely because an email draft exists: actual delivery needs an explicit user request, a matching approval code and an allowlisted recipient.

For a nontechnical live demo, run `python app.py` and open `http://127.0.0.1:8765`. The office UI lets an operator add staff, edit reporting lines, skills and capacity, program bounded agent guidance and decision style, add follow links, inspect the relationship network, talk to each role-grounded avatar, and hear updates via browser text-to-speech. Dictation is optional and may use the browser's speech service. Without an OpenAI connection, avatar replies are local explanations. With a configured connection, role-grounded model responses are available; general-company chat can discover and invoke assigned skills through a bounded tool loop. These responses do not grant permission for external actions.

For business context and the distinction between public facts and invented demo assumptions, read [source register](references/source-register.md). For live supplier integrations, normalize real offers into the same snapshot schema and preserve the provider, observation time and currency. Group fares and inventory still require confirmation.
