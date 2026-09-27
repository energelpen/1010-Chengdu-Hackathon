"""Google Workspace OAuth and explicit API operations. Credentials never enter browser responses."""
from __future__ import annotations
import base64
import hashlib
import json
import os
import threading
from pathlib import Path

SCOPES = {
    "drive":["https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive.metadata.readonly"],
    "gmail":["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.compose"],
    "calendar":["https://www.googleapis.com/auth/calendar.events"],
    "sheets":["https://www.googleapis.com/auth/spreadsheets"],
    "docs":["https://www.googleapis.com/auth/documents"],
    "slides":["https://www.googleapis.com/auth/presentations"],
}
LOCK=threading.Lock()
class ProviderError(RuntimeError): pass
DEMO_RECIPIENT = "amonsk007@gmail.com"
class GoogleWorkspace:
    def __init__(self,data):
        self.data=Path(data)
        self.token=self.data/"private"/"google-token.json"
    def status(self):
        if not self.token.exists(): return {"id":"google","name":"Google Workspace","status":"not_connected","services":[],"message":"Connect selected services with scripts/google_connect.py."}
        try:
            payload=json.loads(self.token.read_text(encoding="utf-8"))
            scopes=set(payload.get("scopes",[]))
            services=[k for k,v in SCOPES.items() if set(v)<=scopes]
            return {"id":"google","name":"Google Workspace","status":"credentials_saved","services":services,"message":"OAuth credentials saved. Run a read skill to verify current account access."}
        except (ValueError,OSError): return {"id":"google","name":"Google Workspace","status":"needs_attention","services":[],"message":"Reconnect Google; the local credential file cannot be read."}
    def require_connection(self,skill_id):
        service=skill_id.split("-")[0]
        status=self.status()
        if service not in status["services"]:
            raise ValueError(f"Connect Google {service} first. Run scripts/google_connect.py with --services {service}; then refresh Connections.")
    def fingerprint(self):
        payload=json.loads(self.token.read_text(encoding="utf-8"))
        return hashlib.sha256((payload.get("client_id","")+"|"+payload.get("refresh_token",payload.get("token",""))).encode()).hexdigest()
    def credentials(self):
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        with LOCK:
            try:
                credentials=Credentials.from_authorized_user_file(str(self.token))
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    self.save(credentials.to_json())
                if not credentials.valid: raise ValueError()
                return credentials
            except Exception: raise ProviderError("Google authorization has expired or was revoked. Reconnect Google Workspace.")
    def save(self,content):
        self.token.parent.mkdir(parents=True,exist_ok=True)
        temp=self.token.with_suffix(".tmp")
        temp.write_text(content,encoding="utf-8")
        if os.name!="nt": temp.chmod(0o600)
        os.replace(temp,self.token)
    def execute(self,skill_id,p,rt,actor="atlas"):
        self.require_connection(skill_id)
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from business_tools import email_message,time_range
        from google_auth_httplib2 import AuthorizedHttp
        import httplib2
        service=skill_id.split("-")[0]; version="v3" if service in ("drive","calendar") else "v4" if service=="sheets" else "v1"
        api=build(service,version,http=AuthorizedHttp(self.credentials(),http=httplib2.Http(timeout=30)),cache_discovery=False)
        created=None
        def run(request): return request.execute(num_retries=0)
        try:
            if skill_id=="gmail-search":
                result=run(api.users().messages().list(userId="me",q=p["query"],maxResults=p["limit"]))
                messages=[]
                for m in result.get("messages",[]):
                    item=run(api.users().messages().get(userId="me",id=m["id"],format="metadata",metadataHeaders=["Subject","From","Date"]))
                    headers={h["name"].lower():h["value"] for h in item.get("payload",{}).get("headers",[])}
                    messages.append({"id":m["id"],"subject":headers.get("subject",""),"from":headers.get("from",""),"date":headers.get("date",""),"snippet":item.get("snippet","")})
                return {"summary":f"Retrieved {len(messages)} Gmail messages.","messages":messages,"next_page_token":result.get("nextPageToken")}
            if skill_id in ("gmail-draft","gmail-send"):
                if p["to"].strip().casefold()!=DEMO_RECIPIENT:
                    raise PermissionError("Demo email is restricted to "+DEMO_RECIPIENT+". Change the test policy only after deployment review.")
                from business_tools import roster
                colleague=next((x for x in roster(rt) if x["id"]==actor),None)
                sender_name=colleague["name"] if colleague else "Atlas"
                sender_role=colleague["role"] if colleague else "Company Assistant"
                signed={**p,"body":p["body"].rstrip()+"\n\n"+sender_name+"\n"+sender_role+" | Atlas Office"}
                raw=base64.urlsafe_b64encode(email_message(signed).as_bytes()).decode()
                req=api.users().drafts().create(userId="me",body={"message":{"raw":raw}}) if skill_id=="gmail-draft" else api.users().messages().send(userId="me",body={"raw":raw})
                result=run(req)
                return {"summary":"Message sent through Gmail." if skill_id=="gmail-send" else "Unsent draft saved in Gmail.","delivery":"sent" if skill_id=="gmail-send" else "draft","provider_result":result,"recipient":p["to"]}
            if skill_id=="drive-search":
                query=p["query"].replace("\\","\\\\").replace("'","\\'")
                return {"summary":"Google Drive search complete.",**run(api.files().list(q=f"trashed = false and name contains '{query}'",pageSize=p["limit"],fields="files(id,name,mimeType,webViewLink,modifiedTime),nextPageToken"))}
            if skill_id=="drive-upload":
                from googleapiclient.http import MediaFileUpload
                meta,path=rt.file(p["file_id"])
                result=run(api.files().create(body={"name":meta["name"],"parents":[p["folder_id"]]},media_body=MediaFileUpload(str(path),resumable=False),fields="id,name,webViewLink"))
                return {"summary":"File uploaded to Google Drive.","provider_result":result}
            if skill_id in ("calendar-list","calendar-create","calendar-invite"):
                time_range(p)
                if skill_id=="calendar-list": return {"summary":"Calendar events retrieved.",**run(api.events().list(calendarId="primary",timeMin=p["start"],timeMax=p["end"],singleEvents=True,orderBy="startTime",maxResults=100))}
                if skill_id=="calendar-invite":
                    if p["attendee"].strip().casefold()!=DEMO_RECIPIENT:
                        raise PermissionError("Demo invitations are restricted to "+DEMO_RECIPIENT+".")
                    body={"summary":p["title"],"description":p["description"],"start":{"dateTime":p["start"]},"end":{"dateTime":p["end"]},"attendees":[{"email":DEMO_RECIPIENT}]}
                    return {"summary":"Calendar event created and test invitation requested.","provider_result":run(api.events().insert(calendarId="primary",sendUpdates="all",body=body)),"attendee":DEMO_RECIPIENT}
                return {"summary":"Calendar event created without attendee invitations.","provider_result":run(api.events().insert(calendarId="primary",sendUpdates="none",body={"summary":p["title"],"description":p["description"],"start":{"dateTime":p["start"]},"end":{"dateTime":p["end"]}}))}
            if skill_id=="sheets-read": return {"summary":"Spreadsheet range retrieved.","data":run(api.spreadsheets().values().get(spreadsheetId=p["spreadsheet_id"],range=p["range"]))}
            if skill_id=="sheets-write": return {"summary":"Spreadsheet range updated.","provider_result":run(api.spreadsheets().values().update(spreadsheetId=p["spreadsheet_id"],range=p["range"],valueInputOption="RAW",body={"values":p["values"]}))}
            if skill_id=="sheets-create":
                created=run(api.spreadsheets().create(body={"properties":{"title":p["title"]}}))
                run(api.spreadsheets().values().update(spreadsheetId=created["spreadsheetId"],range="A1",valueInputOption="RAW",body={"values":p["values"]}))
                return {"summary":"Google spreadsheet created.","url":created["spreadsheetUrl"],"id":created["spreadsheetId"]}
            if skill_id=="docs-read": return {"summary":"Google document retrieved.","data":run(api.documents().get(documentId=p["document_id"]))}
            if skill_id=="docs-create":
                created=run(api.documents().create(body={"title":p["title"]}))
                run(api.documents().batchUpdate(documentId=created["documentId"],body={"requests":[{"insertText":{"location":{"index":1},"text":p["body"]}}]}))
                return {"summary":"Google document created.","id":created["documentId"],"url":"https://docs.google.com/document/d/"+created["documentId"]+"/edit"}
            if skill_id=="slides-create":
                created=run(api.presentations().create(body={"title":p["title"]}))
                requests=[]
                for i,slide in enumerate(p["slides"]):
                    page=f"atlas_page_{i}"; title=f"atlas_title_{i}"; body=f"atlas_body_{i}"
                    requests.append({"createSlide":{"objectId":page,"slideLayoutReference":{"predefinedLayout":"BLANK"}}})
                    for id,text,y,h,size in [(title,slide["title"],30,85,28),(body,"\n".join(slide["bullets"]),125,230,18)]:
                        requests.extend([{"createShape":{"objectId":id,"shapeType":"TEXT_BOX","elementProperties":{"pageObjectId":page,"size":{"width":{"magnitude":620,"unit":"PT"},"height":{"magnitude":h,"unit":"PT"}},"transform":{"scaleX":1,"scaleY":1,"translateX":45,"translateY":y,"unit":"PT"}}}},{"insertText":{"objectId":id,"text":text}},{"updateTextStyle":{"objectId":id,"textRange":{"type":"ALL"},"style":{"fontSize":{"magnitude":size,"unit":"PT"},"fontFamily":"Arial"},"fields":"fontSize,fontFamily"}}])
                if requests: run(api.presentations().batchUpdate(presentationId=created["presentationId"],body={"requests":requests}))
                return {"summary":"Google Slides presentation created.","id":created["presentationId"],"url":"https://docs.google.com/presentation/d/"+created["presentationId"]+"/edit"}
            raise ValueError("Unsupported Google operation.")
        except Exception as exc:
            if created:
                id=created.get("spreadsheetId",created.get("documentId",created.get("presentationId","unknown")))
                raise ProviderError(f"Google created file {id}, but its content update did not complete. Inspect that file before attempting another creation.") from None
            if isinstance(exc,(ValueError,FileNotFoundError,PermissionError)): raise
            code=getattr(getattr(exc,"resp",None),"status",None)
            raise ProviderError(f"Google request did not complete (HTTP {code or 'connection error'}). Check service enablement and account permissions. For a write, inspect the destination before creating another run.") from None
        finally: api.close()
