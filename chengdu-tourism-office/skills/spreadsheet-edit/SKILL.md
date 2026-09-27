---
name: spreadsheet-edit
description: Prepare a controlled one-cell edit to a local Excel workbook.
---

# Edit a reviewed Excel input

Find the real file ID and exact input cell with `spreadsheet-search`. Read the current value and confirm the requested replacement. Submit the file, sheet, cell and finite number or plain text. This skill pauses in Activity until a human approves it. It rejects formulas, unsafe formula-like text, nonexistent sheets, and large workbooks.

Approval creates a **new workbook copy**. The source file is untouched. Excel recalculates its formulas when the copy is opened. Report the saved before/after values and new file link. For simulated bookings use `finance-posting` instead, so commitments are not mislabeled as actual expenses.

Run `python skills/spreadsheet-edit/scripts/run.py --input skills/spreadsheet-edit/references/example.json` after replacing the example file ID. The CLI, GUI, REST and MCP entrypoints share the approval policy.
