"""Synchronize actual recorded chapters with narration; preserve honest scope labels."""
from pathlib import Path
import json, subprocess, re, shutil
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'submission'; QA=OUT/'qa/full-demo'
FF=OUT/'qa/video/pw-browsers/ffmpeg-1011/ffmpeg-win64.exe'
raw=Path((QA/'raw-path.txt').read_text(encoding='utf-8'))
data=json.loads((QA/'narrated.json').read_text(encoding='utf-8'))
segments=[]; cursor=0; subtitles=[]
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',26)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
def stamp(t):
    ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for i,s in enumerate(data['scenes']):
    length=s['end']-s['start']; duration=s['audio_duration']+1.2
    s['video_start']=cursor; s['video_duration']=duration
    band=Image.new('RGBA',(1600,1000),(0,0,0,0)); d=ImageDraw.Draw(band)
    d.rectangle((0,900,1600,1000),fill='#102235')
    d.text((30,917),s['title'],font=font,fill='#8FE4D5')
    d.text((30,960),'ACTUAL APP RECORDING  |  OPERATOR-LED SIMULATION  |  EDITED FOR PACING  |  SYNTHETIC VOICE',font=small,fill='#DBE8EE')
    d.text((1260,925),'ATLAS OFFICE',font=font,fill='white')
    png=QA/f'band-{i:02d}.png'; band.save(png)
    output=QA/f'chapter-{i:02d}.mp4'
    cmd=[str(FF),'-hide_banner','-loglevel','error','-y','-ss',str(s['start']),'-t',str(length),'-i',str(raw),'-i',str(QA/s['voice_file']),'-i',str(png),'-filter_complex',f'[0:v]setpts=(PTS-STARTPTS)*{duration/length},fps=25,pad=1600:1000:0:0:color=0x102235[v];[v][2:v]overlay=0:0,format=yuv420p[out];[1:a]apad[a]','-map','[out]','-map','[a]','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','128k','-ar','44100','-movflags','+faststart',str(output)]
    subprocess.run(cmd,check=True)
    segments.append(output)
    sentences=re.split(r'(?<=[.!?])\s+',s['narration'])
    weight=sum(len(x) for x in sentences); t=cursor
    for sentence in sentences:
        end=t+s['audio_duration']*len(sentence)/weight
        subtitles.append(f'{len(subtitles)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n')
        t=end
    cursor+=duration
    print('Encoded',i,round(cursor,1),flush=True)
concat=QA/'chapters.txt'; concat.write_text('\n'.join("file '"+str(p.as_posix())+"'" for p in segments),encoding='utf-8')
sub=OUT/'03-implementation-demo.srt'; sub.write_text('\n'.join(subtitles),encoding='utf-8')
final=OUT/'03-implementation-demo.mp4'
subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(sub),'-map','0:v','-map','0:a','-map','1:0','-c:v','copy','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(final)],check=True)
data['final_duration']=cursor
(QA/'final-metadata.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
E=OUT/'evidence'; E.mkdir(exist_ok=True)
shutil.copytree(QA/'artifacts',E/'generated-files',dirs_exist_ok=True)
public={k:data[k] for k in ('runs','records','artifacts','voice')}
public.update(scenario='Product Launch Preparation',mode='Operator-led local simulation',distinct_skills=len({x['skill_id'] for x in data['runs']}),recorded_date='2026-09-27')
(E/'launch-execution.json').write_text(json.dumps(public,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Atlas Office narrated implementation demo','','Repository: https://github.com/energelpen/1010-Chengdu-Hackathon','','This is an edited recording of actual UI operations, with synthetic English narration. All business inputs and completion statements are simulation data. The operator invokes each skill; automatic one-sentence launch completion is not claimed.','','The recording demonstrates 13 different skills, with a genuine approval transition for a reviewed spreadsheet change.','']
for s in data['scenes']:
    lines+=['## '+stamp(s['video_start']).split(',')[0]+' - '+s['title'],'',s['narration'],'']
lines+=['## Reproduction and evidence','','See `evidence/launch-execution.json` for actual run records and `evidence/generated-files/` for outputs. The source recorder uses an isolated copy and new data directory, without credentials. `record_full_demo.py` records the UI, `voice_full_demo.py` renders narration using Windows SAPI, and `assemble_full_demo.py` synchronizes chapters. Browser automation requires Playwright and Edge; encoding requires FFmpeg. Paths are configured at the start of these scripts.','','The automatic full single-sentence launch lifecycle, live provider integrations, employee identity and real enterprise validation remain outside the demonstrated scope.']
(OUT/'demo-script.md').write_text('\n'.join(lines),encoding='utf-8')
print('FINAL',round(cursor,2),final.stat().st_size)
