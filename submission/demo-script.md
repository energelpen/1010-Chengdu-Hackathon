# Atlas Office — agent-led implementation demo

Repository: https://github.com/energelpen/1010-Chengdu-Hackathon

One request triggers a real configured model, a model-authored plan and actual skill execution. The business launch is explicitly simulated. The additional product tour inspects the organisation, people, skill contracts, proposal, activity, files, knowledge, settings, connections and API in a copy of the completed workspace. It does not submit skills or approval decisions. Waiting periods are compressed and synthetic English narration is added. The clean video has brief chapter titles and a small Simulation badge.

## Measured run

```json
{
  "model_requests": 24,
  "tool_calls": 26,
  "skills_executed": 20,
  "skills_completed": 20,
  "skills_failed": 0,
  "skills_pending": 0,
  "distinct_skills": 16,
  "delegated_people": 7,
  "artifacts": 10,
  "input_tokens": 786654,
  "output_tokens": 14141,
  "total_tokens": 800795,
  "elapsed_ms": 303797
}
```

## 00:00:00 — One request. A whole team.

Meet Atlas Office. One request brings the team together to prepare a Chengdu food and tea product launch. This is a business simulation using a real model connection and executable local skills. Atlas chooses the work, assigns colleagues, runs the tools, and creates the deliverables.

## 00:00:20 — An organisation the agent can use

The organisation chart connects roles, reporting lines and capacity. Select a colleague to inspect their manager, available hours and assigned skills: the company context Atlas uses when delegating work.

## 00:00:35 — People with defined capabilities

The people directory makes each role inspectable. Search Finance to see Deng’s workload, reporting line and executable skills, all attached to the same fictional colleague used in the launch.

## 00:00:49 — Explore all 69 skills

The library contains sixty-nine executable skills. Filter by function, search for a capability, and inspect its instructions. These are the same skill contracts the agent reads and calls during the launch.

## 00:01:04 — The agent builds its plan

Atlas turns the request into a visible execution plan. Each step has an actual skill, an assigned colleague, and dependencies. The model reads the skill contracts before it uses them. The plan and progress come from the running agent, not a prewritten video sequence.

## 00:01:24 — Skills become action

The first results are arriving. Atlas supplies the skill inputs itself and delegates to colleagues whose profiles allow the work. Every call is recorded with its assignee, outcome, and elapsed time. Completed results become context for the next decision.

## 00:01:43 — Teams work through dependencies

The agent continues across the company. Planning, responsibilities, capacity and commercial decisions are handled through the same shared runtime. Dependent steps can proceed only after their prerequisites complete. There are no manual skill forms between these actions.

## 00:02:02 — From analysis to deliverables

The launch takes shape as business records and real files. Finance calculations, project work, launch risks and management outputs are linked to recorded skill runs. Simulation assumptions remain visible in the content, while the document and spreadsheet generation actually execute.

## 00:02:22 — The agent closes the loop

Atlas brings the completed work into the launch handoff and reusable company knowledge. The same request drives the workflow through its final outputs. The live dashboard keeps the completed work, remaining steps, generated files, and API usage visible.

## 00:02:40 — Measured execution

This run recorded 20 completed skill executions, covering 16 different skills and 7 colleagues. It produced 10 files. The dashboard also reports 24 model requests and 26 tool calls. These are measured results from this run, not projected productivity gains.

## 00:03:01 — Inspect the results

Every completed step links to its actual result. The activity record keeps the inputs and outputs, while the file library contains the generated launch pack. You can reopen the conversation later and inspect the same persisted execution record.

## 00:03:19 — Review the chosen approach

Open the recorded proposal to examine the approach: a fifty-thousand-renminbi pilot versus a hundred-and-twenty-thousand full launch. The actual result includes the recommendation, weighted scores and editable proposal files.

## 00:03:35 — Activity and approval visibility

Activity brings together all twenty recorded runs and their company records. Each result retains its inputs, output and assigned colleague. The review counter clearly distinguishes pending actions from completed work.

## 00:03:50 — Files and reusable knowledge

The file library gathers the launch pack in one place. Search company knowledge to retrieve the saved launch note, carrying the decision, assumptions and evidence forward into future work.

## 00:04:03 — Controls, connections and API

Settings expose tourism proposal modes and delivery permissions. Connections lists optional Google, Telegram and MCP services with their actual status. The API reference documents the same skills for integration.

## 00:04:20 — One brief to a launch pack

Atlas Office makes agent work inspectable: one brief, a delegated plan, executable skills, and a finished set of business outputs. The GitHub repository includes the application, sixty-nine skill contracts, the API reference, and the evidence from this run. The business launch is simulated; the agent execution and generated deliverables are real.

## Reproduction and evidence

See `evidence/launch-execution.json`, `evidence/agent-timeline.json` and `evidence/generated-files/`. `record_agent_demo.py` starts an isolated app, passes the configured API key only through the server environment, submits one prompt and records the genuine UI. It needs an authorized API account, Playwright and Edge. `record_workspace_tour.py` copies that saved state, blocks browser mutation requests and verifies the runs, records and files are unchanged. `voice_full_demo.py --agent` and `--tour` generate narration; `assemble_agent_demo.py --with-tour` edits both recordings with FFmpeg. No keys or runtime databases enter the submission.

The run is evidence for this scenario, not a general reliability rate. It does not establish a real market launch, supplier verification, enterprise adoption or external delivery.