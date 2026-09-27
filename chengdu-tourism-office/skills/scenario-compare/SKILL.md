---
name: scenario-compare
description: Compare several business or travel options across user supplied weighted criteria such as cost, quality, capacity, or delivery time. Use when the decision needs transparent tradeoffs beyond a single price.
---

# Scenario compare

Collect at least two options and the same numeric measures for every criterion. Ask whether higher or lower is better for each measure and ask for nonzero weights. Use actual supplied numbers and label their source and currency in the criterion name or surrounding explanation. If a measure is missing, stop and request it.

The skill normalizes each criterion across the submitted options, applies the weights, and returns the ranked scores and per-criterion contributions. Equal values receive equal credit. Treat the recommendation as decision support; it does not book a flight, choose a supplier, or approve spending. Run through the Skills library or `scripts/run.py` with JSON input.
