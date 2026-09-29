# Atlas Office — reviewer guide

**Team:** Atlas

**Institution:** Singapore Polytechnic

**Entry:** Track B, SP-D Product Launch Preparation simulation

**Repository:** https://github.com/energelpen/1010-Chengdu-Hackathon

This package supplies the original Agent Skill Markdown, executable implementation, examples, tests and supporting evidence. It preserves the application's source files rather than requiring a judge to reconstruct the skills from a PDF. The submission demonstrates a local company workspace in which one model-driven orchestrator discovers skills, delegates work to qualified fictional colleague profiles, executes local tools and records their results.

## A short review path

1. Read [the skill function description](submission/source/01-skill-function-description.md) and [the source map](SOURCE_MAP.md) for the scope and implementation entry points.
2. Open an original skill such as [proposal-package/SKILL.md](chengdu-tourism-office/skills/proposal-package/SKILL.md), its [manifest and input schema](chengdu-tourism-office/skills/proposal-package/skill.json), [example](chengdu-tourism-office/skills/proposal-package/references/example.json), and [CLI runner](chengdu-tourism-office/skills/proposal-package/scripts/run.py).
3. Inspect [the recorded launch evidence](submission/evidence/launch-execution.json). The top-level `prompt` is the single user request; `agent_run.steps` contains the dependency plan and actual run IDs. Match those IDs to the recorded runtime results and generated files.
4. Read [the evidence notes](submission/evidence/README.md), [the narrated demo script](submission/demo-script.md), and [the API reference](submission/source/02-api-documentation.md). The repository provides the demo video separately.
5. Optionally install the dependencies and run the local checks below. A paid model connection is not required for these checks or for inspecting the supplied evidence.

The package contains **69 registered skills**, including the nine tourism stages. There are **69 original per-skill `SKILL.md` files**, plus the original top-level [tourism orchestration SKILL.md](chengdu-tourism-office/SKILL.md): **70 skill instruction files in total**. The top-level instruction document describes the tourism workflow; the complete 69-skill catalog is defined by the individual `skill.json` manifests.

## What the recorded demonstration establishes

One request completed **20 skill executions across 16 distinct skills and 7 fictional colleague profiles**, creating **10 real files**. The record reports 24 model requests, 26 function-tool calls, no failed or pending skill runs, and 303.8 seconds of actual execution time. Provider usage totals 800,795 tokens across requests, including repeated context; this is not a unique context size or a cost estimate.

The files include editable Word, PowerPoint and Excel artifacts and a PDF report. The [downloaded outputs](submission/evidence/generated-files/) and [timestamped agent snapshots](submission/evidence/agent-timeline.json) support the recorded result. Skill execution and file creation were real. The launch, staff, prices, decisions and business completion evidence were explicitly simulated. Seven profiles indicate delegation within one orchestrator, not seven independently running models or real employees.

**There is no need to rerun the full live demonstration to inspect this evidence.** A new model run incurs usage and can choose different steps, assumptions and output wording. The included evidence preserves the measured original run.

## Install in a fresh extraction

Use Python 3.11 or newer. Extract the complete ZIP first, then open a terminal in its root. Dependency installation requires access to the Python package index unless the dependencies are already available locally. The original `requirements.txt` uses version ranges, so it is not a frozen dependency lockfile.

Windows PowerShell:

```powershell
Set-Location chengdu-tourism-office
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY = ''
$env:ATLAS_DATA_DIR = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) '../review-output/workspace'))
```

macOS or Linux:

```sh
cd chengdu-tourism-office
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export OPENAI_API_KEY=''
export ATLAS_DATA_DIR="$(pwd)/../review-output/workspace"
```

The ZIP does not supply `.env`, private API keys, account tokens or a saved personal workspace. Keep this extraction separate from an existing configured installation. The commands below use local fixtures and local output folders. Tests create temporary files and may open a loopback HTTP server; they do not require external accounts or a live model.

## Run the local checks

Windows PowerShell, from `chengdu-tourism-office`:

```powershell
.\.venv\Scripts\python.exe scripts/tourism_office.py test
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
.\.venv\Scripts\python.exe tests/trigger_eval.py
```

macOS or Linux, from `chengdu-tourism-office`:

```sh
.venv/bin/python scripts/tourism_office.py test
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -q
.venv/bin/python tests/trigger_eval.py
```

The captured validation passed 180 tourism decision cases, 51 automated tests, and 43 action plus 5 non-action routing prompts. Compare with [the captured result summary](submission/source/verification/results.json), [tourism cases](submission/source/verification/tourism-behavior-tests.txt), [automated tests](submission/source/verification/automated-tests.txt), and [routing evaluation](submission/source/verification/routing-evaluation.txt). Routing accuracy here is measured on a fixed corpus, not arbitrary-language or end-to-end business success.

Some original integration fixtures contain October 2026 dates. Running those fixtures after their dates can correctly produce past-date validation failures; retain the original evidence and update a separate working copy if evaluating later. The tourism decision-case generator uses dates relative to the test day.

## Execute individual skills without a model

There are two original CLI conventions. Run these examples from `chengdu-tourism-office`; replace `python` with the Python executable in the virtual environment above.

**The 60 company skill runners** accept `--input <JSON-file>` or `--input -` for standard input. `--data-dir` selects an isolated runtime database and artifact folder. For example:

```sh
python skills/proposal-package/scripts/run.py --input skills/proposal-package/references/example.json --data-dir ../review-output/company
```

This computes the comparison and creates local Word and PowerPoint drafts. The returned JSON contains the runtime status and generated artifact IDs. Manifests provide embedded examples; some other examples require a preceding file or record ID, or an optional external account, and are not standalone successful operations.

**The nine tourism runners** accept positional JSON or an `@path` argument. Use the shared tourism CLI, for example:

```sh
python scripts/tourism_office.py run inquiry-intake '@examples/rfq.json'
python scripts/tourism_office.py demo --out ../review-output/tourism
python scripts/tourism_office.py search tea --db ../review-output/tourism/cases.sqlite
```

The first command returns the stage's domain envelope. The demo creates a local JSON trace, Word brief, PowerPoint deck and SQLite search index. The HTTP and company MCP interfaces can invoke all 69 registered skills through the shared runtime. For tourism results, inspect the inner domain status as well as the outer runtime status; completing a handler does not establish that the business stage passed every gate.

## Optional website and live agent review

Start the app with the virtual-environment Python:

```sh
python app.py --data-dir ../review-output/ui
```

Open `http://127.0.0.1:8765`. Inspect the organisation chart, people, skill library, activity and approvals, files and knowledge, and workspace settings. The default general-company template provides the model-driven skill orchestration path. The Chengdu tourism template also provides a separate, deterministic nine-stage workflow. Without an API key, the app supplies clearly identified local responses; this is not a reproduction of the recorded model-driven run.

To voluntarily run the live agent, configure an API key and an available model in **Workspace settings → OpenAI connection**. This incurs provider usage. The original recording used the model named in the supplied execution JSON; access to that model is not bundled with the source. Use the supplied `prompt` or a smaller explicitly simulated local task. The agent reads the skill instructions, creates a dependency plan, calls the tools and publishes execution statistics. Reviewed and external writes remain subject to approval.

The original browser smoke script is an optional development aid requiring Playwright, a running app and its configured Windows Edge path. It is not part of the portable baseline checks above. Do not run the catalog/template generator scripts merely to start the app: all generated skill source and templates are already supplied.

## Operational boundaries

Atlas Office is a local single-user prototype with a loopback web server. Staff and enterprise workflow facts are illustrative. Real supplier integration, reservations, payments and external delivery are not established by the simulation. Optional Google Workspace, Telegram, SMTP and external MCP connections require the reviewer's own configuration; credentials are not supplied. The app does not include production multi-user authentication or enterprise access control. See [governance](chengdu-tourism-office/references/autonomy.md) and [the API documentation](submission/source/02-api-documentation.md) for exact review states and interfaces.
