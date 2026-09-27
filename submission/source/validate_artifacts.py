from pathlib import Path
import json, re, subprocess, hashlib, sys
from PIL import Image,ImageDraw,ImageFont
from pypdf import PdfReader
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'submission'; QA=OUT/'qa/final-validation'
QA.mkdir(parents=True,exist_ok=True)
FF=OUT/'qa/video/pw-browsers/ffmpeg-1011/ffmpeg-win64.exe'
POP=Path(r'C:\Users\ask\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
metadata=json.loads((OUT/'qa/agent-demo/final-metadata.json').read_text(encoding='utf-8'))
manifest={'repository':'https://github.com/energelpen/1010-Chengdu-Hackathon','created':'2026-09-27','files':[],'demo_mode':'Real agent-led execution of one business simulation request; narrated recording with compressed waits','agent_statistics':metadata['agent_run']['statistics']}
for file,limit in [('01-skill-function-description.pdf',30000000),('02-api-documentation.pdf',30000000),('03-implementation-demo.mp4',200000000),('04-enterprise-challenge-fit.pdf',30000000),('05-entry-cover.png',5000000)]:
    p=OUT/file; size=p.stat().st_size; assert 0<size<limit
    row={'file':file,'bytes':size,'limit_bytes':limit,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix=='.pdf':
        reader=PdfReader(p); row['pages']=len(reader.pages)
        assert all((page.extract_text() or '').strip() for page in reader.pages)
        if '--video-only' in sys.argv:
            manifest['files'].append(row)
            continue
        folder=QA/p.stem; folder.mkdir(exist_ok=True)
        subprocess.run([str(POP),'-r','90','-png',str(p),str(folder/'page')],check=True,capture_output=True)
        images=sorted(folder.glob('page-*.png'))
        for start in range(0,len(images),6):
            group=images[start:start+6]; contact=Image.new('RGB',(1080,520*((len(group)+2)//3)),'#ccd8df'); d=ImageDraw.Draw(contact)
            for i,src in enumerate(group):
                im=Image.open(src); im.thumbnail((350,490)); x=(i%3)*360+(360-im.width)//2; y=(i//3)*520+23
                contact.paste(im,(x,y)); d.text(((i%3)*360+12,(i//3)*520+5),src.name,fill='black')
            contact.save(QA/(p.stem+f'-contact-{start//6+1}.png'))
    manifest['files'].append(row)
summary=(OUT/'06-entry-summary.txt').read_text(encoding='utf-8'); assert len(summary)<=3000 and len(summary.split())<=2000
manifest['summary']={'file':'06-entry-summary.txt','characters':len(summary),'limit':3000,'words':len(summary.split()),'word_limit':2000}
manifest['video']={'duration_seconds':round(metadata['final_duration'],2),'maximum_seconds':300,'distinct_skills':len({r['skill_id'] for r in metadata['runs']}),'voice':metadata['voice'],'format':'H.264 video, AAC audio, embedded English subtitles','dimensions':[1600,900]}
if 'workspace_tour' in metadata: manifest['workspace_tour']=metadata['workspace_tour']
assert metadata['final_duration']<300
probe=subprocess.run([str(FF),'-hide_banner','-i',str(OUT/'03-implementation-demo.mp4'),'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
assert probe.returncode==0
assert 'Audio: aac' in probe.stderr and 'Video: h264' in probe.stderr and 'mean_volume: -inf' not in probe.stderr
(QA/'video-decode.txt').write_text(probe.stderr,encoding='utf-8')
times=[s['video_start']+s['video_duration']*.82 for s in metadata['scenes']]
contact=Image.new('RGB',(1200,250*((len(times)+2)//3)),'#172332')
for i,t in enumerate(times):
    frame=QA/f'video-{i:02d}.png'
    subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(OUT/'03-implementation-demo.mp4'),'-frames:v','1',str(frame)],check=True)
    im=Image.open(frame); im.thumbnail((400,250)); contact.paste(im,((i%3)*400,(i//3)*250))
contact.save(QA/'video-contact.png')
(OUT/'submission-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
