---
name: shareholder-report
description: Create a draft shareholder report and slides from supplied financial results.
---

# Shareholder report package

Gather a defined reporting period and currency; current and comparable prior revenue; cost of sales, operating expenses, opening and ending cash; and supplied highlights, risks and management actions. Check that periods and accounting basis match before running. Compute revenue growth, gross profit and margin, operating profit and cash change. Prior revenue of zero yields unavailable growth; revenue of zero yields unavailable margin. Do not fabricate audited status, projections or causal explanations.

Create a Word report and PowerPoint update marked draft, unaudited and unsent. If figures are missing, request them. A human must review before any shareholder distribution.

Run `python skills/shareholder-report/scripts/run.py --input skills/shareholder-report/references/example.json` from the project root. The example is fictional and cannot be reused as company evidence.
