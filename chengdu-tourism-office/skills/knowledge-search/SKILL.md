---
name: knowledge-search
description: Search the local knowledge register and return matching source notes.
---

# Search company knowledge

Return matching passages with their stored source. An empty result means no local match, not that the policy does not exist.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/knowledge-search/scripts/run.py --input skills/knowledge-search/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/knowledge-search/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
