---
name: management-handoff
description: Turn cross-team task status and blockers into a concise manager report, a Word brief, and an unsent email draft. Use when a boss needs an outcome update or a stalled request needs a clear resolution path.
---

# Management handoff

Gather the actual status, owner, due date, next step, and blocker for each work item. If an item is blocked, require a specific blocker. Keep the report faithful to supplied facts; mark unknown status as not started only when the user confirms it. The report summarizes progress, names work needing management attention, and drafts a message for the named audience.

Run through the Skills library or `scripts/run.py` with JSON input. The Word artifact and email draft are saved in Activity and Files. Sending mail requires a separate connected email skill and its review gate.
