"""A reviewed boss notification after a recorded, completed skill run."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen

def _setting(name):
    value=os.environ.get(name,"").strip()
    if value: return value
    path=Path(__file__).resolve().parents[1]/".env"
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if re.match(r"^\s*"+re.escape(name)+r"\s*=",line):
                return line.split("=",1)[1].strip().strip("\"'")
    return ""

def status():
    return {"id":"telegram","name":"Telegram boss updates",
            "status":"configured" if _setting("TELEGRAM_BOT_TOKEN") and _setting("TELEGRAM_BOSS_CHAT_ID") else "not_connected",
            "message":"Add TELEGRAM_BOT_TOKEN and TELEGRAM_BOSS_CHAT_ID to .env; approved notifications require a completed run."}

def notify(rt,payload,actor):
    run=rt.run(payload["run_id"])
    if run["status"]!="completed":
        raise ValueError("The referenced task has not completed. Check Activity before notifying the boss.")
    token=_setting("TELEGRAM_BOT_TOKEN")
    chat_id=_setting("TELEGRAM_BOSS_CHAT_ID")
    if not token or not chat_id:
        raise ValueError("Telegram is not configured. Add the bot token and boss chat ID to .env.")
    if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]{20,}",token) or not re.fullmatch(r"-?[0-9]{5,20}",chat_id):
        raise ValueError("Telegram configuration has an invalid format.")
    from business_tools import roster
    person=next((x for x in roster(rt) if x["id"]==actor),None)
    name=person["name"] if person else "Atlas"
    detail=(run["output"] or {}).get("summary",run["skill_id"]+" completed")
    text=f"Atlas Office task completed\nAgent: {name}\nSkill: {run['skill_id']}\nRun: {run['id']}\nOutcome: {str(detail)[:800]}"
    if payload["note"].strip(): text+="\nNote: "+payload["note"].strip()[:500]
    body=json.dumps({"chat_id":chat_id,"text":text},ensure_ascii=False).encode("utf-8")
    request=Request("https://api.telegram.org/bot"+token+"/sendMessage",data=body,headers={"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(request,timeout=15) as response:
            result=json.loads(response.read(100_000))
    except Exception:
        raise ValueError("Telegram did not confirm delivery. Check the bot and boss chat before retrying.") from None
    if not result.get("ok"):
        raise ValueError("Telegram did not confirm delivery. Check the bot and boss chat before retrying.")
    return {"summary":"Boss notification sent via Telegram for a completed task.",
            "delivery":"sent","telegram_message_id":result.get("result",{}).get("message_id"),"run_id":run["id"]}
