"""Align all submission text with the final recorded demonstration."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
repo='https://github.com/energelpen/1010-Chengdu-Hackathon'
doc=json.loads((ROOT/'skill_description.json').read_text(encoding='utf-8'))
doc['pages'][0]['sections'][2]['paragraphs']=[
 'The supplied SP-D challenge specifies Product Launch Preparation. The narrated recording follows a complete operator-led preparation simulation for a Chengdu food and tea group-tour product, from one entered brief through 13 distinct skills to a completed simulated management handoff.',
 'The recording includes options, qualified staff allocations, a dependency plan, a responsibility matrix, task status revision, budget variance, a real approval gate for a workbook copy, decision logging, PDF generation and searchable knowledge. Automatic launch completion from one sentence remains unverified; operator inputs and synthetic completion evidence are explicit.'
]
doc['pages'][2]['sections'][0]['paragraphs']=[
 'The recording prepares the launch of a fictional Chengdu food and tea group-tour product. A pilot costing CNY 50,000 is compared with a CNY 120,000 full launch. Supplied impact/risk/cost weights of 5/3/2 produce scores of 75.7 and 62.0, respectively. The executed proposal skill recommends the pilot and creates real Word and PowerPoint files.'
]
doc['pages'][2]['sections'][2]['paragraphs'][1]='OpenAI-backed conversation and bounded tool discovery are optional. No-key general-company chat provides local directory/help responses; it does not execute the free-form launch request. The recording uses the typed Skills library to invoke and assign real operations. A selected avatar is role context, not a separate authenticated employee account.'
doc['pages'][2]['sections'][3]['paragraphs']=[
 'The final recording exercises 13 distinct skills and supplies simulated completion evidence for the preparation tasks. The management handoff records three done tasks; the separate task register shows a blocked-to-done operator update. No real product release, supplier reservation, payment or external message is claimed.',
 'Automatic single-sentence orchestration of the entire launch remains outside the demonstrated scope. The workflow shown is a complete operator-led preparation simulation.'
]
doc['pages'][4]['sections'][2]['paragraphs'][1]='The demo video records actual application interactions and 13 completed local skill runs across six roles, with a real awaiting_approval-to-completed spreadsheet edit. Synthetic narration and chapter captions identify the operator-led simulation. This does not establish automatic launch orchestration, enterprise deployment, measured productivity savings or marketplace publication.'
for p in doc['pages']:
    for s in p['sections']:
        for field in ('paragraphs','bullets'):
            if field in s: s[field]=[x.replace('Sichuan Shanghai Holiday International Travel Service Co., Ltd.','Sichuan Shanghai Airlines Holiday International Travel Agency Co., Ltd.') for x in s[field]]
doc['pages'][0]['sections'].append({'heading':'Project repository','paragraphs':[repo]})
(ROOT/'skill_description.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding='utf-8')

fit=json.loads((ROOT/'enterprise_fit.json').read_text(encoding='utf-8'))
fit['pages'][0]['sections'][1]['paragraphs'][0]=fit['pages'][0]['sections'][1]['paragraphs'][0].replace('(descriptive English rendering of 四川上航假期国际旅行社有限公司)','(descriptive English rendering of its registered Chinese name)')
fit['pages'][3]['sections'][0]['paragraphs'][1]='Atlas implements the relationship workspace, independent launch planning and reporting tools, and an integrated tourism RFQ loop. The recording demonstrates the full operator-led launch preparation cycle through 13 distinct skills, including a reviewed workbook change and simulated completion. Automatic multi-person launch completion from a single sentence has not been verified. Separate successful skill calls do not establish that strict SP-D requirement.'
fit['pages'][3]['sections'][-1]['paragraphs'].append('Project source and reproducible demonstration: '+repo)
(ROOT/'enterprise_fit.json').write_text(json.dumps(fit,indent=2,ensure_ascii=False),encoding='utf-8')

api=json.loads((ROOT/'api_documentation.json').read_text(encoding='utf-8'))
api['pages'][0]['sections'][0]['paragraphs'].append('Source repository: '+repo)
appendix=json.loads((ROOT/'api_skill_appendix.json').read_text(encoding='utf-8'))
api['pages']+=appendix['pages']
(ROOT/'api_complete.json').write_text(json.dumps(api,indent=2,ensure_ascii=False),encoding='utf-8')

summary='''Atlas Office is an organizational collaboration workspace for Product Launch Preparation and group-travel operations, aligned with the SP-D challenge and the culture, commerce and tourism theme.

Its representative enterprise context is Sichuan Shanghai Airlines Holiday International Travel Agency Co., Ltd. Public descriptions of destination services, business travel and MICE inform the workflow design. The enterprise has not endorsed the prototype or supplied private SOPs.

Atlas models fictional colleagues through their roles, managers, skills, availability, capacity and relationships. Its 69 registered skills support business documents, spreadsheets, presentations, project work, finance, governance and optional connected tools. The same validated runtime serves browser forms, HTTP, CLI and MCP.

The narrated implementation demo records the full operator-led preparation of a fictional Chengdu food and tea group-tour product. Thirteen distinct skills compare pilot and full-launch options, propose qualified staff allocations, calculate dependencies, map responsibilities, track a blocker through a simulated resolution, calculate budget variance, create and review a workbook change, record a management decision, deliver a completed simulated handoff, generate a PDF, and save and retrieve knowledge. Word, PowerPoint, Excel and PDF artifacts are real outputs. The recording includes a genuine approval gate for a local spreadsheet copy.

Nine independently callable tourism skills additionally form an integrated inquiry-to-outcome simulation. They apply budget and capacity constraints, track evidence and dependencies, build dated schedules, and hold release when required checks are missing.

Verification on 27 September 2026 passed 180 tourism behavior cases and 46 automated tests. The fixed routing corpus matched 43/43 action prompts and left 5/5 non-action prompts unassigned. These bounded tests are not general accuracy or measured enterprise savings.

The core value is visible responsibility, inspectable decisions and reusable preparation work. Demo staff, prices, decisions and completion evidence are synthetic. No real launch, booking, payment or external message occurs. The recording uses typed skill forms; automatic full launch completion from one sentence remains unverified. OpenAI and external services are optional. The current app is a single-user local prototype.

Source: https://github.com/energelpen/1010-Chengdu-Hackathon'''
assert len(summary)<=3000
(ROOT.parent/'06-entry-summary.txt').write_text(summary,encoding='utf-8')
(ROOT/'summary-metadata.json').write_text(json.dumps({'characters':len(summary),'maximum':3000},indent=2),encoding='utf-8')

for name,d in [('01-skill-function-description.md',doc),('02-api-documentation.md',api),('04-enterprise-challenge-fit.md',fit)]:
    lines=['# '+d['subtitle'],'',d['version'],'','Repository: '+repo,'']
    for p in d['pages']:
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
        lines+=['Sources: '+'; '.join(p.get('sources',[])),'']
    (ROOT/name).write_text('\n'.join(lines),encoding='utf-8')
print('Final summary characters',len(summary))
