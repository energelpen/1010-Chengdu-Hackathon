"""Configured stdio and Streamable HTTP MCP connections with explicit tool allowlists."""
from __future__ import annotations
import asyncio
import hashlib
import json
import os
import re
from contextlib import AsyncExitStack
from pathlib import Path
from urllib.parse import urlparse
from skill_runtime import ROOT,check_id,validate

class Bridge:
    def __init__(self,data): self.data=Path(data); self.path=ROOT/"config"/"mcp-servers.json"
    def configuration(self):
        path=Path(os.environ.get("ATLAS_MCP_CONFIG",str(self.path)))
        value=json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"servers":[]}
        return value.get("servers",[])
    def list(self):
        return [{"id":s["id"],"name":s.get("name",s["id"]),"transport":s.get("transport","stdio"),"enabled":bool(s.get("enabled")),"allowed_tools":s.get("allowed_tools",[]),"status":"configured" if s.get("enabled") else "disabled"} for s in self.configuration()]
    def server(self,id):
        check_id(id)
        s=next((s for s in self.configuration() if s["id"]==id),None)
        if not s or not s.get("enabled"): raise ValueError("Enable this MCP connection in config/mcp-servers.json first.")
        return s
    def fingerprint(self,s): return hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()
    async def _request(self,s,name=None,arguments=None):
        from mcp import Client,StdioServerParameters
        async with AsyncExitStack() as stack:
            if s.get("transport")=="http":
                from mcp.client.streamable_http import streamable_http_client
                import httpx2
                url=s.get("url",""); parsed=urlparse(url)
                if parsed.username or parsed.password or parsed.query or parsed.fragment: raise ValueError("MCP URL must not contain credentials, query strings or fragments.")
                if parsed.scheme!="https" and not(parsed.scheme=="http" and parsed.hostname in ("127.0.0.1","localhost")): raise ValueError("Use HTTPS for remote MCP servers, or HTTP on localhost.")
                env=s.get("token_env"); headers={}
                if env:
                    token=os.environ.get(env)
                    if not token: raise ValueError("Set the server's token environment variable first.")
                    headers["Authorization"]="Bearer "+token
                http=await stack.enter_async_context(httpx2.AsyncClient(headers=headers,timeout=30,follow_redirects=False))
                transport=streamable_http_client(url,http_client=http)
            else:
                command=s.get("command","").replace("${PYTHON}",os.sys.executable)
                args=[x.replace("${ROOT}",str(ROOT)) for x in s.get("args",[])]
                env={key:os.environ[key] for key in s.get("env_keys",[]) if key in os.environ}
                env["ATLAS_DATA_DIR"]=str(self.data.resolve())
                transport=StdioServerParameters(command=command,args=args,env=env,cwd=str(ROOT))
            async with Client(transport,read_timeout_seconds=30) as client:
                if name is None:
                    result=await client.list_tools(); return result.model_dump(mode="json",by_alias=True)
                result=await client.call_tool(name,arguments=arguments)
                if result.is_error: raise ValueError("The MCP tool reported an error. Inspect the server before preparing another call.")
                return result.model_dump(mode="json",by_alias=True)
    def discover(self,id):
        s=self.server(id)
        try: result=asyncio.run(asyncio.wait_for(self._request(s),timeout=45))
        except ValueError: raise
        except Exception: raise ValueError("MCP discovery failed. Check its executable or URL, credentials and server logs.") from None
        tools=result.get("tools",[])
        (self.data/"mcp-cache").mkdir(exist_ok=True)
        (self.data/"mcp-cache"/(id+".json")).write_text(json.dumps({"fingerprint":self.fingerprint(s),"tools":tools}),encoding="utf-8")
        return {"server_id":id,"tools":tools,"allowed_tools":s.get("allowed_tools",[])}
    def validate_call(self,p):
        s=self.server(p["server_id"])
        if p["tool"] not in s.get("allowed_tools",[]): raise PermissionError("This tool is not in the server's allowed_tools list.")
        cache=self.data/"mcp-cache"/(p["server_id"]+".json")
        if not cache.exists(): raise ValueError("Discover this server's tools before preparing a call.")
        saved=json.loads(cache.read_text(encoding="utf-8"))
        if saved["fingerprint"]!=self.fingerprint(s): raise ValueError("MCP configuration changed. Discover tools again and prepare a new run.")
        tool=next((t for t in saved["tools"] if t["name"]==p["tool"]),None)
        if tool is None: raise ValueError("This tool was not found during discovery.")
        validate(tool.get("inputSchema",{}),p["arguments"])
        return s
    def call(self,p):
        s=self.validate_call(p)
        try: result=asyncio.run(asyncio.wait_for(self._request(s,p["tool"],p["arguments"]),timeout=45))
        except ValueError: raise
        except Exception: raise ValueError("MCP execution did not confirm a result. Inspect the destination before preparing another run.") from None
        return {"summary":"MCP tool completed.","server_id":p["server_id"],"tool":p["tool"],"result":result}
