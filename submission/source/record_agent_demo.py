"""Record ONE user request and the real model-led run. No scripted skill submissions."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[2]
SRC = BASE / 'chengdu-tourism-office'
QA = BASE / 'submission/qa/agent-demo'
APP = QA / 'app'
DATA = QA / ('state-' + str(int(time.time())))
QA.mkdir(parents=True, exist_ok=True)
for name in ('scripts', 'web', 'resources', 'shared', 'skills', 'examples'):
    shutil.copytree(SRC/name, APP/name, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.env'))
shutil.copy2(SRC/'app.py', APP/'app.py')
sys.path.insert(0, str(SRC/'scripts'))
from assistant_service import settings
config = settings(SRC)
if not config['api_key']:
    raise RuntimeError('A configured API connection is required for the agent demonstration.')
env = dict(os.environ)
for key in list(env):
    if any(word in key.upper() for word in ('OPENAI', 'SMTP', 'TELEGRAM', 'GOOGLE', 'GMAIL')):
        env.pop(key)
env.update(OPENAI_API_KEY=config['api_key'], OPENAI_MODEL=config['model'], ATLAS_DATA_DIR=str(DATA), PYTHONIOENCODING='utf-8')
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(BASE/'submission/qa/video/pw-browsers')
URL = 'http://127.0.0.1:8878'
log = (QA/'server.log').open('w', encoding='utf-8')
server = subprocess.Popen([str(SRC/'.venv/Scripts/python.exe'), str(APP/'app.py'), '--port', '8878', '--data-dir', str(DATA)], cwd=APP, env=env, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
for _ in range(60):
    try:
        with urlopen(URL+'/api/health', timeout=1) as r:
            r.read()
        break
    except Exception:
        time.sleep(.3)

PROMPT = ('Run an end-to-end SIMULATION of launching a Chengdu food-and-tea group-tour product, from evaluating options to recording the simulated launch outcome and delivering the executive pack. Compare a CNY 50,000 pilot with a CNY 120,000 full launch; assume 30 guests and a preparation start of 1 October 2026. You may invent clearly labeled, internally consistent simulation assumptions for all missing facts. Choose the approach, assign qualified colleagues with capacity, plan dependencies and responsibilities, create the campaign and launch checklist, track work, assess risks, calculate budget variance and a finance forecast, record the simulated decision and outcome, and produce editable proposal slides, a Word management handoff, an Excel budget and a final PDF report. Save and retrieve the launch knowledge for reuse. Execute the local skills yourself in this one turn and show the actual plan, delegated staff, calls and statistics. Everything is simulated; do not contact anyone, use external accounts, make payments, book travel, or claim a real product launch. Finish all local preparation and simulated reporting automatically without asking me to operate the skills.')

scenes = []
current = None
started = 0
errors = []
snapshots = []

def scene(title, narration):
    global current
    if current:
        current['end'] = time.monotonic()-started
        page.screenshot(path=str(QA/(f'{len(scenes):02d}-end.png')))
    current = {'title': title, 'narration': narration, 'start': time.monotonic()-started}
    scenes.append(current)
    print('SCENE', len(scenes), title, flush=True)

def wait(seconds):
    page.wait_for_timeout(seconds*1000)

def focus(selector):
    loc = page.locator(selector).first
    if loc.count():
        loc.scroll_into_view_if_needed()

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
        context = browser.new_context(viewport={'width':1600, 'height':900}, record_video_dir=str(QA/'raw'), record_video_size={'width':1600,'height':900})
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        started = time.monotonic()
        page.goto(URL, wait_until='networkidle')
        page.wait_for_selector('body[data-ready="true"]')
        scene('One request. A whole team.', 'Meet Atlas Office. One request brings the team together to prepare a Chengdu food and tea product launch. This is a business simulation using a real model connection and executable local skills. Atlas chooses the work, assigns colleagues, runs the tools, and creates the deliverables.')
        page.locator('#chat-input').fill(PROMPT)
        wait(5)
        page.locator('#send-message').click()
        cid = None
        phase = 0
        last_signature = None
        deadline = time.monotonic()+720
        while time.monotonic()<deadline:
            wait(1)
            conversations = page.request.get(URL+'/api/conversations').json()
            if not conversations:
                continue
            cid = conversations[0]['id']
            run = page.request.get(URL+'/api/conversation/'+cid+'/agent-run').json()
            if not run:
                continue
            stats = run['statistics']
            signature = (stats['model_requests'],stats['tool_calls'],stats['skills_completed'],run['status'])
            if signature != last_signature:
                snapshots.append({'recording_seconds':time.monotonic()-started,'agent_run':run})
                print('AGENT', signature, flush=True)
                last_signature = signature
            if phase == 0 and run['steps']:
                scene('The agent builds its plan', 'Atlas turns the request into a visible execution plan. Each step has an actual skill, an assigned colleague, and dependencies. The model reads the skill contracts before it uses them. The plan and progress come from the running agent, not a prewritten video sequence.')
                focus('.agent-run-header'); phase = 1
            if phase == 1 and stats['skills_completed'] >= 1:
                scene('Skills become action', 'The first results are arriving. Atlas supplies the skill inputs itself and delegates to colleagues whose profiles allow the work. Every call is recorded with its assignee, outcome, and elapsed time. Completed results become context for the next decision.')
                focus('.agent-run-calls'); phase = 2
            if phase == 2 and stats['skills_completed'] >= 5:
                scene('Teams work through dependencies', 'The agent continues across the company. Planning, responsibilities, capacity and commercial decisions are handled through the same shared runtime. Dependent steps can proceed only after their prerequisites complete. There are no manual skill forms between these actions.')
                focus('.agent-run-plan'); phase = 3
            if phase == 3 and stats['skills_completed'] >= 10:
                scene('From analysis to deliverables', 'The launch takes shape as business records and real files. Finance calculations, project work, launch risks and management outputs are linked to recorded skill runs. Simulation assumptions remain visible in the content, while the document and spreadsheet generation actually execute.')
                focus('.agent-run-calls'); phase = 4
            if phase == 4 and stats['skills_completed'] >= 15:
                scene('The agent closes the loop', 'Atlas brings the completed work into the launch handoff and reusable company knowledge. The same request drives the workflow through its final outputs. The live dashboard keeps the completed work, remaining steps, generated files, and API usage visible.')
                focus('.agent-run-metrics'); phase = 5
            if run['status'] != 'running':
                break
        else:
            raise RuntimeError('Agent recording exceeded its bounded timeout.')
        page.wait_for_function('!document.querySelector("#send-message").disabled', timeout=45000)
        conversation = page.request.get(URL+'/api/conversation/'+cid).json()
        run = conversation['agent_run']
        stats = run['statistics']
        (QA/'latest-run.json').write_text(json.dumps({'conversation':conversation,'snapshots':snapshots,'errors':errors},indent=2,ensure_ascii=False),encoding='utf-8')
        if run['status']!='completed':
            raise RuntimeError('Agent run did not complete; inspect latest-run.json before recording outputs.')
        scene('Measured execution', f"This run recorded {stats['skills_completed']} completed skill executions, covering {stats['distinct_skills']} different skills and {stats['delegated_people']} colleagues. It produced {stats['artifacts']} files. The dashboard also reports {stats['model_requests']} model requests and {stats['tool_calls']} tool calls. These are measured results from this run, not projected productivity gains.")
        focus('.agent-run-header'); wait(5)
        focus('.agent-run-footer'); wait(5)
        scene('Inspect the results', 'Every completed step links to its actual result. The activity record keeps the inputs and outputs, while the file library contains the generated launch pack. You can reopen the conversation later and inspect the same persisted execution record.')
        focus('.agent-plan-step.done button[data-run]')
        page.locator('.agent-plan-step.done button[data-run]').first.click()
        wait(5)
        page.locator('#run-dialog').evaluate('(el)=>el.scrollTop=el.scrollHeight')
        wait(5)
        page.locator('#run-dialog [data-close="run-dialog"]').first.click()
        page.locator('.sidebar [data-view="files"]').first.click(); wait(7)
        scene('One brief to a launch pack', 'Atlas Office makes agent work inspectable: one brief, a delegated plan, executable skills, and a finished set of business outputs. The GitHub repository includes the application, sixty-nine skill contracts, the API reference, and the evidence from this run. The business launch is simulated; the agent execution and generated deliverables are real.')
        page.locator('.sidebar [data-view="assistant"]').first.click()
        page.locator('.message.assistant').last.scroll_into_view_if_needed(); wait(6)
        focus('.agent-run-header'); wait(6)
        files = page.request.get(URL+'/api/files').json()
        artifact_dir = QA/('artifacts-'+cid)
        artifact_dir.mkdir()
        for f in files:
            (artifact_dir/f['name']).write_bytes(page.request.get(URL+f"/api/files/{f['id']}/download").body())
        current['end']=time.monotonic()-started
        data = {'scenes':scenes,'prompt':PROMPT,'conversation':conversation,'agent_run':run,'runs':page.request.get(URL+'/api/runs').json(),'records':page.request.get(URL+'/api/records').json(),'artifacts':files,'artifact_dir':str(artifact_dir),'snapshots':snapshots,'browser_errors':errors,'state_dir':str(DATA)}
        (QA/'recording.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
        raw=page.video.path(); context.close(); browser.close()
        (QA/'raw-path.txt').write_text(str(raw),encoding='utf-8')
        print('RECORDED',run['status'],stats,flush=True)
        if errors or run['status']!='completed':
            raise RuntimeError('The recorded run needs review; see local recording evidence.')
finally:
    server.terminate(); server.wait(timeout=10); log.close()
