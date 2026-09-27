#!/usr/bin/env python3
"""CLI for the SP-D tourism-company agent skills and end-to-end simulation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tourism_core import HANDLERS, SKILLS, demo, run_case
from search_store import index_case, search_cases


def read_object(value: str) -> dict:
    raw = Path(value[1:]).read_text(encoding="utf-8") if value.startswith("@") else value
    obj = json.loads(raw)
    if not isinstance(obj, dict): raise ValueError("Input must be a JSON object.")
    return obj


def write_artifacts(case: dict, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    request_id = case["request"]["request_id"]
    json_path = output / f"{request_id}-trace.json"
    json_path.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")
    files = {"trace": str(json_path)}
    if "outcome" in case:
        from render_reports import render
        files.update(render(case, output))
        index_case(output / "cases.sqlite", case)
        files["search_index"] = str(output / "cases.sqlite")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo").add_argument("--out", default=str(ROOT / "output"))
    run = sub.add_parser("run")
    run.add_argument("skill", choices=SKILLS)
    run.add_argument("json", nargs="?", help="JSON object or @path; stdin if omitted")
    case = sub.add_parser("case")
    case.add_argument("json", help="JSON request object or @path")
    case.add_argument("--out", default=str(ROOT / "output"))
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--db", default=str(ROOT / "output" / "cases.sqlite"))
    test = sub.add_parser("test")
    test.add_argument("skill", nargs="?", choices=SKILLS)
    args = parser.parse_args()
    if args.command == "demo":
        result = demo()
        print(json.dumps({"files": write_artifacts(result, Path(args.out)), "statuses": {k: v["status"] for k, v in result.items() if isinstance(v, dict) and "status" in v}}, indent=2))
    elif args.command == "run":
        raw = args.json if args.json is not None else sys.stdin.read()
        print(json.dumps(HANDLERS[args.skill](read_object(raw)), indent=2, ensure_ascii=False))
    elif args.command == "case":
        result = run_case(read_object(args.json))
        print(json.dumps({"files": write_artifacts(result, Path(args.out)), "outcome": result.get("outcome", {}).get("data", {}).get("decision")}, indent=2))
    elif args.command == "search":
        print(json.dumps(search_cases(args.db, args.query), indent=2, ensure_ascii=False))
    else:
        sys.path.insert(0, str(ROOT))
        from tests.test_skills import run_tests
        run_tests(args.skill)


if __name__ == "__main__":
    main()
