---
name: gmail-draft
description: Create an unsent message in Gmail after reviewing its contents.
---

# Create Gmail draft

Use the connected Google account. Surface provider errors and actual IDs. Review the exact saved payload before executing this external write; do not retry an uncertain result automatically.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/gmail-draft/scripts/run.py --input skills/gmail-draft/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/gmail-draft/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
