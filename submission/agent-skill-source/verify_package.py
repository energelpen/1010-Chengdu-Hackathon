"""Verify an extracted Atlas source supplement without third-party dependencies."""
from pathlib import Path
import hashlib
import json
import sys


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "FILE_MANIFEST.json").read_text(encoding="utf-8"))
    failures = []
    seen = set()
    for entry in manifest["files"]:
        name = entry["path"]
        path = (root / name).resolve()
        if name in seen or not path.is_relative_to(root) or not path.is_file():
            failures.append(f"Missing, duplicate or invalid path: {name}")
            continue
        seen.add(name)
        content = path.read_bytes()
        if len(content) != entry["bytes"] or hashlib.sha256(content).hexdigest() != entry["sha256"]:
            failures.append(f"Size/hash mismatch: {name}")

    skills = root / "chengdu-tourism-office" / "skills"
    manifests = sorted(skills.glob("*/skill.json"))
    if len(manifests) != 69:
        failures.append(f"Expected 69 skill manifests, found {len(manifests)}")
    ids = set()
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        sid = data.get("id")
        if sid != path.parent.name or sid in ids:
            failures.append(f"Invalid/duplicate skill identity: {path.parent.name}")
        ids.add(sid)
        for rel in ("SKILL.md", "scripts/run.py"):
            if not (path.parent / rel).is_file():
                failures.append(f"Missing skill source: {path.parent.name}/{rel}")
    top = root / "chengdu-tourism-office" / "SKILL.md"
    if not top.is_file():
        failures.append("Missing original top-level SKILL.md")

    evidence = json.loads((root / "submission/evidence/launch-execution.json").read_text(encoding="utf-8"))
    runs = evidence["runs"]
    actual = (len(runs), len({r["skill_id"] for r in runs}),
              len({r["person_id"] for r in runs}), len(evidence["artifacts"]))
    if actual != (20, 16, 7, 10) or any(r["status"] != "completed" for r in runs):
        failures.append(f"Recorded execution count/status mismatch: {actual}")
    if failures:
        print("VERIFICATION FAILED\n" + "\n".join(failures))
        return 1
    print(f"PASS: {len(manifest['files'])} packaged file hashes match.")
    print("PASS: 69 original skill instruction files, 69 manifests, 69 runners, plus top-level SKILL.md.")
    print("PASS: recorded evidence has 20 completed runs, 16 distinct skills, 7 fictional colleagues, 10 files.")
    print("No dependencies installed, external services contacted or live agent calls made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
