# Submission authoring sources

[Repository](https://github.com/energelpen/1010-Chengdu-Hackathon)

The final Markdown editions are `01-skill-function-description.md`, `02-api-documentation.md` and `04-enterprise-challenge-fit.md`. Their rendered PDFs are one directory above. The final narrated script is `../demo-script.md`; English captions are `../03-implementation-demo.srt`.

## Document generation

`skill_description.json`, `enterprise_fit.json` and `api_complete.json` contain the final structured document content. `render_submission.py` renders these with ReportLab, embedded Segoe fonts when available, page numbers and consistent tables. It needs ReportLab and pypdf. Use the existing final JSON for routine regeneration:

```powershell
python submission/source/render_submission.py
```

`update_agent_content.py` reconciles the PDFs, Markdown and summary with the verified agent execution evidence. `create_content.py` is historical scaffolding, not a prerequisite for rendering the saved content. `build_api_appendix.py` extracts the parameter appendix from the application's manifests.

## Recording and narration

`record_agent_demo.py` copies app code into an isolated QA workspace and records one prompt driving real model-led skill execution in Playwright and Edge. The configured API key is passed only to the child server environment. API usage must be authorized before reproduction. There are no scripted skill submissions or manual approval clicks. The recorder downloads actual generated files and captures measured execution snapshots.

`voice_full_demo.py --agent` uses Windows SAPI for narration. `assemble_agent_demo.py` compresses waits, synchronizes chapters, adds a small Simulation badge and embedded English captions, and exports a clean full-frame H.264/AAC MP4. It requires Pillow and FFmpeg. `validate_artifacts.py` renders PDFs with Poppler, decodes the entire video, checks audio and upload limits, and writes the manifest.

Runtime and FFmpeg paths near the top of the scripts reflect the Windows authoring environment and should be adjusted on another machine. Temporary browser videos, audio, isolated state and encoding tools are not committed. The sanitized execution evidence and generated files are in `../evidence/`.

## Verification scope

`verification/` contains captured test outputs. `verify_submission.py` uses an isolated state directory for those checks. The 180 tourism decision cases, 51 automated tests and 48 fixed routing prompts are distinct reported groups. The added tests cover extended single-request execution, token counts, approval dependencies, required contract reads, unfinished plans and persistence.

The recording covers one successful model-led simulated launch workflow. It demonstrates actual skill execution and local artifacts, not a real external release or a general end-to-end reliability rate. `evidence/launch-execution.json` and `evidence/agent-timeline.json` contain the measured results. The staff profiles represent delegated tool execution within one orchestrator.
