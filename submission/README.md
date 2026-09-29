# Atlas Office submission

[GitHub repository](https://github.com/energelpen/1010-Chengdu-Hackathon) · [Application setup](../chengdu-tourism-office/README.md)

[Download the complete submission bundle](atlas-office-submission.zip) or the [independently runnable skills source package](atlas-office-skills-source.zip).

## Voluntary original-source supplement

**Team Atlas — Singapore Polytechnic.** [Download the documented Agent Skill source ZIP](Atlas-Singapore-Polytechnic-Agent-Skill-Source.zip) for the organizing committee's voluntary source request. It contains all 69 individual original `SKILL.md` files and the top-level instructions, the full application source and assets, examples, tests, reviewer documentation, recorded execution evidence, and an email draft identifying the team and institution. The package's `README.md` is the starting point. `verify_package.py` checks its SHA-256 file manifest without installing dependencies or calling an API.

The [archive checksum](Atlas-Singapore-Polytechnic-Agent-Skill-Source.zip.sha256) is supplied separately. This source supplement omits the video and cover, which remain available below. The original six submission artifacts are unchanged.

## Upload these six items

| Form field | File | Limit |
|---|---|---|
| 1. Skill function description | [01-skill-function-description.pdf](01-skill-function-description.pdf) | 30 MB |
| 2. API documentation | [02-api-documentation.pdf](02-api-documentation.pdf) | 30 MB |
| 3. Implementation demo video | [03-implementation-demo.mp4](03-implementation-demo.mp4) | 200 MB; supplied guideline also requires no more than 5 minutes |
| 4. Enterprise challenge fit | [04-enterprise-challenge-fit.pdf](04-enterprise-challenge-fit.pdf) | 30 MB |
| 5. Entry cover | [05-entry-cover.png](05-entry-cover.png) | 5 MB |
| 6. Entry summary | Paste [06-entry-summary.txt](06-entry-summary.txt) | 3,000 characters |

The API documentation is included even though the pasted form labels it optional: the supplied Judging Rubric requests it. The documents are in English, matching the supplied form and challenge materials.

## Demo contents

The extended video also tours the organisation chart, people directory, skill library and instructions, the recorded launch approach, activity and approvals, files and company knowledge, workspace controls, connection options, and API reference. These sections inspect the saved completed workspace; the agent-led launch remains the main workflow.

The narrated demo shows **one request driving an agent-led Product Launch Preparation simulation**. The recorded run completed 20 skill executions across 16 distinct skills and 7 fictional colleagues, producing 10 real files. It used 24 model requests and 26 tool calls; reported usage totaled 800,795 tokens across requests. Actual wall time was 303.8 seconds. The agent compares pilot and full-launch options, checks team capacity, records decisions, schedules dependencies, maps responsibility, prepares a campaign and launch checklist, tracks tasks, assesses risk, calculates budget variance and a finance forecast, creates the executive pack, and saves and retrieves reusable knowledge. The pack includes editable Word, PowerPoint and Excel files plus a PDF report.

The live dashboard shows the plan, staff, real skill calls, completion states, file counts, elapsed time and provider-reported token usage. [Run evidence](evidence/launch-execution.json) and [the demo script](demo-script.md) preserve the provenance.

One user brief starts a real configured OpenAI model. The model chooses the skills, publishes a dependency-aware plan, assigns qualified colleagues, supplies the inputs and executes local work through the shared runtime. The recording contains no manual skill submissions. All business facts and launch outcomes are explicitly simulated; no external delivery, spending or real product release occurs. Execution evidence and generated files are retained in the submission evidence folder.

## Additional review material

- [Markdown versions and artifact sources](source/)
- [Existing test-suite evidence](source/verification/)
- [Application source](../chengdu-tourism-office/)
- [GitHub link](https://github.com/energelpen/1010-Chengdu-Hackathon)

File sizes, video duration, audio presence and character count are recorded in `submission-manifest.json` after validation. The cover was generated using the built-in image generator; its prompt is saved in the source folder. Recording machinery, credentials and local application databases are excluded from the repository.
