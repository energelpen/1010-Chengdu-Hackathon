---
name: spreadsheet-search
description: Find exact cells in a workspace Excel workbook before changing financial or operational data.
---

# Search an Excel workbook

Use a real file ID from Files. Search all worksheets case-insensitively and return sheet, cell and matched value. The reader rejects non-XLSX and oversized workbooks, and limits output to 100 matches. If no match exists, ask for another term; do not invent a cell address.

Run `python skills/spreadsheet-search/scripts/run.py --input skills/spreadsheet-search/references/example.json` after replacing the example file ID. The same handler is available in the app and MCP skills interface. The example is a shape guide, not a valid file ID.

The next step for a requested change is `spreadsheet-edit` or `finance-posting`, both of which require human review and write a new workbook copy.
