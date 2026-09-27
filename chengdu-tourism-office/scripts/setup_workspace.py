"""Generate bundled templates and integration examples; never edits live company data."""
import copy
import json
from pathlib import Path
from build_skill_catalog import ROOT,build

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def main():
    build()
    tourism=json.loads((ROOT/"resources"/"tourism-company.json").read_text(encoding="utf-8"))
    company=copy.deepcopy(tourism)
    company.update(company="Atlas Company",template="general",simulation=False,affiliation_claim="Fictional staff for your editable company workspace.")
    assignments={
      "director":("Chen","Director",["decision-log","team-capacity","risk-register","presentation-create","policy-checklist"]),
      "sales_manager":("Wang","Sales lead",["crm-pipeline","email-draft","gmail-search","gmail-draft","presentation-create","document-create"]),
      "sales_exec":("Li","Sales specialist",["crm-pipeline","email-draft","gmail-draft","calendar-event","calendar-create"]),
      "account_exec":("Zhou","Customer success lead",["support-triage","email-draft","knowledge-search","gmail-search","gmail-draft","meeting-minutes"]),
      "product_manager":("Zhao","Product lead",["project-plan","task-tracker","document-create","presentation-create","slides-create","docs-create","campaign-plan"]),
      "itinerary_specialist":("Liu","People & culture lead",["hr-onboarding","hiring-scorecard","leave-request","policy-checklist","calendar-event","document-create"]),
      "supplier_manager":("Huang","Procurement lead",["procurement-compare","inventory-reorder","contract-checklist","spreadsheet-create","drive-search"]),
      "ops_manager":("He","Operations lead",["project-plan","task-tracker","meeting-minutes","incident-report","risk-register","calendar-list","calendar-create","team-capacity"]),
      "transport_coordinator":("Sun","IT & knowledge lead",["knowledge-save","knowledge-search","pdf-extract","csv-clean","drive-search","drive-upload","docs-read"]),
      "finance_manager":("Deng","Finance lead",["invoice-create","expense-report","budget-variance","spreadsheet-create","spreadsheet-analyze","sheets-read","sheets-write","sheets-create","pdf-create"]),
    }
    for p in company["people"]:
        name,role,skills=assignments[p["id"]]
        p.update(name=name,role=role,skills=skills,portrait=p["id"],department=role.replace(" lead", ""),agent_instructions=f"Help with {role.lower()} responsibilities. Use your assigned skills and report actual results, assumptions and missing inputs.")
    company["people"][5]["reports_to"]="director"
    write(ROOT/"resources"/"company-general.json",company)
    tourism["template"]="tourism"
    for p in tourism["people"]:
        p["portrait"]=p["id"]
        p["skills"]+=assignments[p["id"]][2]
    write(ROOT/"resources"/"company-tourism-template.json",tourism)
    mappings={"inquiry-intake":"rfq","flight-search":"flight-search","tour-search":"tour-search","option-comparison":"compare","hierarchy-router":None,"workload-splitter":"workload","schedule-builder":"schedule","execution-controller":"execution","outcome-reporter":"outcome"}
    for id,example in mappings.items():
        sample=json.loads((ROOT/"examples"/(example+".json")).read_text(encoding="utf-8")) if example else {"request_id":"demo","inquiry":{"group_size":30,"duration_days":3,"budget_cny":200000}}
        write(ROOT/"skills"/id/"skill.json",{"id":id,"title":id.replace("-"," ").title(),"category":"Tourism template","description":"Run the existing synthetic tourism "+id.replace("-"," ")+" stage.","handler":"tourism","function":id.replace("-","_"),"effect":"local","input_schema":{"type":"object","title":"Tourism stage input"},"example":sample,"version":"2.0.0"})
    providers=[("microsoft-365","Microsoft 365"),("slack","Slack"),("teams","Microsoft Teams"),("notion","Notion"),("github","GitHub"),("linear","Linear"),("salesforce","Salesforce"),("hubspot","HubSpot"),("jira","Jira"),("zendesk","Zendesk"),("dropbox","Dropbox"),("box","Box"),("sharepoint","SharePoint")]
    servers=[{"id":"atlas-local","name":"Atlas local tools","enabled":True,"transport":"stdio","command":"${PYTHON}","args":["${ROOT}/server/company_mcp.py"],"env_keys":[],"allowed_tools":["get_company","list_skills","list_files","search_knowledge"]}]
    servers += [{"id":id,"name":name,"enabled":False,"transport":"http","url":"","token_env":id.upper().replace("-","_")+"_MCP_TOKEN","allowed_tools":[]} for id,name in providers]
    write(ROOT/"config"/"mcp-servers.example.json",{"servers":servers})
    if not (ROOT/"config"/"mcp-servers.json").exists(): write(ROOT/"config"/"mcp-servers.json",{"servers":servers})

if __name__=="__main__": main()
