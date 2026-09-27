---
name: booking-confirm
description: Record a simulated tourism booking decision without making a reservation.
---

# Simulate booking confirmation

Use this after comparing documented options and receiving the user's decision. Require a customer, product, date, positive quote and selected option. The output is an auditable local record with `status=simulated_confirmed` and `real_booking=false`. It is **not** supplier inventory, a payment, a reservation or customer communication.

If the option lacks a source or the customer has not chosen it, explain the missing decision rather than treating the simulation as a booking. After recording, finance may prepare `finance-posting` for review; customer success may record `customer-followup`, and sales may draft a booking-request email to the test inbox.

Run `python skills/booking-confirm/scripts/run.py --input skills/booking-confirm/references/example.json` from the project root. Substitute real user-provided task facts for the example.
