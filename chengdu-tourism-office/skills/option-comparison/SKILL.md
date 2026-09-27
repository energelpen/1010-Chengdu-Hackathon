---
name: tourism-option-comparison
description: Rank complete group-tour quotation options using land, transport, flight and activity estimates. Use after intake and offer search, before delegating the chosen proposal.
---

# Quotation Comparison Agent

Act as the commercial analyst. Accept `inquiry`, optional selected `flight`, optional `activities`, and `priority` (`balanced`, `price` or `experience`). Calculate a complete quote and show each cost component and score component. Reject options above budget, capacity or lead-time limits. Keep the estimate `indicative`: supplier inventory and flight fares are not confirmed by this comparison.

```powershell
python scripts/run.py '@../../examples/compare.json'
```

Send the selected option to workload splitting and schedule building. Run `python scripts/run_tests.py` for this skill's decision cases.
