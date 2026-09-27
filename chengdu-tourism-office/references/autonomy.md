# Company control and review

Atlas Office keeps company preferences in `output/settings.json`. They contain no API keys or SMTP passwords. Use the Settings screen to choose how much responsibility to delegate; saved preferences apply to new proposals. Each proposal records the preferences used to create it, its quotation, the reviewed plan fingerprint, feedback and dated review events.

| Mode | Plan and execution | Email delivery |
| --- | --- | --- |
| Proposal first | Prepare a proposal and wait for approval. Approval permits execution when Execute plan is enabled. | After plan approval, sending follows the explicit email setting and allowed-recipient list. |
| Approval required | Review the proposal before execution. | Also requires a separate approval of email delivery. |
| Autonomous | Approve and execute feasible plans within the automatic quotation limit when Execute plan is enabled. | Send after the workflow completes only when email is enabled, the recipient is allowed, and the quotation is within the delegated limit. No additional approval code is required. |

All modes respect the independent **Execute plan**, **Generate reports** and **Send email** switches. Execute plan grants permission; in a review mode, the team still waits for approval. Turning it off keeps an approved proposal as a plan until execution is explicitly enabled. Send email defaults to off, and an empty recipient list allows no delivery. The default automatic quotation limit is CNY 200,000. A quotation above that limit needs a human decision even in autonomous mode.

## Returning work and resolving issues

1. **Request changes** adds review comments and returns the proposal to the team. The comments remain in its history.
2. Update the task, option or assignments, then **Resubmit** with an explanation of the changes. The proposal receives a new revision and awaits review.
3. **Escalate** records why the task cannot be submitted. Atlas routes an in-app message to the task lead's reporting manager, or the company leader when there is no higher manager. The message includes the request, blocker and suggested next step. This is an in-app management notification, not an email to the manager.
4. **Resolve** needs a written explanation. If the actual case still has unavailable offers, unresolved incidents or another blocking condition, the issue remains open until the plan is fixed. Once resolved, the team can resubmit it.

Changing the reviewed request, quotation, assignments, task list or schedule invalidates its fingerprint. An old approval cannot authorize email for that changed plan. Unfinished internal approval tasks are normal before execution; they do not create a false escalation. Actual missing inputs, impossible offers, schedule conflicts and open incidents do.

A completed proposal can be reopened with review comments. Editing an option or assignment returns the plan for changes and clears its delivery authority; explicit resubmission starts the next revision. A revised request in the same conversation retains the proposal identity, prior request IDs, review comments, audit history and previous delivery receipts. Revised work always returns for review, including when the original proposal used autonomous mode. An existing manager escalation remains open during in-place edits until its resolution is recorded.

## Email connection

The application sender uses `TOURISM_SMTP_HOST`, `TOURISM_SMTP_FROM`, `TOURISM_SMTP_USER`, `TOURISM_SMTP_PASSWORD`, and optionally `TOURISM_SMTP_PORT` (587 by default). Set these in the server environment. SMTP uses STARTTLS. Report attachments are included when report generation is enabled. Demonstration `.test` addresses cannot receive real mail.

Before sending, Atlas verifies the proposal, unchanged plan, workflow evidence, delivery mode, email switch, recipient and amount. Delivery receipts prevent duplicate sends for the same proposal revision. If the mail server fails before sending, fix the connection and resolve the issue. If it fails during delivery and the result is uncertain, the manager must check the sender's outbox before creating a new revision and retrying; Atlas does not blindly send it again.

The built-in travel workflow remains a simulation. Its task evidence does not confirm a real flight, booking or supplier contract. A real SMTP email carrying a simulated proposal is explicitly labelled as a demonstration with indicative prices. This review module never interprets a simulated task completion as a supplier confirmation.

## Integration contract

- `load_settings(data)` and `save_settings(data, updates)` read and atomically save validated settings under the supplied output directory.
- `create_proposal(case, settings)` produces a `pending_review`, `approved` or `escalated` proposal with a manager, issues and audit history.
- `revise_proposal(proposal, case, policy, comment, submit=True)` preserves proposal identity and history for a revised request. With `submit=False`, an edited plan returns for changes and waits for explicit resubmission before its revision increments.
- `review_proposal(proposal, action, comment, case, people=None)` returns a copy after `approve`, `request_changes`, `escalate`, `resolve`, `resubmit` or `approve_email`.
- The execution controller may call `review_proposal(..., action="complete", internal=True)` after the workflow has produced all required evidence.
- `authorize_email(policy, recipient, quote, approval)` validates delivery authority without sending anything. The caller must also verify the reviewed case and workflow readiness.
- `send_approved_email(case, proposal, policy, output_dir)` performs all checks, sends through configured SMTP, and records a receipt. Settings are checked again at delivery time, so a current email disable or recipient removal takes effect immediately.

The Settings API stores only `autonomy_mode`, `execute_plan`, `send_email`, `generate_reports`, `allowed_recipients` and `max_auto_quote_cny`. It rejects unrecognized fields, including keys and passwords.
