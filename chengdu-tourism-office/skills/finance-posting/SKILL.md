---
name: finance-posting
description: Prepare a reviewed simulated booking commitment and customer invoice draft.
---

# Review booking finance and invoice draft

Precheck a `booking-confirm` record with `simulated_confirmed` status, the real Atlas monthly workbook file ID, an expense category on its BvA tab, and a positive committed cost no greater than the customer quote. Never post the simulation into Actuals or describe it as cash spent.

Submission pauses in Activity. A workspace operator reviews the exact booking, category and amount before approval. Approval writes a **new version** of the workbook: the customer quote increases Simulated pipeline on the income side; the supplier cost increases Simulated commitment on the outflow side. Actual income and expense remain unchanged. It also appends a Booking log row and creates an invoice workbook clearly labeled `DRAFT - NOT ISSUED`. The original workbook remains unchanged. The skill refuses duplicate finance postings for the same booking.

If the booking is missing, already posted, or the workbook structure is wrong, stop with a specific error. Customer communication requires a separately reviewed Gmail action to the test inbox.

Run `python skills/finance-posting/scripts/run.py --input skills/finance-posting/references/example.json` after replacing both example IDs with existing records. GUI, REST and MCP use the same runtime and approval gate.
