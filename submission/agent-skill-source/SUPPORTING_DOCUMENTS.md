# Supporting submission documents

This folder preserves the entry documents and recorded evidence included with the source supplement. Start with the [source-package README](../README.md) or [reviewer guide](../REVIEWER_GUIDE.md).

| Document | PDF | Original Markdown/text |
|---|---|---|
| Skill function description | [PDF](01-skill-function-description.pdf) | [Markdown](source/01-skill-function-description.md) |
| Full API reference | [PDF](02-api-documentation.pdf) | [Markdown](source/02-api-documentation.md) |
| Enterprise challenge fit | [PDF](04-enterprise-challenge-fit.pdf) | [Markdown](source/04-enterprise-challenge-fit.md) |
| Entry summary | — | [Text](06-entry-summary.txt) |
| Narrated demo script | — | [Markdown](demo-script.md) |
| English video captions | — | [SRT](03-implementation-demo.srt) |

The API reference describes all 69 skills. For direct command-line execution, use the two runner forms documented in the [reviewer guide](../REVIEWER_GUIDE.md): 60 company runners accept `--input`; the nine tourism runners accept positional JSON or `@path`.

The [recorded evidence](evidence/README.md) includes the agent plan, inputs, runtime outputs, timeline and actual generated documents. The [verification results](source/verification/results.json) and accompanying text files preserve the checks captured for the submitted version. Dates in those files refer to the original verification, not a new live model run.

The [original submission manifest](submission-manifest.json) describes the original upload assets, including the video and cover. `../FILE_MANIFEST.json` describes this source ZIP and is the authoritative inventory for the supplement.

The full narrated video and cover are available in the [GitHub submission folder](https://github.com/energelpen/1010-Chengdu-Hackathon/tree/main/submission). The video lasts 4 minutes 46 seconds and includes the agent execution and a read-only product tour. No video regeneration or new API run is needed to inspect the source evidence.
