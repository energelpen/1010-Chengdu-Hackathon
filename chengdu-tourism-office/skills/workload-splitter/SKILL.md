---
name: tourism-workload-splitter
description: Split a tourism RFQ into owned, dated tasks across sales, product, suppliers, operations, finance and management. Use after an option and hierarchy assignments are available.
---

# Workload Splitting Agent

Act as the project coordinator. Accept `inquiry`, selected `option`, and `hierarchy`. Produce an acyclic dependency graph with effort hours, due dates, owner IDs, approval gates and reporting routes. Supplier confirmation, safety clearance and finance approval precede a client draft. Quotes at or above CNY 100,000 add executive approval. Escalate unassigned or already overdue tasks. Do not report a quote as approved merely because a task exists.

```powershell
python scripts/run.py '@../../examples/workload.json'
```

Use the tasks as input to execution control. Run `python scripts/run_tests.py` for this skill's decision cases.
