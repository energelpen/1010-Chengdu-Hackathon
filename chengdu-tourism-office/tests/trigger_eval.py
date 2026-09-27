"""Reproducible first-pass routing test; no model calls or fabricated outcomes."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from intent_router import route

CASES=[
 ("Prepare a quotation for a customer workshop.","quotation-package"),
 ("Create a price schedule and quote document for our new service.","quotation-package"),
 ("Give Koru a quote for ten consulting days.","quotation-package"),
 ("Create a proposal with options for a new client portal.","proposal-package"),
 ("We need a pitch deck comparing three launch approaches.","proposal-package"),
 ("Launch a Chengdu food-tour product and compare options.","proposal-package"),
 ("Forecast revenue and cost for the next six months.","finance-forecast"),
 ("Build a monthly financial model for customer growth.","finance-forecast"),
 ("Show projected cash and profit for our next quarter.","finance-forecast"),
 ("Make the Q3 shareholder report.","shareholder-report"),
 ("Draft an investor update from these financials.","shareholder-report"),
 ("Create a board report with growth and cash movement.","shareholder-report"),
 ("Search this Excel workbook for flight costs.","spreadsheet-search"),
 ("Find the customer name in the spreadsheet.","spreadsheet-search"),
 ("Locate the hotel line in the monthly sheet.","spreadsheet-search"),
 ("Edit the Excel actual for September flights.","spreadsheet-edit"),
 ("Change cell C10 in the finance workbook.","spreadsheet-edit"),
 ("Update the spreadsheet with the revised budget.","spreadsheet-edit"),
 ("Simulate a booking confirmation for this tour.","booking-confirm"),
 ("Record a simulated reservation for the group.","booking-confirm"),
 ("Mock a booking for the chosen supplier option.","booking-confirm"),
 ("Update accounting after the simulated booking commitment.","finance-posting"),
 ("Post the booking to the finance budget after approval.","finance-posting"),
 ("Record the booking commitment in accounting.","finance-posting"),
 ("Follow up with the customer next week.","customer-followup"),
 ("Log the client status and next action in CRM.","customer-followup"),
 ("Track a customer follow-up due on Monday.","customer-followup"),
 ("Send a calendar invite for the product review.","calendar-invite"),
 ("Schedule a meeting invitation with the team.","calendar-invite"),
 ("Invite the test contact through Google Calendar.","calendar-invite"),
 ("Send the boss a Telegram update after completion.","telegram-boss-update"),
 ("Notify the boss when the task is done.","telegram-boss-update"),
 ("Use Telegram to report the result.","telegram-boss-update"),
 ("Find current flight prices for Chengdu.","web_search"),
 ("Look for supplier prices for hotels this month.","web_search"),
 ("Compare public tour prices online.","web_search"),
 ("Email the customer a status update.","gmail-send"),
 ("Send a booking request to the supplier by email.","gmail-send"),
 ("Mail the client our reviewed message.","gmail-send"),
 ("Create a PowerPoint presentation for the team.","presentation-create"),
 ("Make slides for our quarterly review.","presentation-create"),
 ("Write meeting minutes from these notes.","meeting-minutes"),
 ("Draft a project timeline with milestones.","project-plan"),
 ("What is our company name?",None),
 ("Hello, how are you?",None),
 ("Explain the approval settings.",None),
 ("Who reports to the director?",None),
 ("Thanks for your help.",None),
]

def evaluate():
    company=json.loads((ROOT/"resources"/"company-general.json").read_text(encoding="utf-8"))
    results=[]
    for prompt,expected in CASES:
        outcome=route(prompt,company)
        actual=outcome["skill_id"] if outcome else None
        results.append({"prompt":prompt,"expected":expected,"actual":actual,"hit":actual==expected,
                        "lead":outcome["lead_id"] if outcome else None})
    positives=[x for x in results if x["expected"]]
    negatives=[x for x in results if not x["expected"]]
    hits=sum(x["hit"] for x in positives)
    return {"primary_intent_hit_rate":round(hits/len(positives),4),"positive_hits":hits,
            "positive_total":len(positives),"negative_correct":sum(x["hit"] for x in negatives),
            "negative_total":len(negatives),"misses":[x for x in results if not x["hit"]]}

if __name__=="__main__": print(json.dumps(evaluate(),indent=2,ensure_ascii=False))
