---
name: quotation-package
description: Build a general business quotation document and price schedule from supplied terms.
---

# Business quotation package

Collect the customer, currency, expiry, tax and discount rates, commercial terms, and priced line items. Never guess tax policy or supplier cost. Calculate each line, subtotal, discount, taxable base, tax and total with two-decimal currency rounding. Expired dates, empty lines and invalid prices stop with a clear error.

Produce a Word quotation and Excel price schedule, both explicitly drafts. The skill does not send a message, accept an order, book anything or post an invoice. If the user wants delivery, prepare a separate `gmail-send` run to the demo test inbox and wait for review.

Run `python skills/quotation-package/scripts/run.py --input skills/quotation-package/references/example.json` from the project root; the example demonstrates shape, not customer facts.
