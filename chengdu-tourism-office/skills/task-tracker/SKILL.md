---
name: task-tracker
description: Save an owned task with status and due date to the local work register.
---

# Task tracker

Keep the owner and current status explicit. Saved records can be edited through the work register API or UI.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/task-tracker/scripts/run.py --input skills/task-tracker/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/task-tracker/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
