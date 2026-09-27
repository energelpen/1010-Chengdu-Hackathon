# Atlas Office — SP-D organizational collaboration simulator

[GitHub repository](https://github.com/energelpen/1010-Chengdu-Hackathon) · [Submission files and narrated demo](../submission/README.md) · [Full API PDF](../submission/02-api-documentation.pdf)

The submission recording demonstrates 13 distinct skills in a complete operator-led launch-preparation simulation. It uses local typed forms, actual generated files, a reviewed spreadsheet change and supplied fictional completion evidence. No-key general-company chat provides directory/help responses; it does not execute the free-form prompts below. Those chat examples require a working OpenAI connection. The strict SP-D requirement for automatic full launch completion from one sentence remains unverified.

Atlas Office is a local company-assistant workspace with programmable AI colleagues, a 69-skill library, saved conversations, live task progress, connected tools and an SP-D tourism-company simulation. The general-company template supports one-sentence requests for quotations, option proposals, slides, monthly forecasts, shareholder updates, spreadsheet searches/edits, project work and customer follow-up. The assistant routes work to qualified staff, records each tool run and creates real draft files. The tourism template additionally takes a group inquiry or RFQ through a nine-stage planning and approval workflow with synthetic supplier options, a dated itinerary and searchable case record.

The demo staff, relationships, prices and approvals are fictional. Atlas Office does not make real reservations or payments. Public web prices are indicative, not live inventory. External messages and reviewed file changes need explicit approval; the demo restricts email and calendar recipients to the test address shown in Connections.

## Start

Requires Python 3.11 or newer. In this folder:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:8765`. The default **General company** template can run the examples below. For the tourism-specific SP-D flow, choose **Chengdu tourism** in **Workspace settings**, then try: “RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage tour from 2026-10-25, budget CNY 200000.” Changing templates saves the previous organization. Conversations and linked cases survive refreshes and restarts.

## General-company demo

Paste one of these into Assistant. Open **Activity & approvals** for the actual run and assigned staff member, and **Files & knowledge** for artifacts. The assistant also shows per-person progress events in the conversation.

- “Create a draft quotation for Acme Ltd for two product-launch workshops at CNY 5,000 each, with 5% discount, 6% tax, valid until 2026-12-31, subject to written approval and final scope.” This creates a Word quotation and Excel price schedule without sending them.
- “Make a draft PowerPoint proposal and Word decision brief for the executive team choosing a CNY customer portal launch: Pilot first costs 50000, impact 4/5, risk 2/5, benefit one-market validation, concern slower reach; Full launch costs 120000, impact 5/5, risk 4/5, benefit all customers sooner, concern delivery risk; use impact/risk/cost weights 5/3/2.” This calculates a transparent comparison and creates editable drafts.
- “Forecast October and November 2026 in CNY from 20 opening customers: October adds 5 and loses 1, revenue 3000 and variable cost 900 per average customer, fixed cost 25000; November adds 4 and loses 2, revenue 3100 and variable cost 950 per average customer, fixed cost 26000; create the Excel forecast.”
- “Create a draft Q3 2026 shareholder Word report and PowerPoint in CNY using revenue 900000, prior revenue 800000, cost of sales 480000, operating expenses 210000, cash start 300000, cash end 335000; highlight improved customer renewals, note volatile supplier costs as a risk, and propose reviewing supplier contracts in October.” The results are explicitly unaudited and unsent.

The **monthly-finance-demo.xlsx** workbook is preloaded under Files. Its BvA tab separates customer income and supplier outflow, with actuals kept distinct from simulated pipeline and commitments. **Simulate booking confirmation** creates a local record, not a reservation. After director review, **Finance posting** writes a new workbook copy and a draft invoice; it does not change actuals or issue an invoice.

## Connect OpenAI

Open **Workspace settings → OpenAI connection**, create a new key in the OpenAI dashboard, and enter it in the password field. The local server saves it in an ignored `.env` file beside `app.py`; the key is never returned to the browser. You can instead create `.env` yourself using [.env.example](.env.example):

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-6-astra
```

The file and Settings methods take effect immediately. You can also set `OPENAI_API_KEY` and `OPENAI_MODEL` in the server's environment; environment values override `.env` and must be changed at the server. Keep API keys out of chat messages and browser code. If a key has been exposed, revoke it and generate a replacement before configuring the app. `.env` is ignored by Git.

With a key, Atlas and staff avatars use the official OpenAI Python SDK and Responses API. The assistant receives the recent conversation, selected person's role, roster and linked case so it can explain the actual work. Responses use `store=False`; the app stores its own history in `output/conversations.sqlite`. A failed API call preserves your message and shows a readable error. With no key, the app remains usable with clearly identified local responses. See the [official OpenAI quickstart](https://developers.openai.com/api/docs/quickstart) and [conversation-state guide](https://developers.openai.com/api/docs/guides/conversation-state).

## Connect optional services

The existing OpenAI key also powers public web search; no second search key is needed. Current supplier listings are only indicative. A real availability-and-reservation integration would need a separate supplier agreement/API and is intentionally not part of this demo.

For Google Workspace, create a **Desktop app OAuth client JSON** in Google Cloud, enable only the APIs you intend to use, and run from this folder:

```powershell
.venv\Scripts\python.exe scripts/google_connect.py --credentials "path/to/client-secret.json" --services drive sheets docs slides gmail calendar
```

This opens Google's sign-in and consent flow; the client JSON and resulting token stay on this machine. Gmail sending and Calendar invitations remain pending in Activity until approved and are restricted to `amonsk007@gmail.com` in the demo. To enable a reviewed Telegram notification to the boss, add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_BOSS_CHAT_ID` to `.env` and restart the server. Optional SMTP delivery for the tourism workflow needs the variables documented in [autonomy.md](references/autonomy.md). Do not paste credentials into conversations or commit them to Git.

## Company review and autonomy

Settings controls whether a tourism request stops at a proposal, requires separate delivery approval, or executes within saved rules. The default is proposal-first: the team prepares the plan, then waits for review before recording simulated execution. Return a proposal with comments, resubmit a revision, or escalate an issue to the lead's manager. The review history records each transition. Autonomous mode respects the configured quotation limit; amounts above it still need review. Task-board buttons cannot bypass this approval, and changing the selected option or task ownership clears the old approval. A partial budget or date revision preserves the other original trip facts and earlier review comments.

Report generation and email delivery are separate settings. Real email is off by default. Enabling it requires allowed recipients and server-side SMTP configuration; approval-required mode also needs a separate delivery approval. A blocked proposal or failed delivery records an in-app escalation with the manager, reason and suggested next step; it does not automatically email a real boss. See [governance and delivery](references/autonomy.md) for the exact settings, review states and SMTP variables. Separately, external write actions from the general skills library, Google Workspace or MCP connections require review in **Activity & approvals**, regardless of the tourism autonomy setting.

## Demo path

1. Send the example sentence to Atlas and run the company workflow. Review its proposal and the nine-stage closed loop.
2. Open **Org chart** from the sidebar. Filter reporting, current-task collaboration and follow links; select a colleague to inspect their manager, direct reports, workload and skills, then talk to them and play their answer aloud.
3. Add or edit a staff member, changing skills, manager, capacity, follow links, decision style, avatar color, voice and agent guidance. Run a new request to see the routing and workload change. Older cases retain their roster snapshot.
4. Inspect complete price options, flight and tour comparisons, and the dated schedule. Select an alternative to clear stale price approvals. On the Execution board, reassign a qualified owner, record evidence, or raise and resolve an incident.
5. Approve or return the proposal with comments. Download the Word brief, PowerPoint deck or JSON trace when reports are enabled. Reopen earlier conversations from history or search cases by request or activity. Email remains a draft unless enabled and authorized by the saved delivery rules.

Speech playback uses the browser's speech synthesis support; fictional portraits highlight during speech rather than providing lip-synced video. Dictation is optional, may be unavailable, and may use the browser's voice service; review the transcript before submission. Avatars provide role-grounded AI responses when OpenAI is configured and local explanations otherwise. In the general-company template, OpenAI can discover and run assigned skills through a bounded tool loop; external writes remain pending until reviewed. In the tourism template, workflow and proposal controls determine execution. The nine tourism agent skills are individually callable through the CLI and MCP tooling; see [SKILL.md](SKILL.md), [API](references/api.md), and [MCP setup](references/mcp-setup.md).

The skills library also includes responsibility matrices, capacity-based workload rebalance, weighted scenario comparison, and management handoffs with a Word brief and unsent email draft. New company templates assign these skills to relevant staff; existing custom rosters can assign them in **Your people**.

The app is a local workspace bound to `127.0.0.1`; all conversations belong to that workspace. Authentication and separate employee accounts are not included. A shared company deployment should add identity, role-based data access and an HTTPS application server before exposing it beyond the computer.

## Verify

```powershell
.venv\Scripts\python.exe scripts/tourism_office.py test
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
.venv\Scripts\python.exe tests/trigger_eval.py
.venv\Scripts\python.exe tests/browser_general_smoke.py
node --check web/app.js
```

On 2026-09-26, the general-company first-pass router matched 43 of 43 fixed task prompts and correctly left 5 of 5 non-action prompts unassigned. This is a **routing trigger rate on a fixed test corpus**, not a measure of arbitrary-language or end-to-end success. All 46 automated tests passed. Five manually submitted live requests also completed: quotation, option proposal, finance forecast, shareholder report and public-price web search; the first four created recorded files, and the last cited a public source without booking. The 16-view desktop/mobile browser pass found no JavaScript errors or page-level horizontal overflow. OAuth email/calendar and Telegram delivery require private credentials and have not been live-sent in this verification. Tourism offers remain synthetic fixtures.

For a concise judging narrative, see the [five-minute demo script](references/demo-script.md). The [track-choice note](references/track-choice.md) explains why SP-D is the clearest fit for this build while SP-B is the broader technical challenge.
