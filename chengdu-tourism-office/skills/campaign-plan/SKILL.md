---
name: campaign-plan
description: Create a campaign brief with channels, budget and measurable objectives.
---

# Campaign plan

Label targets as planned. This does not publish a campaign or purchase advertising.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/campaign-plan/scripts/run.py --input skills/campaign-plan/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/campaign-plan/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
