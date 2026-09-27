# Submission authoring sources

[Repository](https://github.com/energelpen/1010-Chengdu-Hackathon)

The final Markdown editions are `01-skill-function-description.md`, `02-api-documentation.md` and `04-enterprise-challenge-fit.md`. Their rendered PDFs are one directory above. The final narrated script is `../demo-script.md`; English captions are `../03-implementation-demo.srt`.

## Document generation

`skill_description.json`, `enterprise_fit.json` and `api_complete.json` contain the final structured document content. `render_submission.py` renders these with ReportLab, embedded Segoe fonts when available, page numbers and consistent tables. It needs ReportLab and pypdf. Use the existing final JSON for routine regeneration:

```powershell
python submission/source/render_submission.py
```

`create_content.py` created the initial content. `finalize_content.py` reconciled it with the final recording and generated the Markdown editions. Do not rerun either as a prerequisite for rendering the saved final content. `build_api_appendix.py` extracts the full parameter appendix from the application's manifests.

## Recording and narration

`record_full_demo.py` copies credential-free app code to the ignored QA directory, creates fresh state, and records real browser interactions with Playwright and Edge. Its skill runs and file downloads are actual application outputs. `voice_full_demo.py` uses Windows SAPI for local synthetic narration. `assemble_full_demo.py` synchronizes chapters, adds scope labels and embedded English captions, and exports H.264/AAC MP4. It requires Pillow and FFmpeg. `validate_artifacts.py` renders PDFs with Poppler, decodes the entire video, checks audio and upload limits, and writes the submission manifest.

Runtime and FFmpeg paths near the top of the scripts reflect the Windows authoring environment and should be adjusted on another machine. Temporary browser videos, audio, isolated state and encoding tools are not committed. The sanitized execution evidence and generated files are in `../evidence/`.

## Verification scope

`verification/` contains the captured existing test-suite outputs, not fabricated evaluation results. `verify_submission.py` uses an isolated state directory for those checks. The 180 tourism decision cases, 46 automated tests and 48 fixed routing prompts are distinct reported groups.

The recording covers an operator-led simulated launch preparation workflow. It does not demonstrate automatic full launch completion from one sentence or real external release. The documentation preserves that distinction.
