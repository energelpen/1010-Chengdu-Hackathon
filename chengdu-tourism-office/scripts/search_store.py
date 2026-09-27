"""Small local FTS5 case index. Indexing is explicit; searching is read-only."""
from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(path))
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS cases USING fts5(request_id UNINDEXED, searchable, payload UNINDEXED)")
    return db


def index_case(path: str | Path, case: dict) -> str:
    request_id = str(case["request"]["request_id"])
    text = " ".join(str(value) for value in (
        case["request"].get("message", ""),
        case["inquiry"]["data"].get("interests", []),
        case["comparison"]["data"]["recommended"].get("id", ""),
        case["outcome"]["data"].get("management_summary", ""),
        " ".join(day["date"] + " " + " ".join(item["title"] for item in day["activities"]) for day in case["schedule"]["data"]["days"]),
    ))
    with closing(connect(path)) as db:
        with db:
            db.execute("DELETE FROM cases WHERE request_id = ?", (request_id,))
            db.execute("INSERT INTO cases(request_id, searchable, payload) VALUES (?,?,?)",
                       (request_id, text, json.dumps(case, ensure_ascii=False)))
    return request_id


def search_cases(path: str | Path, query: str, limit: int = 10) -> list[dict]:
    terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    if not terms or limit < 1 or limit > 50: return []
    expression = " AND ".join(f'"{term}"' for term in terms)
    with closing(connect(path)) as db:
        rows = db.execute("SELECT request_id, snippet(cases, 1, '[', ']', '…', 15) FROM cases WHERE cases MATCH ? LIMIT ?",
                          (expression, limit)).fetchall()
    return [{"request_id": request_id, "snippet": snippet} for request_id, snippet in rows]
