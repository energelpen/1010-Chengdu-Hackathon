"""Reusable cross-industry packages built from supplied facts, never invented metrics."""
from __future__ import annotations
from datetime import date

def quotation(rt,p):
    from business_tools import cash,document,workbook
    if not p["items"]: raise ValueError("Add at least one quoted line item.")
    try: valid=date.fromisoformat(p["valid_until"])
    except ValueError: raise ValueError("Use a valid YYYY-MM-DD quotation expiry.")
    if valid<date.today(): raise ValueError("Quotation expiry cannot be in the past.")
    lines=[]
    for item in p["items"]:
        if item["quantity"]<=0 or item["unit_price"]<0: raise ValueError("Each line needs positive quantity and nonnegative unit price.")
        lines.append({**item,"amount":cash(item["quantity"]*item["unit_price"])})
    subtotal=cash(sum(x["amount"] for x in lines))
    discount=cash(subtotal*p["discount_rate"])
    taxable=cash(subtotal-discount)
    tax=cash(taxable*p["tax_rate"])
    total=cash(taxable+tax)
    detail="\n".join(f"{x['description']}: {x['quantity']} × {x['unit_price']:,.2f} = {x['amount']:,.2f} {p['currency']}" for x in lines)
    doc=document(rt,{"title":"DRAFT quotation - "+p["customer"],"sections":[
        {"heading":"Scope and line items","body":detail},
        {"heading":"Price summary","body":f"Subtotal {subtotal:,.2f} {p['currency']}\nDiscount {discount:,.2f}\nTax {tax:,.2f}\nTotal {total:,.2f}"},
        {"heading":"Validity and conditions","body":f"Valid until {valid.isoformat()}. {p['terms']}\nDraft only; no order or contract exists."}]})
    sheet=workbook(rt,"DRAFT quotation - "+p["customer"],["Description","Quantity","Unit price","Amount ("+p["currency"]+")"],
                   [[x["description"],x["quantity"],x["unit_price"],x["amount"]] for x in lines]+[["Subtotal",None,None,subtotal],["Discount",None,None,-discount],["Tax",None,None,tax],["DRAFT TOTAL",None,None,total]])
    return {"summary":"Generic quotation calculated and drafted; not sent or accepted.","subtotal":subtotal,"discount":discount,"tax":tax,"total":total,"currency":p["currency"],"artifacts":[doc,sheet]}

def proposal(rt,p):
    from business_tools import document,presentation
    if len(p["options"])<2: raise ValueError("Compare at least two real options.")
    names=[x["name"].casefold() for x in p["options"]]
    if len(set(names))!=len(names): raise ValueError("Option names must be unique.")
    weights=p["weights"]
    if sum(weights.values())<=0: raise ValueError("At least one scoring weight must be positive.")
    max_cost=max(x["cost"] for x in p["options"])
    ranked=[]
    for x in p["options"]:
        if x["cost"]<0: raise ValueError("Option costs cannot be negative.")
        score=(weights["impact"]*x["impact"]/5+weights["risk"]*(6-x["risk"])/5+
               weights["cost"]*(1-x["cost"]/max_cost if max_cost else 1))/sum(weights.values())*100
        ranked.append({**x,"score":round(score,1)})
    ranked.sort(key=lambda x:(-x["score"],x["cost"]))
    slides=[{"title":"Decision to make","bullets":[p["objective"],"Audience: "+p["audience"]]},
            {"title":"Options compared","bullets":[f"{x['name']}: {x['cost']:,.0f} {p['currency']}; score {x['score']}/100" for x in ranked]},
            {"title":"Recommended direction","bullets":[ranked[0]["name"],ranked[0]["benefit"],"Risk: "+ranked[0]["concern"]]},
            {"title":"Approval and next steps","bullets":["Validate assumptions and budget","Assign owner and due date","Approve before external commitments"]}]
    deck=presentation(rt,{"title":p["title"],"slides":slides})
    summary="\n".join(f"{x['name']}: {x['score']}/100; cost {x['cost']:,.0f} {p['currency']}; benefit {x['benefit']}; risk {x['concern']}" for x in ranked)
    brief=document(rt,{"title":p["title"]+" - decision brief","sections":[{"heading":"Objective","body":p["objective"]},{"heading":"Options and scores","body":summary},{"heading":"Recommendation","body":ranked[0]["name"]+" ranks first under the supplied weights. Approval is still required."}]})
    return {"summary":"Proposal deck and decision brief created from supplied options; no commitments made.","recommended":ranked[0]["name"],"ranking":ranked,"weights":weights,"artifacts":[deck,brief]}

def forecast(rt,p):
    from business_tools import cash,workbook
    periods=p["periods"]
    if not periods: raise ValueError("Add at least one forecast month.")
    months=[x["month"] for x in periods]
    if sorted(set(months))!=months: raise ValueError("Months must be unique and chronological.")
    opening=p["opening_customers"]
    rows=[]; results=[]
    for x in periods:
        try:
            d=date.fromisoformat(x["month"]+"-01")
        except ValueError: raise ValueError("Use months in YYYY-MM format.")
        if x["churn"]>opening+x["new_customers"]: raise ValueError("Churn cannot exceed available customers in "+x["month"]+".")
        closing=opening+x["new_customers"]-x["churn"]
        average=opening+(x["new_customers"]-x["churn"])/2
        revenue=cash(average*x["revenue_per_customer"])
        variable=cash(average*x["variable_cost_per_customer"])
        expense=cash(variable+x["fixed_cost"])
        profit=cash(revenue-expense)
        item={"month":d.strftime("%Y-%m"),"opening_customers":opening,"new_customers":x["new_customers"],"churn":x["churn"],"closing_customers":closing,"average_customers":average,"revenue":revenue,"variable_cost":variable,"fixed_cost":x["fixed_cost"],"expense":expense,"operating_profit":profit}
        results.append(item)
        rows.append([item[k] for k in ("month","opening_customers","new_customers","churn","closing_customers","average_customers","revenue","variable_cost","fixed_cost","expense","operating_profit")])
        opening=closing
    artifact=workbook(rt,p["title"],["Month","Opening customers","New customers","Churn","Closing customers","Average billable customers","Revenue ("+p["currency"]+")","Variable cost","Fixed cost","Total expense","Operating profit"],rows)
    return {"summary":"Monthly operating forecast calculated; average billable customers assume additions and churn occur evenly within each month.","currency":p["currency"],"months":results,"total_revenue":cash(sum(x["revenue"] for x in results)),"total_operating_profit":cash(sum(x["operating_profit"] for x in results)),"artifacts":[artifact]}

def shareholder(rt,p):
    from business_tools import cash,document,presentation
    revenue,prior=p["revenue"],p["prior_revenue"]
    gross=cash(revenue-p["cost_of_sales"])
    operating=cash(gross-p["operating_expenses"])
    growth=round((revenue-prior)/prior*100,1) if prior else None
    margin=round(gross/revenue*100,1) if revenue else None
    cash_change=cash(p["cash_end"]-p["cash_start"])
    metrics=f"Revenue {revenue:,.2f} {p['currency']}\nRevenue growth {growth if growth is not None else 'n.a.'}%\nGross profit {gross:,.2f}\nGross margin {margin if margin is not None else 'n.a.'}%\nOperating profit {operating:,.2f}\nCash change {cash_change:,.2f}"
    sections=[{"heading":"Financial results","body":metrics},{"heading":"Highlights","body":"\n".join(p["highlights"])},{"heading":"Risks","body":"\n".join(p["risks"])},{"heading":"Management actions","body":"\n".join(p["actions"])},{"heading":"Status","body":"Draft prepared from supplied figures. Figures are not audited and no shareholder distribution has occurred."}]
    brief=document(rt,{"title":"DRAFT shareholder report - "+p["period"],"sections":sections})
    deck=presentation(rt,{"title":"DRAFT shareholder update - "+p["period"],"slides":[{"title":"Financial results","bullets":metrics.split("\n")},{"title":"Progress and risks","bullets":p["highlights"][:3]+p["risks"][:3]},{"title":"Management actions","bullets":p["actions"][:6]}]})
    return {"summary":"Draft shareholder Word report and slide deck created from supplied figures; not audited or sent.","metrics":{"revenue_growth_pct":growth,"gross_profit":gross,"gross_margin_pct":margin,"operating_profit":operating,"cash_change":cash_change},"artifacts":[brief,deck]}
