"""Record a read-only product tour of the completed agent demo workspace."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[2]
SRC=BASE/'chengdu-tourism-office'
QA=BASE/'submission/qa/workspace-tour'
ORIGINAL=BASE/'submission/qa/agent-demo'
saved=json.loads((ORIGINAL/'recording.json').read_text(encoding='utf-8'))
APP=QA/'app'; DATA=QA/('state-'+str(int(time.time())))
QA.mkdir(parents=True,exist_ok=True)
for name in ('scripts','web','resources','shared','skills','examples'):
    shutil.copytree(SRC/name,APP/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.env'))
shutil.copy2(SRC/'app.py',APP/'app.py')
shutil.copytree(saved['state_dir'],DATA,ignore=shutil.ignore_patterns('.env','*credentials*','*token*'))
sys.path.insert(0,str(SRC/'scripts'))
from assistant_service import settings
config=settings(SRC)
env=dict(os.environ)
for key in list(env):
    if any(word in key.upper() for word in ('OPENAI','SMTP','TELEGRAM','GOOGLE','GMAIL')): env.pop(key)
env.update(OPENAI_API_KEY=config['api_key'],OPENAI_MODEL=config['model'],ATLAS_DATA_DIR=str(DATA),PYTHONIOENCODING='utf-8')
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(BASE/'submission/qa/video/pw-browsers')
URL='http://127.0.0.1:8879'
log=(QA/'server.log').open('w',encoding='utf-8')
server=subprocess.Popen([str(SRC/'.venv/Scripts/python.exe'),str(APP/'app.py'),'--port','8879','--data-dir',str(DATA)],cwd=APP,env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
for _ in range(60):
    try:
        with urlopen(URL+'/api/health',timeout=1) as r: r.read()
        break
    except Exception: time.sleep(.3)

scenes=[]; current=None; errors=[]; mutations=[]
def wait(seconds): page.wait_for_timeout(seconds*1000)
def scene(title,narration,placement):
    global current
    if current:
        current['end']=time.monotonic()-started
        page.screenshot(path=str(QA/(f'{len(scenes):02d}-end.png')))
    current={'title':title,'narration':narration,'placement':placement,'start':time.monotonic()-started,'kind':'workspace_review'}
    scenes.append(current); print('TOUR',len(scenes),title,flush=True)
def nav(view):
    page.locator(f'.sidebar [data-view="{view}"]').first.click()
    page.locator('#view-'+view+' h1').wait_for(state='visible')
    wait(.6)
def close(dialog): page.locator('#'+dialog+' [data-close="'+dialog+'"]').first.click()
def snapshot():
    return {key:page.request.get(URL+'/api/'+key).json() for key in ('runs','records','files')}

try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
        context=browser.new_context(viewport={'width':1600,'height':900},record_video_dir=str(QA/'raw'),record_video_size={'width':1600,'height':900})
        def readonly(route):
            if route.request.method not in ('GET','HEAD'):
                mutations.append(route.request.method+' '+route.request.url); route.abort()
            else: route.continue_()
        context.route('**/api/**',readonly)
        page=context.new_page(); page.on('pageerror',lambda e:errors.append(str(e)))
        started=time.monotonic()
        page.goto(URL,wait_until='networkidle'); page.wait_for_selector('body[data-ready="true"]')
        before=snapshot()

        scene('An organisation the agent can use','The organisation chart connects roles, reporting lines and capacity. Select a colleague to inspect their manager, available hours and assigned skills: the company context Atlas uses when delegating work.','after_intro')
        nav('organization')
        page.locator('[data-org-zoom]').press('Home'); wait(2)
        page.locator('.org-inspector [data-org-node="finance_manager"]').click(); wait(3)
        page.locator('[data-network="follows"]').click(); wait(3)

        scene('People with defined capabilities','The people directory makes each role inspectable. Search Finance to see Deng’s workload, reporting line and executable skills, all attached to the same fictional colleague used in the launch.','after_intro')
        nav('people'); wait(2)
        page.locator('#people-search').fill('finance'); wait(3)
        page.locator('#view-people .staff-card').first.scroll_into_view_if_needed(); wait(3)
        page.locator('#people-search').fill(''); wait(2)

        scene('Explore all 69 skills','The library contains sixty-nine executable skills. Filter by function, search for a capability, and inspect its instructions. These are the same skill contracts the agent reads and calls during the launch.','after_intro')
        nav('skills'); wait(2)
        page.locator('#skill-category').select_option('Finance'); wait(2)
        page.locator('#skill-search').fill('forecast'); wait(2)
        page.locator('[data-skill="finance-forecast"]').click()
        page.locator('.skill-instructions summary').click()
        page.locator('.skill-instructions').scroll_into_view_if_needed(); wait(4)
        close('skill-dialog')

        scene('Review the chosen approach','Open the recorded proposal to examine the approach: a fifty-thousand-renminbi pilot versus a hundred-and-twenty-thousand full launch. The actual result includes the recommendation, weighted scores and editable proposal files.','after_results')
        nav('activity')
        proposal=next(r for r in saved['runs'] if r['skill_id']=='proposal-package')
        page.locator('[data-run="'+proposal['id']+'"]').click()
        page.locator('#run-dialog h3').filter(has_text='Result').scroll_into_view_if_needed(); wait(3)
        page.locator('#run-dialog dt').filter(has_text='Ranking').scroll_into_view_if_needed(); wait(5)
        close('run-dialog')

        scene('Activity and approval visibility','Activity brings together all twenty recorded runs and their company records. Each result retains its inputs, output and assigned colleague. The review counter clearly distinguishes pending actions from completed work.','after_results')
        nav('activity'); wait(3)
        page.locator('#view-activity .section-title').filter(has_text='Company register').scroll_into_view_if_needed(); wait(4)
        page.locator('#view-activity h1').scroll_into_view_if_needed(); wait(2)

        scene('Files and reusable knowledge','The file library gathers the launch pack in one place. Search company knowledge to retrieve the saved launch note, carrying the decision, assumptions and evidence forward into future work.','after_results')
        nav('files'); wait(3)
        page.locator('#knowledge-query').scroll_into_view_if_needed()
        page.locator('#knowledge-query').fill('Chengdu'); wait(4)

        scene('Controls, connections and API','Settings expose tourism proposal modes and delivery permissions. Connections lists optional Google, Telegram and MCP services with their actual status. The API reference documents the same skills for integration.','before_outro')
        nav('settings')
        page.locator('.mode-grid').scroll_into_view_if_needed(); wait(4)
        nav('connections')
        page.locator('.connection-setup summary').click(); wait(3)
        page.locator('.connection-grid').scroll_into_view_if_needed(); wait(3)
        page.goto(URL+'/docs',wait_until='networkidle'); wait(4)

        current['end']=time.monotonic()-started
        page.screenshot(path=str(QA/'07-end.png'))
        after=snapshot()
        assert before==after,'Review must not change runs, records or files.'
        assert not mutations,mutations
        assert not errors,errors
        raw=page.video.path(); context.close(); browser.close()
        for s in scenes: s['source_video']=str(raw); s['voice_root']=str(QA)
        data={'scenes':scenes,'browser_errors':errors,'mutation_requests':mutations,'evidence_unchanged':before==after,'run_id':saved['agent_run']['id']}
        (QA/'recording.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
        print('TOUR VERIFIED',len(scenes),'sections; saved evidence unchanged',flush=True)
finally:
    server.terminate(); server.wait(timeout=10); log.close()
