"""Render chapter narration locally with installed Windows SAPI voices."""
from pathlib import Path
import json, wave
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa/full-demo'
data=json.loads((QA/'recording.json').read_text(encoding='utf-8'))
voice=win32com.client.Dispatch('SAPI.SpVoice')
tokens=voice.GetVoices()
choices=[tokens.Item(i) for i in range(tokens.Count)]
token=next((t for t in choices if 'Zira' in t.GetDescription()),choices[0])
voice.Voice=token; voice.Rate=0; voice.Volume=100
for i,s in enumerate(data['scenes']):
    output=QA/f'voice-{i:02d}.wav'
    stream=win32com.client.Dispatch('SAPI.SpFileStream')
    stream.Open(str(output),3,False); voice.AudioOutputStream=stream
    voice.Speak(s['narration']); stream.Close()
    with wave.open(str(output),'rb') as w: s['audio_duration']=w.getnframes()/w.getframerate()
    s['voice_file']=output.name
    print(i,s['audio_duration'],flush=True)
data['voice']={'engine':'Windows SAPI','name':token.GetDescription(),'synthetic':True}
(QA/'narrated.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
