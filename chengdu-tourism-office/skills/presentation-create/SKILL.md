---
name: presentation-create
description: Build an editable presentation with a cover and concise content slides.
---

# PowerPoint presentation

Use at most six concise points per slide. The renderer wraps text; split dense material into additional slides. Do not invent business metrics.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/presentation-create/scripts/run.py --input skills/presentation-create/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/presentation-create/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
