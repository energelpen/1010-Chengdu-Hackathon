# Original Agent Skill index

**Team Atlas — Singapore Polytechnic**

All 69 original skill instruction files are linked below. The additional [top-level SKILL.md](chengdu-tourism-office/SKILL.md) describes the nine-stage tourism workflow. The manifests are executable contracts; SKILL.md provides instructions read by the agent.

| Category | Skills |
|---|---:|
| Communication | 4 |
| Customer success | 1 |
| Data | 1 |
| Finance | 6 |
| Google Workspace | 14 |
| Governance | 7 |
| Integrations | 1 |
| Knowledge | 2 |
| Marketing | 1 |
| Office files | 8 |
| Operations | 8 |
| People | 3 |
| Sales | 3 |
| Tourism template | 10 |

Effects: `local` runs locally; `remote_read` needs a connected service; `remote_write` and `reviewed_write` require review before execution. The Tourism template category contains ten skills: nine stages and the booking-confirm simulation skill. The Recorded column counts skill executions in the preserved launch demo, not general coverage.

## Communication

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Calendar invitation (`calendar-event`) | [SKILL.md](chengdu-tourism-office/skills/calendar-event/SKILL.md) | [skill.json](chengdu-tourism-office/skills/calendar-event/skill.json) | [run.py](chengdu-tourism-office/skills/calendar-event/scripts/run.py) | `local` | 0 |
| Email draft (`email-draft`) | [SKILL.md](chengdu-tourism-office/skills/email-draft/SKILL.md) | [skill.json](chengdu-tourism-office/skills/email-draft/skill.json) | [run.py](chengdu-tourism-office/skills/email-draft/scripts/run.py) | `local` | 0 |
| Meeting minutes (`meeting-minutes`) | [SKILL.md](chengdu-tourism-office/skills/meeting-minutes/SKILL.md) | [skill.json](chengdu-tourism-office/skills/meeting-minutes/skill.json) | [run.py](chengdu-tourism-office/skills/meeting-minutes/scripts/run.py) | `local` | 0 |
| Notify boss on Telegram (`telegram-boss-update`) | [SKILL.md](chengdu-tourism-office/skills/telegram-boss-update/SKILL.md) | [skill.json](chengdu-tourism-office/skills/telegram-boss-update/skill.json) | [run.py](chengdu-tourism-office/skills/telegram-boss-update/scripts/run.py) | `remote_write` | 0 |
## Customer success

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Support triage (`support-triage`) | [SKILL.md](chengdu-tourism-office/skills/support-triage/SKILL.md) | [skill.json](chengdu-tourism-office/skills/support-triage/skill.json) | [run.py](chengdu-tourism-office/skills/support-triage/scripts/run.py) | `local` | 0 |
## Data

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Clean tabular data (`csv-clean`) | [SKILL.md](chengdu-tourism-office/skills/csv-clean/SKILL.md) | [skill.json](chengdu-tourism-office/skills/csv-clean/skill.json) | [run.py](chengdu-tourism-office/skills/csv-clean/scripts/run.py) | `local` | 0 |
## Finance

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Budget variance (`budget-variance`) | [SKILL.md](chengdu-tourism-office/skills/budget-variance/SKILL.md) | [skill.json](chengdu-tourism-office/skills/budget-variance/skill.json) | [run.py](chengdu-tourism-office/skills/budget-variance/scripts/run.py) | `local` | 1 |
| Expense report (`expense-report`) | [SKILL.md](chengdu-tourism-office/skills/expense-report/SKILL.md) | [skill.json](chengdu-tourism-office/skills/expense-report/skill.json) | [run.py](chengdu-tourism-office/skills/expense-report/scripts/run.py) | `local` | 0 |
| Monthly finance forecast (`finance-forecast`) | [SKILL.md](chengdu-tourism-office/skills/finance-forecast/SKILL.md) | [skill.json](chengdu-tourism-office/skills/finance-forecast/skill.json) | [run.py](chengdu-tourism-office/skills/finance-forecast/scripts/run.py) | `local` | 1 |
| Review booking finance and invoice draft (`finance-posting`) | [SKILL.md](chengdu-tourism-office/skills/finance-posting/SKILL.md) | [skill.json](chengdu-tourism-office/skills/finance-posting/skill.json) | [run.py](chengdu-tourism-office/skills/finance-posting/scripts/run.py) | `reviewed_write` | 0 |
| Invoice draft (`invoice-create`) | [SKILL.md](chengdu-tourism-office/skills/invoice-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/invoice-create/skill.json) | [run.py](chengdu-tourism-office/skills/invoice-create/scripts/run.py) | `local` | 0 |
| Shareholder report package (`shareholder-report`) | [SKILL.md](chengdu-tourism-office/skills/shareholder-report/SKILL.md) | [skill.json](chengdu-tourism-office/skills/shareholder-report/skill.json) | [run.py](chengdu-tourism-office/skills/shareholder-report/scripts/run.py) | `local` | 0 |
## Google Workspace

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Create Google Calendar event (`calendar-create`) | [SKILL.md](chengdu-tourism-office/skills/calendar-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/calendar-create/skill.json) | [run.py](chengdu-tourism-office/skills/calendar-create/scripts/run.py) | `remote_write` | 0 |
| Send test calendar invitation (`calendar-invite`) | [SKILL.md](chengdu-tourism-office/skills/calendar-invite/SKILL.md) | [skill.json](chengdu-tourism-office/skills/calendar-invite/skill.json) | [run.py](chengdu-tourism-office/skills/calendar-invite/scripts/run.py) | `remote_write` | 0 |
| Read Google Calendar (`calendar-list`) | [SKILL.md](chengdu-tourism-office/skills/calendar-list/SKILL.md) | [skill.json](chengdu-tourism-office/skills/calendar-list/skill.json) | [run.py](chengdu-tourism-office/skills/calendar-list/scripts/run.py) | `remote_read` | 0 |
| Create Google document (`docs-create`) | [SKILL.md](chengdu-tourism-office/skills/docs-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/docs-create/skill.json) | [run.py](chengdu-tourism-office/skills/docs-create/scripts/run.py) | `remote_write` | 0 |
| Read Google Docs (`docs-read`) | [SKILL.md](chengdu-tourism-office/skills/docs-read/SKILL.md) | [skill.json](chengdu-tourism-office/skills/docs-read/skill.json) | [run.py](chengdu-tourism-office/skills/docs-read/scripts/run.py) | `remote_read` | 0 |
| Search Google Drive (`drive-search`) | [SKILL.md](chengdu-tourism-office/skills/drive-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/drive-search/skill.json) | [run.py](chengdu-tourism-office/skills/drive-search/scripts/run.py) | `remote_read` | 0 |
| Upload to Google Drive (`drive-upload`) | [SKILL.md](chengdu-tourism-office/skills/drive-upload/SKILL.md) | [skill.json](chengdu-tourism-office/skills/drive-upload/skill.json) | [run.py](chengdu-tourism-office/skills/drive-upload/scripts/run.py) | `remote_write` | 0 |
| Create Gmail draft (`gmail-draft`) | [SKILL.md](chengdu-tourism-office/skills/gmail-draft/SKILL.md) | [skill.json](chengdu-tourism-office/skills/gmail-draft/skill.json) | [run.py](chengdu-tourism-office/skills/gmail-draft/scripts/run.py) | `remote_write` | 0 |
| Search Gmail (`gmail-search`) | [SKILL.md](chengdu-tourism-office/skills/gmail-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/gmail-search/skill.json) | [run.py](chengdu-tourism-office/skills/gmail-search/scripts/run.py) | `remote_read` | 0 |
| Send Gmail message (`gmail-send`) | [SKILL.md](chengdu-tourism-office/skills/gmail-send/SKILL.md) | [skill.json](chengdu-tourism-office/skills/gmail-send/skill.json) | [run.py](chengdu-tourism-office/skills/gmail-send/scripts/run.py) | `remote_write` | 0 |
| Create Google spreadsheet (`sheets-create`) | [SKILL.md](chengdu-tourism-office/skills/sheets-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/sheets-create/skill.json) | [run.py](chengdu-tourism-office/skills/sheets-create/scripts/run.py) | `remote_write` | 0 |
| Read Google Sheets (`sheets-read`) | [SKILL.md](chengdu-tourism-office/skills/sheets-read/SKILL.md) | [skill.json](chengdu-tourism-office/skills/sheets-read/skill.json) | [run.py](chengdu-tourism-office/skills/sheets-read/scripts/run.py) | `remote_read` | 0 |
| Write Google Sheets (`sheets-write`) | [SKILL.md](chengdu-tourism-office/skills/sheets-write/SKILL.md) | [skill.json](chengdu-tourism-office/skills/sheets-write/skill.json) | [run.py](chengdu-tourism-office/skills/sheets-write/scripts/run.py) | `remote_write` | 0 |
| Create Google Slides (`slides-create`) | [SKILL.md](chengdu-tourism-office/skills/slides-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/slides-create/skill.json) | [run.py](chengdu-tourism-office/skills/slides-create/scripts/run.py) | `remote_write` | 0 |
## Governance

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Contract review checklist (`contract-checklist`) | [SKILL.md](chengdu-tourism-office/skills/contract-checklist/SKILL.md) | [skill.json](chengdu-tourism-office/skills/contract-checklist/skill.json) | [run.py](chengdu-tourism-office/skills/contract-checklist/scripts/run.py) | `local` | 0 |
| Decision log (`decision-log`) | [SKILL.md](chengdu-tourism-office/skills/decision-log/SKILL.md) | [skill.json](chengdu-tourism-office/skills/decision-log/skill.json) | [run.py](chengdu-tourism-office/skills/decision-log/scripts/run.py) | `local` | 2 |
| Management handoff (`management-handoff`) | [SKILL.md](chengdu-tourism-office/skills/management-handoff/SKILL.md) | [skill.json](chengdu-tourism-office/skills/management-handoff/skill.json) | [run.py](chengdu-tourism-office/skills/management-handoff/scripts/run.py) | `local` | 1 |
| Policy checklist (`policy-checklist`) | [SKILL.md](chengdu-tourism-office/skills/policy-checklist/SKILL.md) | [skill.json](chengdu-tourism-office/skills/policy-checklist/skill.json) | [run.py](chengdu-tourism-office/skills/policy-checklist/scripts/run.py) | `local` | 1 |
| Option proposal and slides (`proposal-package`) | [SKILL.md](chengdu-tourism-office/skills/proposal-package/SKILL.md) | [skill.json](chengdu-tourism-office/skills/proposal-package/skill.json) | [run.py](chengdu-tourism-office/skills/proposal-package/scripts/run.py) | `local` | 1 |
| Risk register (`risk-register`) | [SKILL.md](chengdu-tourism-office/skills/risk-register/SKILL.md) | [skill.json](chengdu-tourism-office/skills/risk-register/skill.json) | [run.py](chengdu-tourism-office/skills/risk-register/scripts/run.py) | `local` | 1 |
| Scenario comparison (`scenario-compare`) | [SKILL.md](chengdu-tourism-office/skills/scenario-compare/SKILL.md) | [skill.json](chengdu-tourism-office/skills/scenario-compare/skill.json) | [run.py](chengdu-tourism-office/skills/scenario-compare/scripts/run.py) | `local` | 0 |
## Integrations

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Connected MCP tool (`mcp-tool`) | [SKILL.md](chengdu-tourism-office/skills/mcp-tool/SKILL.md) | [skill.json](chengdu-tourism-office/skills/mcp-tool/skill.json) | [run.py](chengdu-tourism-office/skills/mcp-tool/scripts/run.py) | `remote_write` | 0 |
## Knowledge

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Save company knowledge (`knowledge-save`) | [SKILL.md](chengdu-tourism-office/skills/knowledge-save/SKILL.md) | [skill.json](chengdu-tourism-office/skills/knowledge-save/skill.json) | [run.py](chengdu-tourism-office/skills/knowledge-save/scripts/run.py) | `local` | 1 |
| Search company knowledge (`knowledge-search`) | [SKILL.md](chengdu-tourism-office/skills/knowledge-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/knowledge-search/skill.json) | [run.py](chengdu-tourism-office/skills/knowledge-search/scripts/run.py) | `local` | 1 |
## Marketing

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Campaign plan (`campaign-plan`) | [SKILL.md](chengdu-tourism-office/skills/campaign-plan/SKILL.md) | [skill.json](chengdu-tourism-office/skills/campaign-plan/skill.json) | [run.py](chengdu-tourism-office/skills/campaign-plan/scripts/run.py) | `local` | 1 |
## Office files

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Word document (`document-create`) | [SKILL.md](chengdu-tourism-office/skills/document-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/document-create/skill.json) | [run.py](chengdu-tourism-office/skills/document-create/scripts/run.py) | `local` | 0 |
| PDF brief (`pdf-create`) | [SKILL.md](chengdu-tourism-office/skills/pdf-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/pdf-create/skill.json) | [run.py](chengdu-tourism-office/skills/pdf-create/scripts/run.py) | `local` | 1 |
| Read a PDF (`pdf-extract`) | [SKILL.md](chengdu-tourism-office/skills/pdf-extract/SKILL.md) | [skill.json](chengdu-tourism-office/skills/pdf-extract/skill.json) | [run.py](chengdu-tourism-office/skills/pdf-extract/scripts/run.py) | `local` | 0 |
| PowerPoint presentation (`presentation-create`) | [SKILL.md](chengdu-tourism-office/skills/presentation-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/presentation-create/skill.json) | [run.py](chengdu-tourism-office/skills/presentation-create/scripts/run.py) | `local` | 0 |
| Analyze a spreadsheet (`spreadsheet-analyze`) | [SKILL.md](chengdu-tourism-office/skills/spreadsheet-analyze/SKILL.md) | [skill.json](chengdu-tourism-office/skills/spreadsheet-analyze/skill.json) | [run.py](chengdu-tourism-office/skills/spreadsheet-analyze/scripts/run.py) | `local` | 0 |
| Excel workbook (`spreadsheet-create`) | [SKILL.md](chengdu-tourism-office/skills/spreadsheet-create/SKILL.md) | [skill.json](chengdu-tourism-office/skills/spreadsheet-create/skill.json) | [run.py](chengdu-tourism-office/skills/spreadsheet-create/scripts/run.py) | `local` | 1 |
| Edit a reviewed Excel input (`spreadsheet-edit`) | [SKILL.md](chengdu-tourism-office/skills/spreadsheet-edit/SKILL.md) | [skill.json](chengdu-tourism-office/skills/spreadsheet-edit/skill.json) | [run.py](chengdu-tourism-office/skills/spreadsheet-edit/scripts/run.py) | `reviewed_write` | 0 |
| Search an Excel workbook (`spreadsheet-search`) | [SKILL.md](chengdu-tourism-office/skills/spreadsheet-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/spreadsheet-search/skill.json) | [run.py](chengdu-tourism-office/skills/spreadsheet-search/scripts/run.py) | `local` | 0 |
## Operations

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Incident report (`incident-report`) | [SKILL.md](chengdu-tourism-office/skills/incident-report/SKILL.md) | [skill.json](chengdu-tourism-office/skills/incident-report/skill.json) | [run.py](chengdu-tourism-office/skills/incident-report/scripts/run.py) | `local` | 0 |
| Inventory reorder (`inventory-reorder`) | [SKILL.md](chengdu-tourism-office/skills/inventory-reorder/SKILL.md) | [skill.json](chengdu-tourism-office/skills/inventory-reorder/skill.json) | [run.py](chengdu-tourism-office/skills/inventory-reorder/scripts/run.py) | `local` | 0 |
| Supplier comparison (`procurement-compare`) | [SKILL.md](chengdu-tourism-office/skills/procurement-compare/SKILL.md) | [skill.json](chengdu-tourism-office/skills/procurement-compare/skill.json) | [run.py](chengdu-tourism-office/skills/procurement-compare/scripts/run.py) | `local` | 0 |
| Project plan (`project-plan`) | [SKILL.md](chengdu-tourism-office/skills/project-plan/SKILL.md) | [skill.json](chengdu-tourism-office/skills/project-plan/skill.json) | [run.py](chengdu-tourism-office/skills/project-plan/scripts/run.py) | `local` | 1 |
| Responsibility matrix (`responsibility-matrix`) | [SKILL.md](chengdu-tourism-office/skills/responsibility-matrix/SKILL.md) | [skill.json](chengdu-tourism-office/skills/responsibility-matrix/skill.json) | [run.py](chengdu-tourism-office/skills/responsibility-matrix/scripts/run.py) | `local` | 1 |
| Task tracker (`task-tracker`) | [SKILL.md](chengdu-tourism-office/skills/task-tracker/SKILL.md) | [skill.json](chengdu-tourism-office/skills/task-tracker/skill.json) | [run.py](chengdu-tourism-office/skills/task-tracker/scripts/run.py) | `local` | 4 |
| Team capacity (`team-capacity`) | [SKILL.md](chengdu-tourism-office/skills/team-capacity/SKILL.md) | [skill.json](chengdu-tourism-office/skills/team-capacity/skill.json) | [run.py](chengdu-tourism-office/skills/team-capacity/scripts/run.py) | `local` | 1 |
| Workload rebalance (`workload-rebalance`) | [SKILL.md](chengdu-tourism-office/skills/workload-rebalance/SKILL.md) | [skill.json](chengdu-tourism-office/skills/workload-rebalance/skill.json) | [run.py](chengdu-tourism-office/skills/workload-rebalance/scripts/run.py) | `local` | 0 |
## People

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Interview scorecard (`hiring-scorecard`) | [SKILL.md](chengdu-tourism-office/skills/hiring-scorecard/SKILL.md) | [skill.json](chengdu-tourism-office/skills/hiring-scorecard/skill.json) | [run.py](chengdu-tourism-office/skills/hiring-scorecard/scripts/run.py) | `local` | 0 |
| Employee onboarding (`hr-onboarding`) | [SKILL.md](chengdu-tourism-office/skills/hr-onboarding/SKILL.md) | [skill.json](chengdu-tourism-office/skills/hr-onboarding/skill.json) | [run.py](chengdu-tourism-office/skills/hr-onboarding/scripts/run.py) | `local` | 0 |
| Leave request (`leave-request`) | [SKILL.md](chengdu-tourism-office/skills/leave-request/SKILL.md) | [skill.json](chengdu-tourism-office/skills/leave-request/skill.json) | [run.py](chengdu-tourism-office/skills/leave-request/scripts/run.py) | `local` | 0 |
## Sales

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Sales pipeline (`crm-pipeline`) | [SKILL.md](chengdu-tourism-office/skills/crm-pipeline/SKILL.md) | [skill.json](chengdu-tourism-office/skills/crm-pipeline/skill.json) | [run.py](chengdu-tourism-office/skills/crm-pipeline/scripts/run.py) | `local` | 0 |
| Customer follow-up register (`customer-followup`) | [SKILL.md](chengdu-tourism-office/skills/customer-followup/SKILL.md) | [skill.json](chengdu-tourism-office/skills/customer-followup/skill.json) | [run.py](chengdu-tourism-office/skills/customer-followup/scripts/run.py) | `local` | 0 |
| Business quotation package (`quotation-package`) | [SKILL.md](chengdu-tourism-office/skills/quotation-package/SKILL.md) | [skill.json](chengdu-tourism-office/skills/quotation-package/skill.json) | [run.py](chengdu-tourism-office/skills/quotation-package/scripts/run.py) | `local` | 0 |
## Tourism template

| Skill | Original instructions | Manifest | Runner | Effect | Recorded |
|---|---|---|---|---|---:|
| Simulate booking confirmation (`booking-confirm`) | [SKILL.md](chengdu-tourism-office/skills/booking-confirm/SKILL.md) | [skill.json](chengdu-tourism-office/skills/booking-confirm/skill.json) | [run.py](chengdu-tourism-office/skills/booking-confirm/scripts/run.py) | `local` | 0 |
| Execution Controller (`execution-controller`) | [SKILL.md](chengdu-tourism-office/skills/execution-controller/SKILL.md) | [skill.json](chengdu-tourism-office/skills/execution-controller/skill.json) | [run.py](chengdu-tourism-office/skills/execution-controller/scripts/run.py) | `local` | 0 |
| Flight Search (`flight-search`) | [SKILL.md](chengdu-tourism-office/skills/flight-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/flight-search/skill.json) | [run.py](chengdu-tourism-office/skills/flight-search/scripts/run.py) | `local` | 0 |
| Hierarchy Router (`hierarchy-router`) | [SKILL.md](chengdu-tourism-office/skills/hierarchy-router/SKILL.md) | [skill.json](chengdu-tourism-office/skills/hierarchy-router/skill.json) | [run.py](chengdu-tourism-office/skills/hierarchy-router/scripts/run.py) | `local` | 0 |
| Inquiry Intake (`inquiry-intake`) | [SKILL.md](chengdu-tourism-office/skills/inquiry-intake/SKILL.md) | [skill.json](chengdu-tourism-office/skills/inquiry-intake/skill.json) | [run.py](chengdu-tourism-office/skills/inquiry-intake/scripts/run.py) | `local` | 0 |
| Option Comparison (`option-comparison`) | [SKILL.md](chengdu-tourism-office/skills/option-comparison/SKILL.md) | [skill.json](chengdu-tourism-office/skills/option-comparison/skill.json) | [run.py](chengdu-tourism-office/skills/option-comparison/scripts/run.py) | `local` | 0 |
| Outcome Reporter (`outcome-reporter`) | [SKILL.md](chengdu-tourism-office/skills/outcome-reporter/SKILL.md) | [skill.json](chengdu-tourism-office/skills/outcome-reporter/skill.json) | [run.py](chengdu-tourism-office/skills/outcome-reporter/scripts/run.py) | `local` | 0 |
| Schedule Builder (`schedule-builder`) | [SKILL.md](chengdu-tourism-office/skills/schedule-builder/SKILL.md) | [skill.json](chengdu-tourism-office/skills/schedule-builder/skill.json) | [run.py](chengdu-tourism-office/skills/schedule-builder/scripts/run.py) | `local` | 0 |
| Tour Search (`tour-search`) | [SKILL.md](chengdu-tourism-office/skills/tour-search/SKILL.md) | [skill.json](chengdu-tourism-office/skills/tour-search/skill.json) | [run.py](chengdu-tourism-office/skills/tour-search/scripts/run.py) | `local` | 0 |
| Workload Splitter (`workload-splitter`) | [SKILL.md](chengdu-tourism-office/skills/workload-splitter/SKILL.md) | [skill.json](chengdu-tourism-office/skills/workload-splitter/skill.json) | [run.py](chengdu-tourism-office/skills/workload-splitter/scripts/run.py) | `local` | 0 |

Use the runner forms in [Reviewer guide](REVIEWER_GUIDE.md); the nine tourism runners use a different CLI from the 60 company runners.
