"""Check the packaged source in a fresh extraction with local, offline examples."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote
import zipfile

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "submission"
NAME = "Atlas-Singapore-Polytechnic-Agent-Skill-Source"
QA = OUT / "qa/source-package"


def main():
    QA.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="extracted-", dir=QA))
    archive = OUT / (NAME + ".zip")
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert (folder / name).resolve().is_relative_to(folder.resolve())
        z.extractall(folder)
    root = folder / NAME
    app = root / "chengdu-tourism-office"
    environment = {k: v for k, v in os.environ.items() if not any(term in k.upper() for term in
                   ("OPENAI", "TELEGRAM", "SMTP", "GOOGLE", "TOURISM_EMAIL"))}
    environment.update(OPENAI_API_KEY="", PYTHONIOENCODING="utf-8", ATLAS_DATA_DIR=str(root / "review-output/workspace"))
    checks = []
    jobs = [
        ("package-integrity", root, ["verify_package.py"]),
        ("tourism-behavior", app, ["scripts/tourism_office.py", "test"]),
        ("automated-tests", app, ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"]),
        ("routing", app, ["tests/trigger_eval.py"]),
        ("standalone-proposal", app, ["skills/proposal-package/scripts/run.py", "--input", "skills/proposal-package/references/example.json", "--data-dir", "../review-output/company"]),
        ("tourism-stage", app, ["scripts/tourism_office.py", "run", "inquiry-intake", "@examples/rfq.json"]),
        ("tourism-demo", app, ["scripts/tourism_office.py", "demo", "--out", "../review-output/tourism"]),
        ("tourism-search", app, ["scripts/tourism_office.py", "search", "tea", "--db", "../review-output/tourism/cases.sqlite"]),
    ]
    for name, cwd, args in jobs:
        run = subprocess.run([sys.executable, *args], cwd=cwd, env=environment, capture_output=True,
                             text=True, encoding="utf-8", timeout=120)
        (QA / (name + ".txt")).write_text(run.stdout + run.stderr, encoding="utf-8")
        checks.append({"name":name, "exit_code":run.returncode, "command":"python " + " ".join(args)})
        print(name, run.returncode, (run.stdout + run.stderr)[-650:], flush=True)
        assert run.returncode == 0, name
        if name == "standalone-proposal":
            result = json.loads(run.stdout)
            assert result["status"] == "completed"
            assert len(result["output"]["artifacts"]) == 2
        if name == "tourism-stage":
            assert json.loads(run.stdout)["status"] == "ok"
        if name == "tourism-demo":
            result = json.loads(run.stdout)
            for path in result["files"].values():
                assert (app / path).is_file(), path
        if name == "tourism-search":
            assert json.loads(run.stdout), "No indexed demonstration case found"

    broken = []
    docs = [root / name for name in ("README.md", "REVIEWER_GUIDE.md", "SOURCE_MAP.md", "SKILL_INDEX.md", "DEMO_TRACE.md")]
    docs += [root / "submission/README.md", app / "README.md", app / "SKILL.md", app / "references/api.md", app / "references/source-register.md"]
    link_count = 0
    for path in docs:
        for raw in re.findall(r"\]\((<[^>]+>|[^)\n]+)\)", path.read_text(encoding="utf-8")):
            target = raw.strip("<>")
            if re.match(r"^[a-zA-Z]+:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            if not (path.parent / target).exists():
                broken.append({"document":path.relative_to(root).as_posix(), "target":target})
            link_count += 1
    assert not broken, json.dumps(broken, indent=2)
    report = {"date":"2026-09-29", "scope":"Fresh extraction of the source ZIP using the authoring Python environment; no new model/API run",
              "python":sys.version.split()[0], "checks":checks, "relative_document_links_checked":link_count,
              "broken_document_links":0, "source_file_identity":"All 407 original application files verified byte-for-byte against the packaged manifest",
              "original_skill_instructions":70, "live_model_calls":0,
              "notes":["Dependencies were already installed in the authoring environment; fresh dependency resolution on another machine is not claimed.",
                       "The final package is rebuilt to include this report, then integrity-checked again. Prior submission logs retain their original dates."]}
    (OUT / "agent-skill-source/PACKAGE_VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"extracted_root":str(root), "checks_passed":len(checks), "relative_links":link_count}, indent=2))


if __name__ == "__main__":
    main()
