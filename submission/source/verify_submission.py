import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / 'chengdu-tourism-office'
OUT = BASE / 'submission/source/verification'
OUT.mkdir(parents=True, exist_ok=True)
commands = [
    ('tourism-behavior-tests', ['scripts/tourism_office.py', 'test']),
    ('automated-tests', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-q']),
    ('routing-evaluation', ['tests/trigger_eval.py']),
]
env = dict(os.environ)
env.update(PYTHONIOENCODING='utf-8', ATLAS_DATA_DIR=str(OUT / 'isolated-test-state'),
           OPENAI_API_KEY='', TELEGRAM_BOT_TOKEN='', SMTP_HOST='')
results = []
for name, args in commands:
    result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', env=env)
    content = 'COMMAND: python ' + ' '.join(args) + '\n' + result.stdout + result.stderr
    (OUT / (name + '.txt')).write_text(content, encoding='utf-8')
    results.append({'name': name, 'exit_code': result.returncode})
    print(name, result.returncode, content[-2200:])
(OUT / 'results.json').write_text(json.dumps({'date': '2026-09-27', 'results': results}, indent=2), encoding='utf-8')
