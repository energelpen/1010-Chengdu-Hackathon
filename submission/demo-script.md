# Atlas Office — agent-led implementation demo

Repository: https://github.com/energelpen/1010-Chengdu-Hackathon

One request triggers a real configured model, a model-authored plan and actual skill execution. The business launch is explicitly simulated. No skill forms or manual approval clicks are used in this recording. Waiting periods are compressed and synthetic English narration is added. The clean video has brief chapter titles and a small Simulation badge.

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

## 00:00:20 — The agent builds its plan

Atlas turns the request into a visible execution plan. Each step has an actual skill, an assigned colleague, and dependencies. The model reads the skill contracts before it uses them. The plan and progress come from the running agent, not a prewritten video sequence.

## 00:00:40 — Skills become action

The first results are arriving. Atlas supplies the skill inputs itself and delegates to colleagues whose profiles allow the work. Every call is recorded with its assignee, outcome, and elapsed time. Completed results become context for the next decision.

## 00:00:59 — Teams work through dependencies

The agent continues across the company. Planning, responsibilities, capacity and commercial decisions are handled through the same shared runtime. Dependent steps can proceed only after their prerequisites complete. There are no manual skill forms between these actions.

## 00:01:18 — From analysis to deliverables

The launch takes shape as business records and real files. Finance calculations, project work, launch risks and management outputs are linked to recorded skill runs. Simulation assumptions remain visible in the content, while the document and spreadsheet generation actually execute.

## 00:01:38 — The agent closes the loop

Atlas brings the completed work into the launch handoff and reusable company knowledge. The same request drives the workflow through its final outputs. The live dashboard keeps the completed work, remaining steps, generated files, and API usage visible.

## 00:01:56 — Measured execution

This run recorded 20 completed skill executions, covering 16 different skills and 7 colleagues. It produced 10 files. The dashboard also reports 24 model requests and 26 tool calls. These are measured results from this run, not projected productivity gains.

## 00:02:18 — Inspect the results

Every completed step links to its actual result. The activity record keeps the inputs and outputs, while the file library contains the generated launch pack. You can reopen the conversation later and inspect the same persisted execution record.

## 00:02:35 — One brief to a launch pack

Atlas Office makes agent work inspectable: one brief, a delegated plan, executable skills, and a finished set of business outputs. The GitHub repository includes the application, sixty-nine skill contracts, the API reference, and the evidence from this run. The business launch is simulated; the agent execution and generated deliverables are real.

## Reproduction and evidence

See `evidence/launch-execution.json`, `evidence/agent-timeline.json` and `evidence/generated-files/`. `record_agent_demo.py` starts an isolated app, passes the configured API key only through the server environment, submits one prompt and records the genuine UI. It needs an authorized API account, Playwright and Edge. `voice_full_demo.py --agent` generates narration; `assemble_agent_demo.py` edits the footage with FFmpeg. No keys or runtime databases enter the submission.

The run is evidence for this scenario, not a general reliability rate. It does not establish a real market launch, supplier verification, enterprise adoption or external delivery.