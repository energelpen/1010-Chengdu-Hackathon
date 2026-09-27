---
name: inventory-reorder
description: Calculate reorder points and suggested quantities using demand, lead time and safety stock.
---

# Inventory reorder

Inventory position includes on-order stock. Recommended quantities are rounded up and never negative; no purchase is placed.

Read [input schema](references/input.schema.json) for exact fields and use the
[example](references/example.json) as a shape example, not factual company data.
Ask for missing required inputs instead of inventing them. Return the actual result,
artifact links and unresolved issues from the runner.

Run from the project root:

```console
python skills/inventory-reorder/scripts/run.py --input skills/inventory-reorder/references/example.json
```

The same implementation is available in the Skills GUI, `POST /api/skills/inventory-reorder/run`,
and the company MCP server's `run_skill` tool. Supporting implementation lives in
`scripts/business_tools.py`, `scripts/skill_runtime.py` and, for Google, `scripts/google_workspace.py`.
Remote writes return an immutable pending run. Review its inputs and use the GUI or
`POST /api/runs/{id}/approve` to execute. Local file creation runs immediately.
