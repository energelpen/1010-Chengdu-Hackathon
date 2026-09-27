---
name: responsibility-matrix
description: Build a RACI responsibility matrix for a cross-functional company project from the current roster. Use when a task needs clear owners, one accountable decision maker, consulted specialists, and informed colleagues.
---

# Responsibility matrix

Use the current company roster shown in the org chart. Ask for task names and responsible, accountable, consulted, and informed colleagues when any required assignment is missing. Colleagues may be named by roster ID or exact display name. Require one accountable person and at least one responsible person for every task. Review the reporting route with the user when accountability is unclear; a matrix is a proposal and does not change assignments or send notifications.

Run the skill through the Skills library or `scripts/run.py` with JSON input. Return the matrix and an Excel artifact. If a person is absent from the current roster, report the unknown name instead of silently assigning another person.
