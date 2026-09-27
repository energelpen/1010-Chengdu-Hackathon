# Atlas Office narrated implementation demo

Repository: https://github.com/energelpen/1010-Chengdu-Hackathon

This is an edited recording of actual UI operations, with synthetic English narration. All business inputs and completion statements are simulation data. The operator invokes each skill; automatic one-sentence launch completion is not claimed.

The recording demonstrates 13 different skills, with a genuine approval transition for a reviewed spreadsheet change.

## 00:00:00 - 01 / One launch brief

This is Atlas Office, running locally with fictional colleagues. Our scenario is preparing the launch of a Chengdu food and tea group-tour product. We will follow the entire preparation cycle. In this credential-free recording, the operator invokes the actual skills and reviews their results. Free-form model orchestration is optional and is not shown here.

## 00:00:24 - 02 / Compare launch options

Wang, the sales lead, prepares two launch alternatives. We supply the costs, impact, risk, and weights explicitly. The executed proposal skill recommends the pilot, scoring seventy-five point seven against sixty-two for full launch. It creates an editable PowerPoint proposal and Word decision brief. The recorded result is a recommendation, not spending approval.

## 00:00:52 - 03 / Assign qualified colleagues

Operations now splits the launch work using real assigned skill identifiers and projected capacity. The result assigns planning, budget review, and management handoff to qualified colleagues. If no colleague has the required skill or hours, the same tool reports unassigned work for manager attention. These are proposed allocations; it does not secretly change saved staff capacity.

## 00:01:18 - 04 / Dependencies and accountability

Zhao, the product lead, converts the launch preparation into a dependency-aware schedule. The pilot review follows scope confirmation, and the executive decision follows the review. Finish dates are exclusive calendar-day boundaries. A separate responsibility matrix names the responsible specialists and makes Chen accountable for the final decision.

## 00:01:42 - 05 / Track a blocker through resolution

We record a launch task as blocked, with Operations as its owner. The manager can inspect and edit that saved record. For this simulation, we enter a supplied readiness outcome and mark the task done. This is an operator-recorded status transition, not automatic verification of a real supplier. The record remains available in the company register.

## 00:02:07 - 06 / Budget evidence and a real review gate

Deng, the finance lead, calculates budget variance from supplied simulation figures. Marketing is fifteen hundred renminbi over budget. We then create a real Excel launch budget and propose a revised input value. Spreadsheet editing stops at awaiting approval. Only after review and the approval click does Atlas create a new workbook copy, preserving the original.

## 00:02:34 - 07 / Management decision and completed handoff

Chen records the simulated decision to proceed with pilot preparation, with the weighted comparison and reviewed budget as its rationale. The final handoff reports three preparation tasks done from supplied simulation evidence and produces a management Word brief plus an unsent email draft. The preparation loop is complete; launching a real travel product still requires authorized enterprise checks.

## 00:03:00 - 08 / Deliver documents and retain knowledge

The launch pack can be delivered as a PDF as well as Word, PowerPoint, and Excel. We save the outcome as a sourced local knowledge note, then find it with a real search. This preserves the decision and its limits for the next request. Files remain downloadable from the workspace, and the email draft remains unsent.

## 00:03:22 - 09 / Inspect the execution record

Activity shows the actual runs across Sales, Product, Operations, Finance, IT and the Director. Thirteen different skills are demonstrated. The repository contains the source, all sixty-nine skill contracts, test evidence, and this submission. The nine-stage tourism engine is an additional domain workflow. This recording demonstrates the complete operator-led launch preparation cycle, including a real approval gate and simulated completion.

## Reproduction and evidence

See `evidence/launch-execution.json` for actual run records and `evidence/generated-files/` for outputs. The source recorder uses an isolated copy and new data directory, without credentials. `record_full_demo.py` records the UI, `voice_full_demo.py` renders narration using Windows SAPI, and `assemble_full_demo.py` synchronizes chapters. Browser automation requires Playwright and Edge; encoding requires FFmpeg. Paths are configured at the start of these scripts.

The automatic full single-sentence launch lifecycle, live provider integrations, employee identity and real enterprise validation remain outside the demonstrated scope.