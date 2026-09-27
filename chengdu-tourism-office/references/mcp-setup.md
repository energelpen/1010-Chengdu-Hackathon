# MCP server and email delivery

The [server](../server/tourism_mcp.py) uses the official Python MCP SDK's stdio transport. It exposes:

- `simulate_rfq`: run the synthetic full workflow and render artifacts.
- `compare_flights`, `find_tours`: research the bundled fixture offers.
- `search_prior_cases`: query the local case index.
- `preview_report_email`: inspect the stored draft and attachment names.
- `send_approved_report_email`: send the stored draft and Word/PowerPoint reports through SMTP.

Install dependencies and launch the local server:

```powershell
python -m pip install -r requirements.txt
python server/tourism_mcp.py
```

The process waits silently for an MCP host on stdin. Point a host's stdio MCP configuration at the **absolute** path to your Python executable and this server file. The [official MCP host guide](https://py.sdk.modelcontextprotocol.io/get-started/real-host/) explains host-specific configuration. Keep the server local unless you separately add authentication for a network transport.

Actual email sending requires all of these environment variables in the MCP server process:

```text
TOURISM_EMAIL_APPROVAL_CODE=<human-held code>
TOURISM_EMAIL_ALLOWLIST=approved@example.com,another@example.com
TOURISM_SMTP_HOST=<SMTP server>
TOURISM_SMTP_PORT=587
TOURISM_SMTP_FROM=<sender address>
TOURISM_SMTP_USER=<SMTP username>
TOURISM_SMTP_PASSWORD=<SMTP password>
```

The tool reads the exact stored draft from an eligible case, attaches only that case's generated reports, checks the allowlist, approval code and readiness decision, then sends over STARTTLS. The `example.test` demo address is intentionally unsendable. Do not put credentials or approval codes in the repository. The local web UI previews drafts and downloads reports; it does not invoke the send tool automatically.

Flight and tour search default to transparent fixtures. To compare provider data, pass a normalized flight `snapshot` or tour `catalog` to the relevant skill. Include source, observation time, currency, capacity and final-price caveats. Public airfare searches are not reliable group quotations; the supplier task remains mandatory.
