"""Update submission narratives from the verified, recorded agent run."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'submission'; HERE=OUT/'source'
evidence=json.loads((OUT/'evidence/launch-execution.json').read_text(encoding='utf-8'))
run=evidence['agent_run']; stats=run['statistics']; assert run['status']=='completed'
repo='https://github.com/energelpen/1010-Chengdu-Hackathon'
measured=f"The recorded run completed {stats['skills_completed']} skill executions across {stats['distinct_skills']} distinct skills and {stats['delegated_people']} fictional colleagues, producing {stats['artifacts']} real files. It used {stats['model_requests']} model requests and {stats['tool_calls']} tool calls; reported usage totaled {stats['total_tokens']:,} tokens across requests. Actual wall time was {stats['elapsed_ms']/1000:.1f} seconds."
scope='One user brief starts a real configured OpenAI model. The model chooses the skills, publishes a dependency-aware plan, assigns qualified colleagues, supplies the inputs and executes local work through the shared runtime. The recording contains no manual skill submissions. All business facts and launch outcomes are explicitly simulated; no external delivery, spending or real product release occurs.'
coverage='The agent compares pilot and full-launch options, checks team capacity, records decisions, schedules dependencies, maps responsibility, prepares a campaign and launch checklist, tracks tasks, assesses risk, calculates budget variance and a finance forecast, creates the executive pack, and saves and retrieves reusable knowledge. The pack includes editable Word, PowerPoint and Excel files plus a PDF report.'
doc=json.loads((HERE/'skill_description.json').read_text(encoding='utf-8'))
for page in doc['pages']:
    for section in page['sections']:
        for field in ('paragraphs','bullets'):
            if field not in section: continue
            result=[]
            for text in section[field]:
                if text.startswith('The supplied SP-D challenge'): text='The supplied SP-D challenge specifies Product Launch Preparation. The narrated recording follows one request through an agent-led launch simulation for a Chengdu food and tea group-tour product. '+measured
                elif text.startswith('The recording includes options'): text=coverage
                elif text.startswith('The recording prepares the launch'): text='The recording prepares a fictional Chengdu food and tea group-tour launch. A CNY 50,000 pilot is compared with a CNY 120,000 full launch. The agent supplies clearly labeled synthetic assumptions and delegates the actual scoring and proposal generation to proposal-package. Its recommendation and detailed inputs are retained in the execution evidence.'
                elif text.startswith('OpenAI-backed conversation and bounded tool discovery'): text='The recording uses the configured OpenAI model to orchestrate the entire local workflow from one request. Offline general-company chat provides directory/help responses and does not execute free-form requests. Staff profiles supply role context, assigned skills and capacity; one orchestrator performs the delegated tool calls. They are not separate authenticated employee accounts or independent model sessions.'
                elif text.startswith('The final recording exercises'): text=scope
                elif text.startswith('Automatic single-sentence orchestration'): text='The live dashboard persists the model-authored plan, assignees, prerequisite states, each actual tool call, run IDs, artifact counts, elapsed time and provider-reported token usage. Step completion is based on runtime status. Pending approvals and unfinished plans are never counted as completed execution.'
                elif text.startswith('The demo video records actual application'): text=measured+' The successful run establishes this one-request scenario. It does not establish arbitrary-language reliability, enterprise adoption or measured productivity savings.'
                text=text.replace('46 automated tests','51 automated tests')
                result.append(text)
            section[field]=result
        if section.get('table'):
            section['table']['rows']=[[str(x).replace('46 / 46','51 / 51') for x in row] for row in section['table']['rows']]
doc['pages'][0]['sections'][0]['paragraphs'][0]=doc['pages'][0]['sections'][0]['paragraphs'][0].replace('The operator can inspect','The reviewer can inspect')
fit=json.loads((HERE/'enterprise_fit.json').read_text(encoding='utf-8'))
fit['pages'][3]['sections'][0]['heading']='SP-D alignment and demonstrated scope'
fit['pages'][3]['sections'][0]['paragraphs'][1]=scope+' '+measured+' This is a single recorded scenario, not a broad end-to-end success-rate study. The fictional profiles represent delegated skill execution by one orchestrator; they are not real employees or independently running model sessions.'
api=json.loads((HERE/'api_documentation.json').read_text(encoding='utf-8'))
api['pages']=[p for p in api['pages'] if p.get('title')!='Agent orchestration and execution statistics']
api['pages'].append({'title':'Agent orchestration and execution statistics','kicker':'API / AGENT EXECUTION','sections':[
 {'heading':'One request, bounded model-led execution','paragraphs':['POST /api/chat with message and optional conversation_id/person_id runs the selected company assistant. With a configured API key, Atlas exposes find_skills, read_skill, read_skills, set_plan, run_skill, list_workspace_files, ask_user and web search to the configured Responses model. The model chooses the sequence and inputs. There is no hard-coded launch pipeline.','The turn is bounded to 48 model requests, 80 function-tool calls and 600 seconds checked between operations. A single in-flight model request may extend past the time check. Read skill contracts before execution. Planned runs must match their step assignee and skill and may execute only after prerequisites complete. Qualified staff are enforced by the runtime. External and reviewed writes remain pending for explicit review.']},
 {'heading':'Polling and persistence','table':{'headers':['Route / field','Contract'],'rows':[['GET /api/conversation/{id}/agent-run','Latest persisted agent execution object, or null before the first run.'],['GET /api/conversation/{id}/events','Timestamped progress events.'],['conversation.agent_run','The same snapshot included when reading or completing a conversation.'],['steps[]','id, title, skill_id, person_id, depends_on, status; optional run_id and error.'],['calls[]','id, tool, status, started_at, duration_ms; optional skill_id/person_id/step_id/run_id/error.']]}},
 {'heading':'Measured fields and completion states','paragraphs':['statistics contains model_requests, tool_calls, skills_executed, skills_completed, skills_failed, skills_pending, distinct_skills, delegated_people, artifacts, elapsed_ms and input/output/total_tokens. Tokens sum provider usage across requests, including repeated context; they are null if usage is unavailable. They are not a cost estimate. Tool-call counts refer to function tools; built-in web search activity is separately exposed in progress events.','Run states are running, completed, needs_input, awaiting_approval, needs_attention and budget_exhausted. Offline directory mode requests a configured connection and produces no skill runs. Failed or pending work cannot complete a planned dependency. A completed skill means its local handler finished, not that a real-world business outcome occurred.']}
 ],'sources':['Application: scripts/company_chat.py, scripts/agent_execution.py, scripts/conversation_store.py, app.py','OpenAI function calling: https://developers.openai.com/api/docs/guides/function-calling']})
appendix=json.loads((HERE/'api_skill_appendix.json').read_text(encoding='utf-8'))
complete={**api,'pages':api['pages']+appendix['pages']}
for name,data in [('skill_description.json',doc),('enterprise_fit.json',fit),('api_documentation.json',api),('api_complete.json',complete)]:
    (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
summary=f'''Atlas Office is an AI-powered collaboration workspace that turns one business request into a coordinated plan, executed skills and a reviewable set of deliverables. Built for the SP-D Product Launch Preparation challenge, it demonstrates a Chengdu food-and-tea group-tour launch simulation.

The agent reads skill instructions, chooses qualified fictional colleagues, plans dependencies, supplies inputs and calls the tools itself. In the recorded demonstration, one request completed {stats['skills_completed']} skill executions across {stats['distinct_skills']} distinct skills and {stats['delegated_people']} colleagues, producing {stats['artifacts']} real files.

The workflow covers launch-option comparison, team capacity, responsibilities, campaign planning, risk assessment, budgets, forecasting, decisions, management handoff and reusable knowledge. Deliverables include editable Word, PowerPoint and Excel files, plus a final PDF report.

A live dashboard shows the agent's plan, assignees, tool calls, completion states, elapsed time, token usage and generated files. The organisation chart, people directory, 69-skill library, activity and approval views, and file and knowledge tools make the work easy to inspect and reopen.

Browser, HTTP, CLI and MCP interfaces share one validated execution runtime. External and reviewed writes require approval. The library includes nine tourism stages supporting an inquiry-to-outcome simulation.

Verification passed 180 tourism behaviour cases, 51 automated tests and 48 fixed routing prompts. The repository includes the application, skill contracts, API documentation, narrated demonstration, execution evidence and generated outputs.

Atlas makes task ownership, decisions and deliverables visible and reusable. It is a local single-user prototype. Staff and business outcomes are simulated; the recorded agent calls and generated files are real.

GitHub repository: {repo}'''
assert len(summary)<=3000 and len(summary.split())<=2000
(OUT/'06-entry-summary.txt').write_text(summary,encoding='utf-8')
(HERE/'summary-metadata.json').write_text(json.dumps({'characters':len(summary),'maximum':3000,'words':len(summary.split()),'maximum_words':2000},indent=2),encoding='utf-8')
for name,data in [('01-skill-function-description.md',doc),('02-api-documentation.md',complete),('04-enterprise-challenge-fit.md',fit)]:
    lines=['# '+data['subtitle'],'',data['version'],'','Repository: '+repo,'']
    for p in data['pages']:
        lines+=['## '+p['title'],'']
        for s in p['sections']:
            lines+=['### '+s.get('heading',''),'']
            for para in s.get('paragraphs',[]): lines += [para,'']
            for bullet in s.get('bullets',[]): lines += ['- '+bullet]
            if s.get('bullets'): lines+=['']
            if s.get('code'): lines+=['```text',s['code'],'```','']
            if s.get('table'):
                t=s['table']; lines+=['| '+' | '.join(t['headers'])+' |','| '+' | '.join(['---']*len(t['headers']))+' |']
                lines+=['| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in t['rows']]; lines+=['']
        if p.get('sources'): lines+=['Sources: '+'; '.join(p['sources']),'']
    (HERE/name).write_text('\n'.join(lines),encoding='utf-8')
shorthand=HERE/'enterprise-fit.md'
shorthand.write_text((HERE/'04-enterprise-challenge-fit.md').read_text(encoding='utf-8'),encoding='utf-8')
for path in [BASE/'README.md',BASE/'chengdu-tourism-office/README.md',BASE/'chengdu-tourism-office/references/demo-script.md',OUT/'README.md']:
    text=path.read_text(encoding='utf-8')
    paragraphs=text.split('\n\n'); revised=[]
    for para in paragraphs:
        if 'operator-led' in para:
            if 'tourism-only rehearsal' in para: para='The final [agent-led launch recording and script](../../submission/demo-script.md) supersede this tourism-only rehearsal. '+measured+' The scenario below remains an additional demonstration of the tourism engine.'
            else: para='The narrated demo shows **one request driving an agent-led Product Launch Preparation simulation**. '+measured+' '+coverage
        elif para.startswith('The recording begins with one brief') or para.startswith('Preparation completion is based'): para=scope+' Execution evidence and generated files are retained in the submission evidence folder.'
        elif para.startswith('The launch work is for a fictional'): para='The live dashboard shows the plan, staff, real skill calls, completion states, file counts, elapsed time and provider-reported token usage. [Run evidence](evidence/launch-execution.json) and [the demo script](demo-script.md) preserve the provenance.'
        para=para.replace('46 automated tests','51 automated tests').replace('46**','51**').replace('**46 automated tests**','**51 automated tests**').replace('the 46 automated tests','the 51 automated tests')
        revised.append(para)
    path.write_text('\n\n'.join(revised),encoding='utf-8')
print('Updated verified agent narratives; summary characters:',len(summary))
