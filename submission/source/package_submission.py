"""Package only reviewed, non-ignored source and the six upload deliverables."""
from pathlib import Path
import subprocess, zipfile, json, re, hashlib
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'submission'
raw=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=BASE)
files=sorted(set(p.decode('utf-8') for p in raw.split(b'\0') if p))
bad=[]; suspect=[]
for rel in files:
    p=BASE/rel
    if p.is_symlink(): bad.append(rel); continue
    if (p.name=='.env' or (p.name.startswith('.env.') and p.name!='.env.example') or p.suffix=='.sqlite' or any(x in p.parts for x in ('.venv','node_modules','__pycache__'))): bad.append(rel)
    if p.suffix.lower() in ('.py','.js','.mjs','.json','.md','.txt','.html','.ps1') or p.name=='.env.example':
        body=p.read_text(encoding='utf-8',errors='replace')
        if re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b',body): suspect.append(rel)
assert not bad, 'Excluded data in package candidates: '+str(bad)
assert not suspect, 'Potential credential in candidates: '+str(suspect)
source=OUT/'atlas-office-skills-source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for rel in files:
        if rel.startswith('chengdu-tourism-office/'): z.write(BASE/rel,rel)
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    skills=[n for n in z.namelist() if n.startswith('chengdu-tourism-office/skills/') and n.endswith('/SKILL.md')]
    assert len(skills)==69
uploads=['01-skill-function-description.pdf','02-api-documentation.pdf','03-implementation-demo.mp4','03-implementation-demo.srt','04-enterprise-challenge-fit.pdf','05-entry-cover.png','06-entry-summary.txt','README.md','demo-script.md','atlas-office-skills-source.zip','submission-manifest.json']
bundle=OUT/'atlas-office-submission.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in uploads: z.write(OUT/name,'atlas-office-submission/'+name)
    for p in (OUT/'evidence').rglob('*'):
        if p.is_file(): z.write(p,'atlas-office-submission/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(bundle) as z: assert z.testzip() is None
print(json.dumps({'publication_candidates':len(files),'source_bytes':source.stat().st_size,'source_skills':len(skills),'bundle_bytes':bundle.stat().st_size,'credential_scan':'no token patterns detected in candidate text files'},indent=2))
