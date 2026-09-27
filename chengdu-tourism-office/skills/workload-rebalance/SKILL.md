---
name: workload-rebalance
description: Propose skill and capacity aware assignments for office tasks using the saved company roster. Use when several tasks need workload splitting, a preferred colleague may be unavailable, or a manager needs a clear staffing blocker.
---

# Workload rebalance

Use task names, estimated hours, and exact skill IDs from the Skills library. Inspect the current org chart for available colleagues and remaining weekly hours. The skill projects assignments sequentially, choosing the colleague with the lowest resulting utilization; a preferred colleague is honored only if they have the skill and capacity. Surface unassigned work and its reason for manager resolution.

The result is a staffing proposal. It does not change a colleague's saved workload, complete tasks, or notify anyone. Enter the tasks in priority order when order matters. Run through the Skills library or `scripts/run.py` with JSON input.
