"""Transparent first-pass task routing; the agent may refine this suggestion."""
from __future__ import annotations
import re

PATTERNS = [
    ("telegram-boss-update",r"\btelegram\b|notify (?:the )?boss"),
    ("calendar-invite",r"\b(calendar invite|invite .*calendar|schedule .*meeting|meeting invitation)\b"),
    ("shareholder-report",r"\b(shareholder|investor update|board report|annual report)\b"),
    ("finance-posting",r"\b(post|update|record).*(?:booking|commitment).*(?:budget|accounting|finance)|\b(post|update|record).*accounting.*(?:booking|commitment)|\bfinance posting\b"),
    ("finance-forecast",r"\b(forecast|projection|projected cash|future revenue|financial model)\b"),
    ("spreadsheet-search",r"\b(search|find|locate|look up).*(?:excel|spreadsheet|workbook|sheet)\b"),
    ("spreadsheet-edit",r"\b(edit|change|update|modify).*(?:excel|spreadsheet|workbook|cell)\b"),
    ("booking-confirm",r"\b(simulate|mock|record).*(?:booking|confirmation|reservation)\b"),
    ("customer-followup",r"\b(follow[ -]?up|follow through|customer status|client status|crm)\b"),
    ("quotation-package",r"\b(quotation|quote document|price schedule|cost estimate|quote for|prepare a quote)\b"),
    ("proposal-package",r"\b(proposal|pitch deck|compare options|business case|product launch)\b"),
    ("gmail-send",r"\b(send|email|mail).*(?:email|message|supplier|customer|client)\b"),
    ("presentation-create",r"\b(slides|slide deck|powerpoint|presentation)\b"),
    ("document-create",r"\b(word document|brief|memo|write a document)\b"),
    ("meeting-minutes",r"\b(meeting minutes|minutes from|meeting notes)\b"),
    ("project-plan",r"\b(project plan|timeline|milestones|project schedule)\b"),
]

def route(message,company):
    text=" ".join(message.casefold().split())
    skill=next((name for name,pattern in PATTERNS if re.search(pattern,text)),None)
    if not skill and re.search(r"\b(flight prices|hotel prices|supplier prices|tour prices|travel prices|find suppliers)\b",text):
        skill="web_search"
    if not skill: return None
    people=company.get("people",[])
    candidates=[p for p in people if p.get("available") and skill in p.get("skills",[])]
    if skill=="web_search": candidates=[p for p in people if p.get("available") and p["id"] in ("supplier_manager","sales_manager")]
    candidates.sort(key=lambda p:((p.get("assigned_hours",0)/max(p.get("capacity_hours",1),1)),p.get("name","")))
    lead=candidates[0]["id"] if candidates else "atlas"
    collaborator_ids={
        "proposal-package":["product_manager","finance_manager","sales_manager"],
        "quotation-package":["sales_manager","finance_manager"],
        "finance-posting":["finance_manager","sales_manager"],
        "booking-confirm":["product_manager","supplier_manager","finance_manager"],
        "shareholder-report":["finance_manager","director"],
        "web_search":["supplier_manager","product_manager"],
    }.get(skill,[])
    collaborators=[p["id"] for p in people if p.get("available") and p["id"] in collaborator_ids and p["id"]!=lead]
    return {"skill_id":skill,"lead_id":lead,"collaborators":collaborators[:3],
            "reason":"First-pass intent and current skill/capacity match; the agent checks required inputs before execution."}
