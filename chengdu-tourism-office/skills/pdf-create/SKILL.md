---
name: pdf-create
description: Create a paginated, printable PDF brief from structured sections.
---

# PDF brief

Use short sections. The output uses a Unicode font when available; inspect documents with scripts unavailable in the installed font.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/pdf-create/scripts/run.py --input skills/pdf-create/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/pdf-create/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
