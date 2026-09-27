---
name: crm-pipeline
description: Calculate weighted pipeline value and summarize opportunities by stage.
---

# Sales pipeline

Keep currencies separate. Weighted value is a scenario calculation, not booked revenue or a forecast guarantee.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/crm-pipeline/scripts/run.py --input skills/crm-pipeline/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/crm-pipeline/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
