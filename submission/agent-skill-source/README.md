# Atlas Office — Agent Skill source submission

**Team:** Atlas

**Institution:** Singapore Polytechnic

**Competition:** 1010 Global AI Agent Competition, Track B

**Entry:** Atlas Office — Product Launch Preparation (SP-D)

**Source package date:** 29 September 2026

**GitHub:** https://github.com/energelpen/1010-Chengdu-Hackathon

This is the voluntary original-source supplement to our submitted entry. It contains all 69 individual skill instruction files, the top-level tourism `SKILL.md`, manifests, Python implementations, examples, tests, the full application source and assets, and supporting execution evidence. Original application files are copied without modification.

Atlas Office turns one business request into a model-authored plan, delegated skill calls and inspectable deliverables. The recorded Chengdu food-and-tea launch simulation completed **20 skill executions across 16 distinct skills and 7 fictional colleagues, generating 10 real files**. Business outcomes are simulated; the recorded calls and generated documents are real. Colleagues are staff profiles used by one orchestrator, not seven independent model sessions.

## Start here

1. Read [Reviewer guide](REVIEWER_GUIDE.md) for setup, offline checks and optional agent execution.
2. Open [Skill index](SKILL_INDEX.md) to browse all 69 original `SKILL.md` files, manifests and runners.
3. Follow [Recorded launch trace](DEMO_TRACE.md) from the single prompt to the 20 completed steps and output files.
4. Use [Source map](SOURCE_MAP.md) to inspect orchestration, validation, approvals, APIs and tests.
5. Browse [supporting submission documents](submission/README.md) for the original PDFs, Markdown and evidence.

## Package layout

| Path | Contents |
|---|---|
| `chengdu-tourism-office/SKILL.md` | Original top-level tourism skill instructions |
| `chengdu-tourism-office/skills/<id>/SKILL.md` | Original instructions for each of the 69 registered skills |
| `chengdu-tourism-office/skills/<id>/skill.json` | Typed input contract, effect, handler and example |
| `chengdu-tourism-office/skills/<id>/scripts/run.py` | Executable entry point for that skill |
| `chengdu-tourism-office/scripts/` | Shared execution runtime, agent loop and implementations |
| `chengdu-tourism-office/app.py`, `web/`, `server/` | Web application and MCP entry points |
| `chengdu-tourism-office/tests/`, `examples/`, `resources/` | Automated checks and fictional inputs |
| `submission/evidence/` | Actual recorded execution and the 10 generated deliverables |
| `submission/source/verification/` | Captured verification results from the submitted version |
| `FILE_MANIFEST.json` | Sizes, SHA-256 hashes and original paths for every packaged file except itself |
| `verify_package.py` | Standard-library-only integrity and inventory check |
| `EMAIL_DRAFT.txt`, `SUBMISSION_DETAILS.json` | Team identification and ready-to-copy submission email |

From this extracted folder, verify the contents before running the application:

```text
python verify_package.py
```

This checks hashes, skill instructions/manifests/runners, and the recorded statistics. It does not install dependencies, call an API or execute the live agent. Setup and three reproducible local demonstrations are in the reviewer guide. The full app requires Python 3.11 or newer and the supplied requirements; dependency installation requires internet access. Dependencies are bounded in `requirements.txt`, not fully version-locked.

[Package validation results](PACKAGE_VALIDATION.json) record the fresh-extraction checks performed on 29 September: 180 tourism cases, 51 automated tests, 48 fixed routing prompts, the standalone proposal, the tourism stage and full demo, and case search. The checks used the existing authoring Python environment; no live model run was made.

## Source and evidence boundaries

The source snapshot is identified in `SUBMISSION_DETAILS.json` and `FILE_MANIFEST.json`. The ZIP includes all tracked application files, including the fictional portrait assets and the demonstration finance workbook. It excludes credentials, personal runtime databases, virtual environments, browser profiles, temporary recordings and Git history. The narrated video and cover remain available through the repository; omitting them keeps this supplement focused on source review.

The 69-skill library includes nine tourism stages. Optional connected services require separate accounts and configuration. Local typed skills and offline tests can run without an API key; general-company free-form agent execution requires a configured model and incurs provider usage. A fresh run may choose a different plan and will not reproduce identical IDs, timings or token totals.

The application is a local single-user prototype. Public enterprise context is documented in its source register; the named enterprise has not supplied private SOPs or endorsed the prototype. See the reviewer guide for the precise simulation and approval behavior.

This supplement is provided for the evaluation and potential showcase purposes described in the organizing committee's request. No new software license is added by this package; dependency licenses remain with their respective projects.
