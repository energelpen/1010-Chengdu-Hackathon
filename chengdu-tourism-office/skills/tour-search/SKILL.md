---
name: tourism-tour-search
description: Search Chengdu activities against traveler interests, group capacity and accessibility requirements. Use after inquiry intake when an itinerary needs priced tour candidates.
---

# Tour Research Agent

Accept `inquiry` with `group_size`, `interests` and optional `accessible`; optionally accept a supplier `catalog`. Rank activities by matched interests and group cost, and show capacity or accessibility rejects. The bundled catalog is synthetic and availability remains unverified. Pass chosen activities to quote comparison and schedule building, then request supplier confirmation before client release.

Run `python scripts/run.py '@../../examples/tour-search.json'` from this skill directory. Run `python scripts/run_tests.py` for decision cases.
