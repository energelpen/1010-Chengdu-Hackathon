"""Build the documented voluntary Track B source ZIP from original tracked files."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "submission"
DOCS = OUT / "agent-skill-source"
NAME = "Atlas-Singapore-Polytechnic-Agent-Skill-Source"
REPO = "https://github.com/energelpen/1010-Chengdu-Hackathon"
DATE = "2026-09-29"


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE, text=True).strip()
    # Source provenance refers to the last application change, not later packaging-only commits.
    source_revision = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", "chengdu-tourism-office"], cwd=BASE, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "chengdu-tourism-office"], cwd=BASE, text=True)
    assert not dirty.strip(), "Commit/review application changes before packaging the original source."
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "chengdu-tourism-office"], cwd=BASE)
    app_files = sorted(p.decode("utf-8") for p in tracked.split(b"\0") if p)
    manifests = sorted((BASE / "chengdu-tourism-office/skills").glob("*/skill.json"))
    skills = [json.loads(p.read_text(encoding="utf-8")) for p in manifests]
    assert len(skills) == 69 and len({s["id"] for s in skills}) == 69
    evidence = json.loads((OUT / "evidence/launch-execution.json").read_text(encoding="utf-8"))
    used = Counter(r["skill_id"] for r in evidence["runs"])
    title = "# Original Agent Skill index\n\n"
    title += "**Team Atlas — Singapore Polytechnic**\n\n"
    title += ("All 69 original skill instruction files are linked below. The additional "
              "[top-level SKILL.md](chengdu-tourism-office/SKILL.md) describes the nine-stage tourism workflow. "
              "The manifests are executable contracts; SKILL.md provides instructions read by the agent.\n\n")
    title += "| Category | Skills |\n|---|---:|\n"
    title += "\n".join(f"| {category} | {count} |" for category, count in sorted(Counter(s["category"] for s in skills).items()))
    title += ("\n\nEffects: `local` runs locally; `remote_read` needs a connected service; "
              "`remote_write` and `reviewed_write` require review before execution. "
              "The Tourism template category contains ten skills: nine stages and the booking-confirm simulation skill. "
              "The Recorded column counts skill executions in the preserved launch demo, not general coverage.\n\n")
    for category in sorted({s["category"] for s in skills}):
        title += f"## {category}\n\n| Skill | Original instructions | Manifest | Runner | Effect | Recorded |\n|---|---|---|---|---|---:|\n"
        for skill in skills:
            if skill["category"] != category:
                continue
            sid = skill["id"]
            path = "chengdu-tourism-office/skills/" + sid
            title += f"| {skill['title']} (`{sid}`) | [SKILL.md]({path}/SKILL.md) | [skill.json]({path}/skill.json) | [run.py]({path}/scripts/run.py) | `{skill['effect']}` | {used[sid]} |\n"
    title += "\nUse the runner forms in [Reviewer guide](REVIEWER_GUIDE.md); the nine tourism runners use a different CLI from the 60 company runners.\n"
    (DOCS / "SKILL_INDEX.md").write_text(title, encoding="utf-8")

    stats = evidence["agent_run"]["statistics"]
    trace = "# Recorded launch: prompt, skills and evidence\n\n**Team Atlas — Singapore Polytechnic**\n\n"
    trace += ("This index is generated from [launch-execution.json](submission/evidence/launch-execution.json). "
              "It describes the preserved successful run, not a newly executed demonstration. "
              "Business inputs and outcomes are simulated; tool calls and file creation are real.\n\n")
    trace += "## One initiating request\n\n> " + evidence["prompt"].replace("\n", "\n> ") + "\n\n"
    trace += "## Measured execution\n\n| Measure | Recorded value |\n|---|---:|\n"
    for name, value in [("Completed skill executions",stats["skills_completed"]),("Distinct skills",stats["distinct_skills"]),
                        ("Fictional delegated colleagues",stats["delegated_people"]),("Generated files",stats["artifacts"]),
                        ("Model requests",stats["model_requests"]),("Function-tool calls",stats["tool_calls"]),
                        ("Failed / pending skills",f"{stats['skills_failed']} / {stats['skills_pending']}"),
                        ("Elapsed seconds",round(stats["elapsed_ms"]/1000,1)),("Provider-reported total tokens",f"{stats['total_tokens']:,}")]:
        trace += f"| {name} | {value} |\n"
    trace += ("\nToken usage is summed across requests and includes repeated context; it is not a cost estimate or unique-context size. "
              "The 26 function calls include planning/discovery operations as well as the 20 skill executions. "
              "Seven staff profiles represent delegation inside one model-driven orchestrator.\n\n")
    trace += "## Published plan and matching runs\n\n| Step | Skill instructions | Assignee | Depends on | Status | Runtime run ID |\n|---|---|---|---|---|---|\n"
    runs = {r["id"]: r for r in evidence["runs"]}
    for step in evidence["agent_run"]["steps"]:
        sid = step["skill_id"]
        assert step["run_id"] in runs and runs[step["run_id"]]["skill_id"] == sid
        trace += f"| {step['id']} | [{sid}](chengdu-tourism-office/skills/{sid}/SKILL.md) | `{step['person_id']}` | {', '.join(step['depends_on']) or '—'} | {step['status']} | `{step['run_id']}` |\n"
    trace += ("\nIn the JSON, join `agent_run.steps[].run_id` to `runs[].id`. Inspect each run's `input`, `output` and `status`, "
              "then join artifact IDs with `artifacts[]`. The [timeline](submission/evidence/agent-timeline.json) preserves interim snapshots.\n\n")
    trace += "## Actual generated deliverables\n\n"
    for path in sorted((OUT / "evidence/generated-files").iterdir()):
        if path.is_file():
            rel = "submission/evidence/generated-files/" + path.name
            trace += f"- [{path.name}](<{rel}>)\n"
    trace += ("\nThe [demo script](submission/demo-script.md) describes both agent execution and the subsequent read-only tour. "
              "The organisation chart, people, library, approach, activity, files and settings tour adds no skill executions to these counts.\n")
    (DOCS / "DEMO_TRACE.md").write_text(trace, encoding="utf-8")

    details = {"team_name":"Atlas","institution":"Singapore Polytechnic","entry":"Atlas Office",
               "competition":"1010 Global AI Agent Competition","track":"B","challenge":"SP-D Product Launch Preparation",
               "purpose":"Voluntary original Agent Skill source supplement","package_date":DATE,"repository":REPO,
               "application_source_commit":source_revision,"source_snapshot_base_commit":revision,
               "original_individual_skill_markdown_files":69,"original_top_level_skill_markdown_files":1,
               "original_application_files":len(app_files),"original_application_markdown_files":sum(p.endswith('.md') for p in app_files),
               "submission_email":"support@wesomeai.com","email_sent":False,
               "review_documents":["README.md","REVIEWER_GUIDE.md","SOURCE_MAP.md","SKILL_INDEX.md","DEMO_TRACE.md"]}
    dump(DOCS / "SUBMISSION_DETAILS.json", details)
    files = {}
    origins = {}

    def add(name, source):
        assert name not in files and source.is_file() and not source.is_symlink(), name
        files[name] = source.read_bytes()
        origins[name] = source.relative_to(BASE).as_posix()

    for rel in app_files:
        add(rel, BASE / rel)
    # These organizer-supplied references are linked by the original source register.
    for name in ("Challenge Topics.pdf", "Judging Rubric.pdf"):
        add(name, BASE / name)
    docs = ["README.md","REVIEWER_GUIDE.md","SOURCE_MAP.md","SKILL_INDEX.md","DEMO_TRACE.md",
            "EMAIL_DRAFT.txt","SUBMISSION_DETAILS.json","verify_package.py"]
    if (DOCS / "PACKAGE_VALIDATION.json").exists():
        docs.append("PACKAGE_VALIDATION.json")
    for name in docs:
        add(name, DOCS / name)
    add("submission/README.md", DOCS / "SUPPORTING_DOCUMENTS.md")
    for name in ["01-skill-function-description.pdf","02-api-documentation.pdf","04-enterprise-challenge-fit.pdf",
                 "06-entry-summary.txt","03-implementation-demo.srt","demo-script.md","submission-manifest.json"]:
        add("submission/" + name, OUT / name)
    for name in ["01-skill-function-description.md","02-api-documentation.md","04-enterprise-challenge-fit.md"]:
        add("submission/source/" + name, OUT / "source" / name)
    for folder in [OUT / "evidence", OUT / "source/verification"]:
        for path in sorted(folder.rglob("*")):
            if path.is_file() and "isolated-test-state" not in path.parts:
                add(path.relative_to(BASE).as_posix(), path)

    token = re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b")
    for name, content in files.items():
        path = Path(name)
        assert not any(part in {".git", ".venv", "node_modules", "__pycache__", "output", "qa"} for part in path.parts), name
        assert path.name == ".env.example" or not path.name.startswith(".env"), name
        assert path.suffix not in {".sqlite", ".pyc", ".log"}, name
        if path.suffix in {".py", ".js", ".mjs", ".json", ".md", ".txt", ".html", ".ps1"}:
            assert not token.search(content), "Potential credential pattern in " + name
    inventory = {"package":NAME,"package_date":DATE,"repository":REPO,"application_source_commit":source_revision,
                 "note":"SHA-256 covers every packaged file except this manifest. Original application files are byte-for-byte copies of the working checkout at the recorded source snapshot.",
                 "files":[{"path":name,"bytes":len(files[name]),"sha256":hashlib.sha256(files[name]).hexdigest(),
                           "original_repository_path":origins[name]} for name in sorted(files)]}
    manifest_bytes = (json.dumps(inventory, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    files["FILE_MANIFEST.json"] = manifest_bytes
    dump(DOCS / "FILE_MANIFEST.json", inventory)
    archive = OUT / (NAME + ".zip")
    temporary = OUT / (NAME + ".tmp.zip")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(NAME + "/" + name, (2026,9,29,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[name], compresslevel=9)
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(files)
    temporary.replace(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (OUT / (NAME + ".zip.sha256")).write_text(f"{digest}  {NAME}.zip\n", encoding="ascii")
    print(json.dumps({"zip":str(archive),"bytes":archive.stat().st_size,"files":len(files),
                      "original_application_files":len(app_files),"original_skill_markdown_files":70,
                      "sha256":digest,"credential_scan":"no token patterns detected"}, indent=2))


if __name__ == "__main__":
    main()
