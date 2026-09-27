"""Additional REST routes and OpenAPI contract for the general company workspace."""
import json
import re
from pathlib import Path
from urllib.parse import parse_qs
from skill_runtime import ROOT,Runtime
from google_workspace import GoogleWorkspace
from mcp_bridge import Bridge

def specification(rt):
    paths={}
    def route(path,method,summary,body=None):
        operation={"summary":summary,"responses":{"200":{"description":"Successful result","content":{"application/json":{"schema":{"type":"object"}}}},"400":{"description":"Input validation failed"},"403":{"description":"Action not allowed"},"404":{"description":"Item not found"}}}
        params=re.findall(r"\{(\w+)\}",path)
        if params: operation["parameters"]=[{"name":p,"in":"path","required":True,"schema":{"type":"string"}} for p in params]
        if body is not None: operation["requestBody"]={"required":True,"content":{"application/json":{"schema":body}}}
        paths.setdefault(path,{})[method]=operation
    object_schema={"type":"object"}
    route("/api/conversation/{id}/agent-run","get","Latest measured agent run: plan, skill calls, assignments, artifacts and token usage")
    route("/api/conversation/{id}/events","get","Recorded assistant progress events")
    for path,summary in [("/api/health","Server status"),("/api/company","Current organization"),("/api/templates","Organization templates"),("/api/skills","Executable skill catalog"),("/api/skills/{id}","Skill instructions and schema"),("/api/runs","Recorded runs"),("/api/runs/{id}","Single run result"),("/api/files","Workspace files"),("/api/records","Company work register"),("/api/connections","Connection configuration status"),("/api/audit","Recent audit events"),("/api/conversations","Saved conversations"),("/api/conversation/{id}","Saved conversation messages"),("/api/settings","Saved autonomy settings"),("/api/config","Public AI configuration"),("/api/case/{id}","Saved tourism case"),("/api/search","Search tourism cases")]: route(path,"get",summary)
    for path,summary in [("/api/runs/{id}/approve","Execute the exact pending external action once"),("/api/runs/{id}/reject","Cancel a pending external action")]: route(path,"post",summary,object_schema)
    for skill in rt.catalog():
        body={"type":"object","properties":{"inputs":skill["input_schema"],"person_id":{"type":"string","default":"atlas"},"idempotency_key":{"type":"string"}},"required":["inputs"],"additionalProperties":False}
        route("/api/skills/"+skill["id"]+"/run","post",skill["title"]+" — "+skill["effect"],body)
        paths["/api/skills/"+skill["id"]+"/run"]["post"]["requestBody"]["content"]["application/json"]["example"]={"inputs":skill["example"]}
    post={
      "/api/chat":("Message Atlas or an individual colleague",{"type":"object","properties":{"message":{"type":"string","minLength":1,"maxLength":6000},"person_id":{"type":"string"},"conversation_id":{"type":"string"},"run_workflow":{"type":"boolean","description":"Run the tourism template pipeline"}},"required":["message"]}),
      "/api/company":("Save the editable organization",object_schema),
      "/api/company/template":("Apply a template; current structure is backed up",{"type":"object","properties":{"template":{"enum":["general","tourism"]}},"required":["template"]}),
      "/api/files":("Upload a file up to 15 MB",{"type":"object","properties":{"name":{"type":"string"},"content_base64":{"type":"string","contentEncoding":"base64"}},"required":["name","content_base64"]}),
      "/api/mcp/discover":("Discover a configured MCP server's tools",{"type":"object","properties":{"server_id":{"type":"string"}},"required":["server_id"]}),
      "/api/records/{id}":("Update a register record using its skill input schema",object_schema),
      "/api/settings":("Save tourism autonomy controls",object_schema),
      "/api/review":("Review a tourism proposal",object_schema),
      "/api/simulate":("Prepare a synthetic tourism case",object_schema),
      "/api/event":("Record a tourism execution event",object_schema),
      "/api/reassign":("Reassign a tourism duty",object_schema),
      "/api/option":("Change a tourism quotation option",object_schema),
      "/api/agent":("Query a tourism role's case facts",object_schema),
    }
    for path,(summary,schema) in post.items(): route(path,"post",summary,schema)
    route("/api/files/{id}/download","get","Download an uploaded or generated file")
    paths["/api/files/{id}/download"]["get"]["responses"]["200"]={"description":"File bytes","content":{"application/octet-stream":{"schema":{"type":"string","format":"binary"}}}}
    return {"openapi":"3.1.0","info":{"title":"Atlas Company Workspace API","version":"3.0.0","description":"Local single-user API. Shared GUI, CLI and MCP execution. Remote writes prepare a pending run and require explicit review. Credentials remain in server-side private files."},"servers":[{"url":"/"}],"paths":paths}

def get(handler,url,data):
    rt=Runtime(data); path=url.path; query=parse_qs(url.query)
    result=None
    if path=="/api/health": result={"status":"ok","version":"3.0.0","skills":len(rt.catalog())}
    elif path=="/api/skills": result=rt.catalog()
    elif re.fullmatch(r"/api/skills/[\w-]+",path): result=rt.skill_detail(path.split("/")[-1])
    elif path=="/api/runs": result=rt.runs()
    elif re.fullmatch(r"/api/runs/[\w-]+",path): result=rt.run(path.split("/")[-1])
    elif path=="/api/files": result=rt.list_files()
    elif re.fullmatch(r"/api/files/[\w-]+/download",path):
        meta,file=rt.file(path.split("/")[-2]); raw=file.read_bytes()
        handler.send_response(200); handler.send_header("Content-Type","application/octet-stream")
        from urllib.parse import quote
        handler.send_header("Content-Disposition","attachment; filename*=UTF-8''"+quote(meta["name"]))
        handler.send_header("Content-Length",str(len(raw))); handler.send_header("X-Content-Type-Options","nosniff"); handler.end_headers(); handler.wfile.write(raw)
        return True
    elif path=="/api/records": result=rt.records(query.get("kind",[None])[0],query.get("q",[""])[0])
    elif path=="/api/audit": result=rt.audit_log()
    elif path=="/api/templates": result=[{"id":"general","name":"General company","description":"Sales, operations, finance, product, people and IT."},{"id":"tourism","name":"Chengdu tourism","description":"Original nine-stage synthetic tourism workflow, extended with office skills."}]
    elif path=="/api/connections":
        from telegram_service import status as telegram_status
        result={"google":GoogleWorkspace(data).status(),"telegram":telegram_status(),"mcp":Bridge(data).list()}
    elif path in ("/openapi.json","/api/openapi.json"): result=specification(rt)
    elif path=="/docs": handler.file(ROOT/"web"/"docs.html","text/html; charset=utf-8"); return True
    elif path in ("/workspace.js","/workspace.css","/docs.js"):
        handler.file(ROOT/"web"/path[1:],"text/css; charset=utf-8" if path.endswith("css") else "text/javascript; charset=utf-8"); return True
    elif re.fullmatch(r"/portraits/[a-z_]+\.png",path): handler.file(ROOT/"web"/path[1:],"image/png"); return True
    else: return False
    handler.respond(200,result); return True

def post(handler,path,body,data,load_company,save_company):
    rt=Runtime(data)
    if re.fullmatch(r"/api/skills/[\w-]+/run",path):
        if set(body)-{"inputs","person_id","idempotency_key"}: raise ValueError("Unknown run fields.")
        result=rt.submit(path.split("/")[-2],body.get("inputs"),body.get("person_id","atlas"),body.get("idempotency_key"))
    elif re.fullmatch(r"/api/runs/[\w-]+/(approve|reject)",path): result=(rt.approve if path.endswith("approve") else rt.reject)(path.split("/")[-2])
    elif path=="/api/files": result=rt.upload(body)
    elif path=="/api/mcp/discover": result=Bridge(data).discover(body.get("server_id"))
    elif re.fullmatch(r"/api/records/[\w-]+",path): result=rt.update_record(path.split("/")[-1],body)
    elif path=="/api/company/template":
        template=body.get("template")
        if template not in ("general","tourism"): raise ValueError("Choose a listed company template.")
        old=load_company(); rt.record("organization-backup",old["company"],old)
        name="company-general.json" if template=="general" else "company-tourism-template.json"
        result=json.loads((ROOT/"resources"/name).read_text(encoding="utf-8")); save_company(result)
    else: return False
    handler.respond(200,result); return True
