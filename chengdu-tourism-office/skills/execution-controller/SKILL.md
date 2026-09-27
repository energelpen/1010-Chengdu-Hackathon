---
name: tourism-execution-controller
description: Apply task dependencies, owner checks, supplier and safety evidence, finance approval and incident escalation to a tourism quotation workflow. Use during RFQ execution.
---

# Execution Control Agent

Act as the control desk. Accept `tasks` and ordered `events`. A completion event needs the assigned `actor_id`, `action: complete`, a nonempty `evidence_ref`, fulfilled dependencies and the task's required gate flag (`supplier_confirmed`, `safety_cleared` or `approved`). Reject and explain invalid events. Incident events travel back through the task's reporting route and hold the customer response. Output ready tasks, blocked tasks, accepted evidence and escalations.

```powershell
python scripts/run.py '@../../examples/execution.json'
```

Only pass accepted evidence to the outcome reporter. Run `python scripts/run_tests.py` for this skill's decision cases.
