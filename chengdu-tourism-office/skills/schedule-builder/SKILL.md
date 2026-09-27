---
name: tourism-schedule-builder
description: Build a dated, conflict-aware Chengdu group itinerary from a travel inquiry, selected activities and optional flights. Use after option selection and tour research.
---

# Schedule Agent

Accept `inquiry`, a chosen `activities` list, and optional `flight`. Reserve arrival and departure days, place each activity in its preferred morning, afternoon or evening slot, reject overlong activities and expose unscheduled items. Check flight dates against the itinerary. Keep booking status unconfirmed; the schedule is a plan until suppliers confirm time slots.

Run `python scripts/run.py '@../../examples/schedule.json'` from this skill directory. Run `python scripts/run_tests.py` for decision cases.
