---
name: tourism-flight-search
description: Compare dated group flight offers for a tourism RFQ by route, seats, full fare, stops and baggage. Use after inquiry intake when flights form part of the requested trip.
---

# Flight Research Agent

Accept `inquiry` and optional `snapshot` with `source`, `observed_at`, `currency: CNY`, and `offers`. Filter route, departure and return dates, group seat capacity and valid fare. Rank eligible offers by full group cost, then stops and duration. Explain every rejection. The bundled snapshot is synthetic; if a connected provider supplies offers, retain its source and timestamp. An offer is an estimate until the supplier confirms group inventory and fare.

Run `python scripts/run.py '@../../examples/flight-search.json'` from this skill directory. Run `python scripts/run_tests.py` for decision cases.
