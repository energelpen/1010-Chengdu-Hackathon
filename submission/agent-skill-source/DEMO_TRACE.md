# Recorded launch: prompt, skills and evidence

**Team Atlas — Singapore Polytechnic**

This index is generated from [launch-execution.json](submission/evidence/launch-execution.json). It describes the preserved successful run, not a newly executed demonstration. Business inputs and outcomes are simulated; tool calls and file creation are real.

## One initiating request

> Run an end-to-end SIMULATION of launching a Chengdu food-and-tea group-tour product, from evaluating options to recording the simulated launch outcome and delivering the executive pack. Compare a CNY 50,000 pilot with a CNY 120,000 full launch; assume 30 guests and a preparation start of 1 October 2026. You may invent clearly labeled, internally consistent simulation assumptions for all missing facts. Choose the approach, assign qualified colleagues with capacity, plan dependencies and responsibilities, create the campaign and launch checklist, track work, assess risks, calculate budget variance and a finance forecast, record the simulated decision and outcome, and produce editable proposal slides, a Word management handoff, an Excel budget and a final PDF report. Save and retrieve the launch knowledge for reuse. Execute the local skills yourself in this one turn and show the actual plan, delegated staff, calls and statistics. Everything is simulated; do not contact anyone, use external accounts, make payments, book travel, or claim a real product launch. Finish all local preparation and simulated reporting automatically without asking me to operate the skills.

## Measured execution

| Measure | Recorded value |
|---|---:|
| Completed skill executions | 20 |
| Distinct skills | 16 |
| Fictional delegated colleagues | 7 |
| Generated files | 10 |
| Model requests | 24 |
| Function-tool calls | 26 |
| Failed / pending skills | 0 / 0 |
| Elapsed seconds | 303.8 |
| Provider-reported total tokens | 800,795 |

Token usage is summed across requests and includes repeated context; it is not a cost estimate or unique-context size. The 26 function calls include planning/discovery operations as well as the 20 skill executions. Seven staff profiles represent delegation inside one model-driven orchestrator.

## Published plan and matching runs

| Step | Skill instructions | Assignee | Depends on | Status | Runtime run ID |
|---|---|---|---|---|---|
| S01 | [team-capacity](chengdu-tourism-office/skills/team-capacity/SKILL.md) | `ops_manager` | — | completed | `run_62efe6f09db944ff88a65bfaf9a4be90` |
| S02 | [proposal-package](chengdu-tourism-office/skills/proposal-package/SKILL.md) | `sales_manager` | S01 | completed | `run_7e06ef0f33f84bd3b9c820729344f030` |
| S03 | [decision-log](chengdu-tourism-office/skills/decision-log/SKILL.md) | `director` | S02 | completed | `run_62e4f3a6d8b6470d9c1e5f731ab7a019` |
| S04 | [project-plan](chengdu-tourism-office/skills/project-plan/SKILL.md) | `ops_manager` | S03 | completed | `run_6c5ce806dc5d437b90ac675d1469ae9b` |
| S05 | [responsibility-matrix](chengdu-tourism-office/skills/responsibility-matrix/SKILL.md) | `ops_manager` | S04 | completed | `run_def062ae8350403fa38b40789411d45d` |
| S06 | [campaign-plan](chengdu-tourism-office/skills/campaign-plan/SKILL.md) | `product_manager` | S03, S04 | completed | `run_b43f96aae6564812b3147054c7391ccb` |
| S07 | [risk-register](chengdu-tourism-office/skills/risk-register/SKILL.md) | `ops_manager` | S04, S06 | completed | `run_3ff1a25982e14ca9bf6540c9a92ab240` |
| S08 | [policy-checklist](chengdu-tourism-office/skills/policy-checklist/SKILL.md) | `itinerary_specialist` | S05, S06, S07 | completed | `run_aabc6ec812f2499fbd2888dea40426f9` |
| S09 | [task-tracker](chengdu-tourism-office/skills/task-tracker/SKILL.md) | `product_manager` | S08 | completed | `run_483b02acf6324fcf9e0c759004b1f3c4` |
| S10 | [budget-variance](chengdu-tourism-office/skills/budget-variance/SKILL.md) | `finance_manager` | S08 | completed | `run_03067b5bc9aa4a73991413bd108e13c1` |
| S11 | [spreadsheet-create](chengdu-tourism-office/skills/spreadsheet-create/SKILL.md) | `finance_manager` | S10 | completed | `run_1093043173fd4ebbba27c5451a4869d9` |
| S12 | [finance-forecast](chengdu-tourism-office/skills/finance-forecast/SKILL.md) | `finance_manager` | S10 | completed | `run_55a93062141f4c6ea6d48d3b1a8ade6f` |
| S13 | [decision-log](chengdu-tourism-office/skills/decision-log/SKILL.md) | `director` | S09, S11, S12 | completed | `run_459c3e660bb64fc4bcb37c62cdc9368c` |
| S14 | [task-tracker](chengdu-tourism-office/skills/task-tracker/SKILL.md) | `ops_manager` | S13 | completed | `run_2cebbd0acd134e2ab267935deab7cc3b` |
| S15 | [knowledge-save](chengdu-tourism-office/skills/knowledge-save/SKILL.md) | `transport_coordinator` | S13, S14 | completed | `run_90c49f37b68349f9a91cf5b765b2fa03` |
| S16 | [knowledge-search](chengdu-tourism-office/skills/knowledge-search/SKILL.md) | `transport_coordinator` | S15 | completed | `run_0b725bf68dcd4316859b909eb4269e38` |
| S17 | [management-handoff](chengdu-tourism-office/skills/management-handoff/SKILL.md) | `sales_manager` | S11, S12, S14, S16 | completed | `run_ab07d92a4cc14b84b5884e4920646e84` |
| S18 | [task-tracker](chengdu-tourism-office/skills/task-tracker/SKILL.md) | `product_manager` | S17 | completed | `run_a98ce13acec54b3681dee7a796f6ff45` |
| S19 | [pdf-create](chengdu-tourism-office/skills/pdf-create/SKILL.md) | `finance_manager` | S18, S16 | completed | `run_5065c8da97ce43b294d374948ca08b7f` |
| S20 | [task-tracker](chengdu-tourism-office/skills/task-tracker/SKILL.md) | `ops_manager` | S19 | completed | `run_6aa35c758022409d9fba0e063982e135` |

In the JSON, join `agent_run.steps[].run_id` to `runs[].id`. Inspect each run's `input`, `output` and `status`, then join artifact IDs with `artifacts[]`. The [timeline](submission/evidence/agent-timeline.json) preserves interim snapshots.

## Actual generated deliverables

- [SIMULATION Chengdu food-and-tea executive management handoff.docx](<submission/evidence/generated-files/SIMULATION Chengdu food-and-tea executive management handoff.docx>)
- [SIMULATION Chengdu food-and-tea launch options - decision brief.docx](<submission/evidence/generated-files/SIMULATION Chengdu food-and-tea launch options - decision brief.docx>)
- [SIMULATION Chengdu food-and-tea launch options.pptx](<submission/evidence/generated-files/SIMULATION Chengdu food-and-tea launch options.pptx>)
- [SIMULATION Chengdu Food-and-Tea Launch — Final Executive Report.pdf](<submission/evidence/generated-files/SIMULATION Chengdu Food-and-Tea Launch — Final Executive Report.pdf>)
- [SIMULATION Chengdu food-and-tea pilot — local draft only.md](<submission/evidence/generated-files/SIMULATION Chengdu food-and-tea pilot — local draft only.md>)
- [SIMULATION Chengdu launch budget CNY — assumptions not transactions.xlsx](<submission/evidence/generated-files/SIMULATION Chengdu launch budget CNY — assumptions not transactions.xlsx>)
- [SIMULATION Chengdu launch checklist — tabletop gate 2026-10-11, not real clearance.md](<submission/evidence/generated-files/SIMULATION Chengdu launch checklist — tabletop gate 2026-10-11, not real clearance.md>)
- [SIMULATION Chengdu pilot preparation and fictional outcome.xlsx](<submission/evidence/generated-files/SIMULATION Chengdu pilot preparation and fictional outcome.xlsx>)
- [SIMULATION Chengdu pilot — 40h assumed effort, no reservations responsibility matrix.xlsx](<submission/evidence/generated-files/SIMULATION Chengdu pilot — 40h assumed effort, no reservations responsibility matrix.xlsx>)
- [SIMULATION Oct-Dec 2026 retained 30-guest monthly-repeat scenario.xlsx](<submission/evidence/generated-files/SIMULATION Oct-Dec 2026 retained 30-guest monthly-repeat scenario.xlsx>)

The [demo script](submission/demo-script.md) describes both agent execution and the subsequent read-only tour. The organisation chart, people, library, approach, activity, files and settings tour adds no skill executions to these counts.
