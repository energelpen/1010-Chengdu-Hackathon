---
name: telegram-boss-update
description: Notify the configured boss chat after a task has actually completed.
---

# Notify boss on Telegram

Select an existing **completed** skill run and write a short optional context note. The notification includes the actual agent, skill, run ID and recorded outcome. Configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_BOSS_CHAT_ID` in the server's private `.env`; no token is returned to the browser. Submission waits for human review in Activity. The configured boss chat is the only destination.

If the run is pending, failed or absent, do not send. If Telegram does not confirm the delivery, record `needs_attention`; check the boss chat before attempting a new run because the delivery state may be uncertain.

Run `python skills/telegram-boss-update/scripts/run.py --input skills/telegram-boss-update/references/example.json` after replacing the example run ID.
