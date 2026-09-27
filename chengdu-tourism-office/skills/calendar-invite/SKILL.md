---
name: calendar-invite
description: Send a reviewed Google Calendar test invitation with explicit time zone and agenda.
---

# Send test calendar invitation

Verify the date, start and end with explicit timezone offsets and a real agenda. The only demo attendee is `amonsk007@gmail.com`; other addresses are rejected. Google OAuth calendar access must already be connected. Submission creates a pending action; the operator reviews and approves it in Activity. On approval, Google creates the event and requests attendee email updates.

If credentials are missing, the date is invalid or the provider result is uncertain, stop and report the issue. Do not describe a draft event as an invitation sent. Inspect the calendar before retrying an uncertain write.

Run `python skills/calendar-invite/scripts/run.py --input skills/calendar-invite/references/example.json` from the project root.
