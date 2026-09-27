"""Company workspace MCP server. Run with Python; transport is stdio."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mcp.server import MCPServer
from skill_runtime import Runtime

server=MCPServer("atlas-company-workspace")
@server.tool()
def list_skills(category: str="") -> list[dict]:
    """Discover company skill names, capabilities, effects and input schemas."""
    return [s for s in Runtime().catalog() if not category or s["category"]==category]
@server.tool()
def read_skill(skill_id: str) -> dict:
    """Read a skill's SKILL.md instructions, input schema and runnable example."""
    return Runtime().skill_detail(skill_id)
@server.tool()
def run_skill(skill_id: str, arguments: dict, person_id: str="atlas", idempotency_key: str|None=None) -> dict:
    """Run local work or prepare an external action for review in the GUI. This cannot approve external writes."""
    return Runtime().submit(skill_id,arguments,person_id,idempotency_key)
@server.tool()
def list_runs() -> list[dict]:
    """Inspect recorded skill runs and their actual results."""
    return Runtime().runs()
@server.tool()
def list_files() -> list[dict]:
    """List uploaded and generated workspace files and their IDs."""
    return Runtime().list_files()
@server.tool()
def search_knowledge(query: str) -> list[dict]:
    """Search saved company notes, with their sources."""
    return Runtime().records("knowledge-save",query)
@server.tool()
def get_company() -> dict:
    """Read the current editable organization and each colleague's assigned skills."""
    import json
    rt=Runtime(); path=rt.data/"company.json"
    return json.loads((path if path.exists() else ROOT/"resources"/"company-general.json").read_text(encoding="utf-8"))

if __name__=="__main__": server.run()
