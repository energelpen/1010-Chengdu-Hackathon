---
name: mcp-tool
description: Prepare an allowlisted tool call on a configured MCP server.
---

# Connected MCP tool

Discover the selected server first. Only tools explicitly allowlisted in the server configuration can run. Every call requires review because a remote tool's declared annotations do not prove that it is read-only.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/mcp-tool/scripts/run.py --input skills/mcp-tool/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/mcp-tool/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
