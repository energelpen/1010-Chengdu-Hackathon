---
name: tourism-hierarchy-router
description: Assign a task lead and specialist agents within a tourism-company reporting hierarchy using skills, availability and capacity. Use when an RFQ needs cross-department delegation.
---

# Hierarchy Routing Agent

Act as the coordination office. Read `people` from the [demo company model](../../resources/tourism-company.json), or accept a supplied roster with `id`, `reports_to`, `skills`, `capacity_hours`, `assigned_hours` and `available`. Choose each duty by skill and free capacity. Show the route from the RFQ lead up to the common manager and down to the assigned specialist. Return `escalated` if a duty has no capable agent; report cycles or broken reporting lines as invalid input. Formal ranks remain unchanged; the temporary task lead can differ by request.

```powershell
python scripts/run.py '{}'
```

Use `assignments` and `routes` in workload splitting and escalation. Run `python scripts/run_tests.py` for this skill's decision cases.
