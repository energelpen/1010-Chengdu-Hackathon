---
name: finance-forecast
description: Build a transparent monthly operating forecast for any customer-based company.
---

# Monthly finance forecast

Require starting customers and, for each dated month, additions, churn, revenue per average billable customer, variable cost per average billable customer, and fixed cost. Reject duplicate/out-of-order months and churn greater than available customers. Calculate closing customers, average billable customers assuming uniform timing, revenue, variable and fixed cost, total expense and operating profit. Keep the assumption explicit; do not present forecast as booked revenue or actual cash.

Return a month-by-month JSON trace and downloadable Excel schedule. Ask for missing drivers rather than inventing growth or FX rates. Validate totals against the sum of monthly rows.

Run `python skills/finance-forecast/scripts/run.py --input skills/finance-forecast/references/example.json` from the project root. The example contains fictional numbers.
