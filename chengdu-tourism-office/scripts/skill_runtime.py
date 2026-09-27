"""One validated, auditable execution path for GUI, REST, CLI and MCP skills."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-zA-Z0-9_-]{1,90}$")
ALLOWED_FILES = {".csv", ".xlsx", ".docx", ".pptx", ".pdf", ".txt", ".md", ".json", ".eml", ".ics"}
def now(): return datetime.now(timezone.utc).isoformat()
def data_dir(): return Path(os.environ.get("ATLAS_DATA_DIR", str(ROOT/"output")))
def check_id(value):
    if not isinstance(value,str) or not ID.fullmatch(value): raise ValueError("Invalid item ID.")
    return value
def validate(schema, value):
    errors=sorted(Draft202012Validator(schema).iter_errors(value),key=lambda e:str(e.path))
    if errors:
        error=errors[0]
        raise ValueError(f"{' / '.join(map(str,error.path)) or 'Input'}: {error.message[:400]}")
    # JSON parsers can accept non-finite floats, but they are not valid business data.
    try: json.dumps(value,allow_nan=False)
    except (ValueError,TypeError): raise ValueError("Use finite JSON values.")

class Runtime:
    def __init__(self, data=None):
        self.data=Path(data) if data is not None else data_dir()
        self.data.mkdir(parents=True,exist_ok=True)
        self.files=self.data/"files"
        self.files.mkdir(exist_ok=True)
        with self.db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS skill_runs(id TEXT PRIMARY KEY,skill_id TEXT,person_id TEXT,status TEXT,input TEXT,output TEXT,created_at TEXT,updated_at TEXT,idempotency_key TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY,name TEXT,stored TEXT,size INTEGER,created_at TEXT);
            CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,kind TEXT,title TEXT,payload TEXT,created_at TEXT,updated_at TEXT);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,event TEXT,item_id TEXT,details TEXT,created_at TEXT);
            ''')
        if self.data.resolve() == (ROOT / "output").resolve():
            self.seed_demo_file()

    def seed_demo_file(self):
        demo = ROOT / "outputs" / "atlas-finance-demo" / "monthly-finance-demo.xlsx"
        if not demo.is_file(): return
        with self.db() as db:
            existing = db.execute("SELECT id FROM files WHERE name=? LIMIT 1", (demo.name,)).fetchone()
        if not existing: self.add_file(demo.name, demo.read_bytes())
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.data/"workspace.sqlite",timeout=20)
        db.row_factory=sqlite3.Row
        try:
            with db: yield db
        finally: db.close()
    def audit(self,event,item_id,details):
        with self.db() as db: db.execute("INSERT INTO audit(event,item_id,details,created_at) VALUES(?,?,?,?)",(event,item_id,json.dumps(details),now()))
    def catalog(self):
        result=[]
        for folder in sorted((ROOT/"skills").iterdir()):
            manifest=folder/"skill.json"
            if manifest.exists():
                skill=json.loads(manifest.read_text(encoding="utf-8"))
                skill["instructions_path"]=f"skills/{folder.name}/SKILL.md"
                skill["script_path"]=f"skills/{folder.name}/scripts/run.py"
                result.append(skill)
        return result
    def skill(self,id):
        check_id(id)
        path=ROOT/"skills"/id/"skill.json"
        if not path.is_file(): raise FileNotFoundError("Skill not found.")
        return json.loads(path.read_text(encoding="utf-8"))
    def skill_detail(self,id):
        skill=self.skill(id)
        skill["instructions"]=(ROOT/"skills"/id/"SKILL.md").read_text(encoding="utf-8")
        return skill
    def file(self,id):
        check_id(id)
        with self.db() as db: row=db.execute("SELECT * FROM files WHERE id=?",(id,)).fetchone()
        if row is None: raise FileNotFoundError("Workspace file not found.")
        result=dict(row)
        path=(self.files/result["stored"]).resolve()
        if not path.is_relative_to(self.files.resolve()) or not path.is_file(): raise FileNotFoundError("Workspace file is unavailable.")
        return result,path
    def list_files(self):
        with self.db() as db: return [dict(r) for r in db.execute("SELECT id,name,size,created_at FROM files ORDER BY created_at DESC LIMIT 300")]
    def add_file(self,name,content):
        name=Path(name.replace("\\","/")).name
        ext=Path(name).suffix.lower()
        if ext not in ALLOWED_FILES: raise ValueError("Supported files: "+", ".join(sorted(ALLOWED_FILES)))
        if len(content)>15_000_000: raise ValueError("Files must be under 15 MB.")
        id="file_"+uuid.uuid4().hex
        stored=id+ext
        (self.files/stored).write_bytes(content)
        with self.db() as db: db.execute("INSERT INTO files VALUES(?,?,?,?,?)",(id,name[:200],stored,len(content),now()))
        return {"id":id,"name":name[:200],"size":len(content),"url":"/api/files/"+id+"/download"}
    def upload(self,body):
        if not isinstance(body.get("name"),str) or not isinstance(body.get("content_base64"),str): raise ValueError("Provide name and content_base64.")
        try: raw=base64.b64decode(body["content_base64"],validate=True)
        except Exception: raise ValueError("Invalid base64 file content.")
        result=self.add_file(body["name"],raw)
        self.audit("file.uploaded",result["id"],{"name":result["name"]})
        return result
    def record(self,kind,title,payload,id=None):
        id=id or "rec_"+uuid.uuid4().hex
        check_id(id)
        with self.db() as db:
            old=db.execute("SELECT * FROM records WHERE id=?",(id,)).fetchone()
            created=old["created_at"] if old else now()
            db.execute("INSERT OR REPLACE INTO records VALUES(?,?,?,?,?,?)",(id,kind,title,json.dumps(payload,ensure_ascii=False),created,now()))
        self.audit("record.saved",id,{"kind":kind})
        return {"id":id,"kind":kind,"title":title,"payload":payload}
    def records(self,kind=None,query=""):
        with self.db() as db: result=[dict(r) for r in db.execute("SELECT * FROM records ORDER BY updated_at DESC LIMIT 1000")]
        return [{**r,"payload":json.loads(r["payload"])} for r in result if (not kind or r["kind"]==kind) and all(t in (r["title"]+r["payload"]).lower() for t in query.lower().split())]
    def update_record(self,id,body):
        check_id(id)
        with self.db() as db: old=db.execute("SELECT * FROM records WHERE id=?",(id,)).fetchone()
        if not old: raise FileNotFoundError("Record not found.")
        skill=self.skill(old["kind"])
        validate(skill["input_schema"],body)
        return self.record(old["kind"],body.get("title",old["title"]),body,id)
    def runs(self):
        with self.db() as db: ids=[r[0] for r in db.execute("SELECT id FROM skill_runs ORDER BY created_at DESC LIMIT 200")]
        return [self.run(id) for id in ids]
    def run(self,id):
        check_id(id)
        with self.db() as db: row=db.execute("SELECT * FROM skill_runs WHERE id=?",(id,)).fetchone()
        if row is None: raise FileNotFoundError("Run not found.")
        r=dict(row)
        for key in ("input","output"): r[key]=json.loads(r[key]) if r[key] else None
        return r
    def submit(self,skill_id,payload,person_id="atlas",idempotency_key=None):
        skill=self.skill(skill_id)
        validate(skill["input_schema"],payload)
        check_id(person_id)
        if person_id!="atlas":
            company=json.loads((self.data/"company.json").read_text(encoding="utf-8")) if (self.data/"company.json").exists() else json.loads((ROOT/"resources"/"company-general.json").read_text(encoding="utf-8"))
            person=next((p for p in company["people"] if p["id"]==person_id),None)
            if not person or not person.get("available"): raise ValueError("Choose an available colleague.")
            if skill_id not in person.get("skills",[]): raise PermissionError("This skill is not assigned to the selected colleague. Edit their skills or use Atlas.")
        if idempotency_key:
            check_id(idempotency_key)
            with self.db() as db: old=db.execute("SELECT id FROM skill_runs WHERE idempotency_key=?",(idempotency_key,)).fetchone()
            if old:
                result=self.run(old["id"])
                if result["skill_id"]!=skill_id or result["input"]!=payload or result["person_id"]!=person_id: raise ValueError("Idempotency key already belongs to a different request.")
                return result
        preparation = None
        if skill.get("connector")=="google":
            from google_workspace import GoogleWorkspace
            google = GoogleWorkspace(self.data)
            google.require_connection(skill_id)
            preparation = {"connection_fingerprint": google.fingerprint()}
        if skill["handler"]=="mcp":
            from mcp_bridge import Bridge
            bridge = Bridge(self.data)
            server = bridge.validate_call(payload)
            preparation = {"connection_fingerprint": bridge.fingerprint(server)}
        id="run_"+uuid.uuid4().hex
        status="awaiting_approval" if skill["effect"] in ("remote_write", "reviewed_write") else "queued"
        try:
            with self.db() as db: db.execute("INSERT INTO skill_runs VALUES(?,?,?,?,?,?,?,?,?)",(id,skill_id,person_id,status,json.dumps(payload,ensure_ascii=False),json.dumps(preparation) if preparation else None,now(),now(),idempotency_key))
        except sqlite3.IntegrityError:
            if idempotency_key: return self.submit(skill_id,payload,person_id,idempotency_key)
            raise
        self.audit("skill.prepared",id,{"skill_id":skill_id,"status":status})
        return self.run(id) if status=="awaiting_approval" else self._execute(id,"queued")
    def approve(self,id): return self._execute(id,"awaiting_approval")
    def reject(self,id):
        with self.db() as db:
            changed=db.execute("UPDATE skill_runs SET status='cancelled',updated_at=? WHERE id=? AND status='awaiting_approval'",(now(),check_id(id))).rowcount
        if not changed: raise ValueError("Only a pending run can be cancelled.")
        self.audit("skill.cancelled",id,{})
        return self.run(id)
    def _execute(self,id,expected):
        run=self.run(id)
        if run["status"]=="completed": return run
        with self.db() as db:
            changed=db.execute("UPDATE skill_runs SET status='running',updated_at=? WHERE id=? AND status=?",(now(),id,expected)).rowcount
        if not changed: raise ValueError("This run is already executing or is no longer actionable. Inspect its recorded status.")
        self.audit("skill.executing",id,{"reviewed":expected=="awaiting_approval"})
        skill=self.skill(run["skill_id"])
        try:
            if skill.get("connector") == "google":
                from google_workspace import GoogleWorkspace
                if (run["output"] or {}).get("connection_fingerprint") != GoogleWorkspace(self.data).fingerprint():
                    raise ValueError("The Google account connection changed after this run was prepared. Prepare a new run for the current account.")
            if skill["handler"] == "mcp":
                from mcp_bridge import Bridge
                bridge = Bridge(self.data)
                server = bridge.server(run["input"]["server_id"])
                if (run["output"] or {}).get("connection_fingerprint") != bridge.fingerprint(server):
                    raise ValueError("Connection configuration changed after this run was prepared. Discover tools and prepare a new run.")
            from business_tools import execute
            output=execute(self,skill,run["input"],actor=run["person_id"])
            status="completed"
        except Exception as exc:
            # Never leak credentials or raw provider responses through the API.
            from google_workspace import ProviderError
            output={"error":str(exc)[:500] if isinstance(exc,(ValueError,FileNotFoundError,PermissionError,ProviderError)) else "The skill failed. Check its inputs and server configuration."}
            status="needs_attention" if skill["effect"] in ("remote_write", "reviewed_write") else "failed"
        with self.db() as db: db.execute("UPDATE skill_runs SET status=?,output=?,updated_at=? WHERE id=?",(status,json.dumps(output,ensure_ascii=False,allow_nan=False),now(),id))
        self.audit("skill."+status,id,{"skill_id":skill["id"]})
        return self.run(id)
    def audit_log(self):
        with self.db() as db: return [dict(r) for r in db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 300")]

def cli(skill_id):
    parser=argparse.ArgumentParser(description="Run a registered company skill")
    parser.add_argument("--input",required=True,help="Path to JSON input, or - for stdin")
    parser.add_argument("--data-dir")
    args=parser.parse_args()
    import sys
    try:
        payload=json.loads(sys.stdin.read() if args.input=="-" else Path(args.input).read_text(encoding="utf-8-sig"))
        result=Runtime(args.data_dir).submit(skill_id,payload)
        print(json.dumps(result,indent=2,ensure_ascii=False))
        if result["status"] in ("failed","needs_attention"): sys.exit(1)
    except Exception as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        sys.exit(1)
