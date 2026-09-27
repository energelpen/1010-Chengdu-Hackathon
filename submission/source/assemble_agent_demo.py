"""Create a clean full-frame startup demo from the actual one-request recording."""
from pathlib import Path
import json, subprocess, re, shutil, sys
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'submission'; QA=OUT/'qa/agent-demo'
FF=OUT/'qa/video/pw-browsers/ffmpeg-1011/ffmpeg-win64.exe'
raw=Path((QA/'raw-path.txt').read_text(encoding='utf-8'))
data=json.loads((QA/'narrated.json').read_text(encoding='utf-8'))
assert data['agent_run']['status']=='completed'
if '--with-tour' in sys.argv:
    tour=json.loads((OUT/'qa/workspace-tour/narrated.json').read_text(encoding='utf-8'))
    assert tour['evidence_unchanged'] and not tour['browser_errors'] and not tour['mutation_requests']
    original=data['scenes']; combined=[]
    for index,chapter in enumerate(original):
        if index==len(original)-1:
            combined.extend(s for s in tour['scenes'] if s['placement']=='before_outro')
        combined.append(chapter)
        if index==0:
            combined.extend(s for s in tour['scenes'] if s['placement']=='after_intro')
        if chapter['title']=='Inspect the results':
            combined.extend(s for s in tour['scenes'] if s['placement']=='after_results')
    data['scenes']=combined
    data['workspace_tour']={k:tour[k] for k in ('evidence_unchanged','browser_errors','mutation_requests','run_id')}
    data['workspace_tour']['chapters']=[s['title'] for s in tour['scenes']]
assert sum(s['audio_duration']+1.2 for s in data['scenes'])<300,'Narration exceeds the five-minute submission limit.'
segments=[]; cursor=0; subtitles=[]
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)

def stamp(t):
    ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for i,s in enumerate(data['scenes']):
    scene_raw=Path(s.get('source_video',str(raw)))
    voice_root=Path(s.get('voice_root',str(QA)))
    length=s['end']-s['start']; duration=s['audio_duration']+1.2
    s['video_start']=cursor; s['video_duration']=duration
    title=Image.new('RGBA',(1600,900),(0,0,0,0)); d=ImageDraw.Draw(title)
    width=int(d.textlength(s['title'],font=font))+48
    d.rounded_rectangle((280,18,280+width,74),radius=12,fill='#163F35')
    d.text((304,29),s['title'],font=font,fill='white')
    png=QA/f'title-{i:02d}.png'; title.save(png)
    label=Image.new('RGBA',(1600,900),(0,0,0,0)); d=ImageDraw.Draw(label)
    d.rounded_rectangle((1468,18,1580,50),radius=9,fill='#F5F4EB')
    d.text((1483,23),'Simulation',font=small,fill='#466853')
    badge=QA/'simulation.png'; label.save(badge)
    output=QA/f'chapter-{i:02d}.mp4'
    filter=f'[0:v]setpts=(PTS-STARTPTS)*{duration/length},fps=25[v];[v][2:v]overlay=0:0:enable=lt(t\\,3)[t];[t][3:v]overlay=0:0,format=yuv420p[out];[1:a]apad[a]'
    subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-ss',str(s['start']),'-t',str(length),'-i',str(scene_raw),'-i',str(voice_root/s['voice_file']),'-i',str(png),'-i',str(badge),'-filter_complex',filter,'-map','[out]','-map','[a]','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','128k','-ar','44100','-movflags','+faststart',str(output)],check=True)
    segments.append(output)
    sentences=re.split(r'(?<=[.!?])\s+',s['narration']); weight=sum(len(x) for x in sentences); t=cursor
    for sentence in sentences:
        end=t+s['audio_duration']*len(sentence)/weight
        subtitles.append(f'{len(subtitles)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n'); t=end
    cursor+=duration
    print('Encoded',i,round(cursor,1),flush=True)
concat=QA/'chapters.txt'; concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in segments),encoding='utf-8')
sub=OUT/'03-implementation-demo.srt'; sub.write_text('\n'.join(subtitles),encoding='utf-8')
final=OUT/'03-implementation-demo.mp4'
subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(sub),'-map','0:v','-map','0:a','-map','1:0','-c:v','copy','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(final)],check=True)
data['final_duration']=cursor
(QA/'final-metadata.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
E=OUT/'evidence'; E.mkdir(exist_ok=True)
destination=(E/'generated-files').resolve()
assert destination.is_relative_to(BASE.resolve()) and destination.name=='generated-files'
destination.mkdir(exist_ok=True)
for p in destination.iterdir():
    if p.is_file(): p.unlink()
shutil.copytree(data['artifact_dir'],destination,dirs_exist_ok=True)
public={k:data[k] for k in ('prompt','agent_run','runs','records','artifacts','voice')}
public.update(scenario='Product Launch Preparation',mode='Real model-led local execution of a business simulation',distinct_skills=data['agent_run']['statistics']['distinct_skills'],recorded_date='2026-09-27',recording_notes='Single user request. Waiting periods compressed; synthetic English narration. No manual skill submissions.',answer=data['conversation']['messages'][-1]['content'])
if 'workspace_tour' in data:
    public['workspace_tour']=data['workspace_tour']
    public['recording_notes']+=' Additional website sections are shown through read-only inspection of a copy of the completed workspace; run evidence is unchanged.'
(E/'launch-execution.json').write_text(json.dumps(public,indent=2,ensure_ascii=False),encoding='utf-8')
(E/'agent-timeline.json').write_text(json.dumps(data['snapshots'],indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Atlas Office — agent-led implementation demo','','Repository: https://github.com/energelpen/1010-Chengdu-Hackathon','','One request triggers a real configured model, a model-authored plan and actual skill execution. The business launch is explicitly simulated. The additional product tour inspects the organisation, people, skill contracts, proposal, activity, files, knowledge, settings, connections and API in a copy of the completed workspace. It does not submit skills or approval decisions. Waiting periods are compressed and synthetic English narration is added. The clean video has brief chapter titles and a small Simulation badge.','','## Measured run','','```json',json.dumps(data['agent_run']['statistics'],indent=2),'```','']
for s in data['scenes']:
    lines+=['## '+stamp(s['video_start']).split(',')[0]+' — '+s['title'],'',s['narration'],'']
lines+=['## Reproduction and evidence','','See `evidence/launch-execution.json`, `evidence/agent-timeline.json` and `evidence/generated-files/`. `record_agent_demo.py` starts an isolated app, passes the configured API key only through the server environment, submits one prompt and records the genuine UI. It needs an authorized API account, Playwright and Edge. `record_workspace_tour.py` copies that saved state, blocks browser mutation requests and verifies the runs, records and files are unchanged. `voice_full_demo.py --agent` and `--tour` generate narration; `assemble_agent_demo.py --with-tour` edits both recordings with FFmpeg. No keys or runtime databases enter the submission.','','The run is evidence for this scenario, not a general reliability rate. It does not establish a real market launch, supplier verification, enterprise adoption or external delivery.']
(OUT/'demo-script.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'source/demo-prompt.md').write_text('# Recorded agent request\n\nSubmit this as one message to Atlas in the General company template, using an authorized configured API connection. The model chooses the skills and inputs; results can vary between runs.\n\n'+data['prompt']+'\n',encoding='utf-8')
print('FINAL',round(cursor,2),final.stat().st_size)
