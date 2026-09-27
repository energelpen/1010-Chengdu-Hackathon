"""Durable, local conversation history for the company assistant."""
from __future__ import annotations

import json
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

VALID_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def check_id(value: str) -> str:
    if not isinstance(value, str) or not VALID_ID.fullmatch(value):
        raise ValueError("Invalid conversation ID.")
    return value


class ConversationStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    person_id TEXT NOT NULL, request_id TEXT, proposal TEXT,
                    work_plan TEXT, agent_run TEXT
                );
                CREATE TABLE IF NOT EXISTS messages (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT UNIQUE NOT NULL, conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL, content TEXT NOT NULL,
                    person_id TEXT, name TEXT NOT NULL, mode TEXT NOT NULL,
                    created_at TEXT NOT NULL, request_id TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                );
                CREATE INDEX IF NOT EXISTS messages_by_conversation
                    ON messages(conversation_id, sequence);
                CREATE TABLE IF NOT EXISTS imported_cases (request_id TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS conversation_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    person_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                );
                CREATE INDEX IF NOT EXISTS events_by_conversation
                    ON conversation_events(conversation_id, sequence);
            """)
            if "proposal" not in {row[1] for row in db.execute("PRAGMA table_info(conversations)")}:
                db.execute("ALTER TABLE conversations ADD COLUMN proposal TEXT")
            if "work_plan" not in {row[1] for row in db.execute("PRAGMA table_info(conversations)")}:
                db.execute("ALTER TABLE conversations ADD COLUMN work_plan TEXT")
            if "agent_run" not in {row[1] for row in db.execute("PRAGMA table_info(conversations)")}:
                db.execute("ALTER TABLE conversations ADD COLUMN agent_run TEXT")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def append_event(self, conversation_id: str, person_id: str, stage: str, detail: str) -> None:
        check_id(conversation_id)
        with closing(self._connect()) as db, db:
            db.execute("INSERT INTO conversation_events(conversation_id,person_id,stage,detail,created_at) VALUES(?,?,?,?,?)",
                       (conversation_id, person_id[:64], stage[:40], detail[:500], utc_now()))

    def events(self, conversation_id: str) -> list[dict]:
        check_id(conversation_id)
        with closing(self._connect()) as db:
            return [dict(row) for row in db.execute(
                "SELECT sequence,person_id,stage,detail,created_at FROM conversation_events WHERE conversation_id=? ORDER BY sequence LIMIT 300",
                (conversation_id,))]

    def create(self, title: str, person_id: str = "atlas") -> dict:
        now = utc_now()
        cid = "CHAT-" + uuid.uuid4().hex
        with closing(self._connect()) as db, db:
            db.execute("INSERT INTO conversations (id, title, created_at, updated_at, person_id, request_id) VALUES (?, ?, ?, ?, ?, NULL)",
                       (cid, " ".join(title.split())[:100] or "New conversation", now, now, person_id))
        return self.get(cid)

    def get(self, conversation_id: str) -> dict:
        check_id(conversation_id)
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
            if row is None:
                raise FileNotFoundError("Conversation not found.")
            result = dict(row)
            result["proposal"] = json.loads(result["proposal"]) if result.get("proposal") else None
            result["work_plan"] = json.loads(result["work_plan"]) if result.get("work_plan") else None
            result["agent_run"] = json.loads(result["agent_run"]) if result.get("agent_run") else None
            result["messages"] = [dict(message) for message in db.execute(
                "SELECT id, role, content, person_id, name, mode, created_at, request_id "
                "FROM messages WHERE conversation_id=? ORDER BY sequence", (conversation_id,))]
        return result

    def list(self) -> list[dict]:
        with closing(self._connect()) as db:
            return [dict(row) for row in db.execute("""
                SELECT c.id, c.title, c.updated_at, c.person_id, c.request_id,
                    COALESCE((SELECT substr(m.content, 1, 180) FROM messages m
                              WHERE m.conversation_id=c.id ORDER BY m.sequence DESC LIMIT 1), '') AS preview
                FROM conversations c ORDER BY c.updated_at DESC, c.id
            """)]

    def for_case(self, request_id: str) -> list[dict]:
        check_id(request_id)
        with closing(self._connect()) as db:
            rows = db.execute("SELECT id FROM conversations WHERE request_id=? AND proposal IS NOT NULL",
                              (request_id,)).fetchall()
        return [self.get(row["id"]) for row in rows]

    def append(self, conversation_id: str, role: str, content: str, *,
               person_id: str | None = None, name: str = "You", mode: str = "local",
               request_id: str | None = None) -> dict:
        check_id(conversation_id)
        if role not in ("user", "assistant") or not isinstance(content, str) or not content.strip():
            raise ValueError("A message needs a supported role and nonempty text.")
        now = utc_now()
        with closing(self._connect()) as db, db:
            if db.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone() is None:
                raise FileNotFoundError("Conversation not found.")
            db.execute("""INSERT INTO messages
                (id, conversation_id, role, content, person_id, name, mode, created_at, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uuid.uuid4().hex, conversation_id, role, content, person_id, name, mode, now, request_id))
            db.execute("""UPDATE conversations SET updated_at=?,
                person_id=COALESCE(?, person_id), request_id=COALESCE(?, request_id) WHERE id=?""",
                (now, person_id if role == "assistant" else None, request_id, conversation_id))
        return self.get(conversation_id)

    def link_case(self, conversation_id: str, request_id: str) -> None:
        check_id(conversation_id)
        check_id(request_id)
        with closing(self._connect()) as db, db:
            db.execute("UPDATE conversations SET request_id=?, updated_at=? WHERE id=?",
                       (request_id, utc_now(), conversation_id))
            db.execute("INSERT OR IGNORE INTO imported_cases VALUES (?)", (request_id,))

    def save_proposal(self, conversation_id: str, proposal: dict) -> None:
        check_id(conversation_id)
        with closing(self._connect()) as db, db:
            db.execute("UPDATE conversations SET proposal=?, updated_at=? WHERE id=?",
                       (json.dumps(proposal, ensure_ascii=False), utc_now(), conversation_id))

    def save_work_plan(self, conversation_id: str, plan: dict) -> None:
        check_id(conversation_id)
        with closing(self._connect()) as db, db:
            if db.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone() is None:
                raise FileNotFoundError("Conversation not found.")
            db.execute("UPDATE conversations SET work_plan=?, updated_at=? WHERE id=?",
                       (json.dumps(plan, ensure_ascii=False), utc_now(), conversation_id))

    def save_agent_run(self, conversation_id: str, run: dict) -> None:
        """Persist the latest actual agent execution snapshot for polling and reopening."""
        check_id(conversation_id)
        with closing(self._connect()) as db, db:
            if db.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone() is None:
                raise FileNotFoundError("Conversation not found.")
            db.execute("UPDATE conversations SET agent_run=?, updated_at=? WHERE id=?",
                       (json.dumps(run, ensure_ascii=False), utc_now(), conversation_id))

    def import_cases(self, folder: Path) -> None:
        """Import saved simulations once, including traces made by the legacy UI."""
        with closing(self._connect()) as db:
            known = {row[0] for row in db.execute("SELECT request_id FROM imported_cases")}
        for path in sorted(folder.glob("*-trace.json")):
            if path.name.removesuffix("-trace.json") in known:
                continue
            try:
                case = json.loads(path.read_text(encoding="utf-8"))
                request = case["request"]
                rid = check_id(request["request_id"])
                message = str(request["message"])
                stamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
                # The import marker and full conversation are committed together.
                with closing(self._connect()) as db, db:
                    inserted = db.execute("INSERT OR IGNORE INTO imported_cases VALUES (?)", (rid,)).rowcount
                    if not inserted:
                        continue
                    if db.execute("SELECT id FROM conversations WHERE request_id=?", (rid,)).fetchone():
                        continue
                    cid = "CHAT-" + uuid.uuid4().hex
                    db.execute("INSERT INTO conversations (id, title, created_at, updated_at, person_id, request_id) VALUES (?, ?, ?, ?, 'atlas', ?)",
                               (cid, " ".join(message.split())[:100], stamp, stamp, rid))
                    quote = case.get("selected_option", {}).get("quote_cny")
                    content = "This saved company workflow is ready to reopen."
                    if isinstance(quote, (int, float)):
                        content += f" The indicative group quote is CNY {quote:,.0f}."
                    content += " Open the linked case to review the team, itinerary, tasks and reports. Prices and execution are simulated."
                    for role, text, person, name in (("user", message, None, "You"),
                                                     ("assistant", content, "atlas", "Atlas")):
                        db.execute("""INSERT INTO messages
                            (id, conversation_id, role, content, person_id, name, mode, created_at, request_id)
                            VALUES (?, ?, ?, ?, ?, ?, 'local', ?, ?)""",
                            (uuid.uuid4().hex, cid, role, text, person, name, stamp, rid))
            except (OSError, ValueError, KeyError, TypeError):
                # One damaged legacy trace must not hide the rest of the history.
                continue
