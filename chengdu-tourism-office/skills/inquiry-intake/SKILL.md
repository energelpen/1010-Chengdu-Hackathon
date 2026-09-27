---
name: tourism-inquiry-intake
description: Turn a tourism customer inquiry or RFQ into a validated brief with group size, dates, budget, interests and source provenance. Use first when a new travel request arrives.
---

# Inquiry Intake Agent

Act as the sales desk. Extract only values present in the customer's message or structured fields; do not fill missing constraints with guesses. Accept `message`, `type` (`rfq` or `inquiry`), optional `group_size`, `duration_days`, `budget_cny`, `travel_start`, `origin_airport`, `customer_name` and `customer_email`. Return `needs_input` for invalid dates, amounts, group size or email. Preserve which values were supplied and which were parsed.

```powershell
python scripts/run.py '@../../examples/rfq.json'
```

Pass the normalized `data` to flight and tour research. Run `python scripts/run_tests.py` for this skill's decision cases.
