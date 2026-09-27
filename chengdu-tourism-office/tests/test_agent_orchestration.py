"""Behavioral coverage for one-request orchestration and persisted measurements."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from company_chat import reply
from conversation_store import ConversationStore


class Runtime:
    def __init__(self, pending=False):
        self.submitted=[]
        self.pending=pending
    def catalog(self):
        return [{'id':'document-create','title':'Document','description':'Create a document','effect':'local_write'}]
    def skill_detail(self, sid):
        return {'id':sid,'input_schema':{'type':'object'}}
    def submit(self, sid, payload, person, idempotency_key):
        self.submitted.append(payload)
        return {'id':'run_'+str(len(self.submitted)),'skill_id':sid,'person_id':person,
                'status':'awaiting_approval' if self.pending else 'completed',
                'output':{} if self.pending else {'artifacts':[{'id':'file_'+str(len(self.submitted))}]}}


def call(name, **args):
    return NS(type='function_call',name=name,arguments=json.dumps(args),call_id='call_'+str(id(args)))


def response(*actions, text='Finished.'):
    return NS(output=list(actions),output_text=text,usage=NS(input_tokens=10,output_tokens=5,total_tokens=15))


class AgentTests(unittest.TestCase):
    def invoke(self, rt, responses, **kw):
        class Client:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            @property
            def responses(self): return self
            def create(self,**args): return next(iterator)
        iterator=iter(responses)
        company={'company':'Test','people':[{'id':'writer','name':'Writer','role':'Writer','skills':['document-create'],'available':True}]}
        with patch('company_chat.settings',return_value={'api_key':'test-key','model':'configured-model'}), patch('intent_router.route',return_value=None):
            return reply(rt,{'messages':[{'id':'message1','role':'user','content':'Create all the documents.'}]}, {'id':'atlas'}, company,client_factory=lambda **kwargs:Client(),**kw)

    def test_one_request_executes_beyond_old_limit_and_measures_usage(self):
        steps=[{'id':str(i),'title':'Document '+str(i),'skill_id':'document-create','person_id':'writer','depends_on':[str(i-1)] if i else []} for i in range(8)]
        responses=[response(call('set_plan',steps=steps)),response(call('read_skills',skill_ids=['document-create']))]
        responses += [response(call('run_skill',skill_id='document-create',person_id='writer',step_id=str(i),arguments_json=json.dumps({'title':str(i)}))) for i in range(8)]
        responses.append(response())
        snapshots=[]; rt=Runtime()
        answer=self.invoke(rt,responses,telemetry=snapshots.append)
        self.assertEqual(len(rt.submitted),8)
        run=answer['agent_run']; stats=run['statistics']
        self.assertEqual(run['status'],'completed')
        self.assertEqual((stats['skills_completed'],stats['artifacts'],stats['delegated_people']),(8,8,1))
        self.assertEqual((stats['model_requests'],stats['tool_calls'],stats['total_tokens']),(11,10,165))
        self.assertTrue(any(s['statistics']['skills_completed']==3 for s in snapshots))
        self.assertTrue(all(s['status']=='completed' for s in run['steps']))

    def test_pending_prerequisite_is_not_executed_or_counted_completed(self):
        steps=[{'id':'a','title':'First','skill_id':'document-create','person_id':'writer','depends_on':[]},
               {'id':'b','title':'Dependent','skill_id':'document-create','person_id':'writer','depends_on':['a']}]
        rt=Runtime(pending=True)
        answer=self.invoke(rt,[response(call('set_plan',steps=steps)),response(call('read_skill',skill_id='document-create')),
          response(call('run_skill',skill_id='document-create',person_id='writer',step_id='a',arguments_json='{}')),
          response(call('run_skill',skill_id='document-create',person_id='writer',step_id='b',arguments_json='{}')),response()])
        self.assertEqual(len(rt.submitted),1)
        self.assertEqual(answer['agent_run']['status'],'awaiting_approval')
        self.assertEqual(answer['agent_run']['statistics']['skills_executed'],0)
        self.assertEqual(answer['agent_run']['steps'][1]['status'],'blocked')

    def test_unread_skill_cannot_execute(self):
        rt=Runtime()
        answer=self.invoke(rt,[response(call('run_skill',skill_id='document-create',person_id='writer',step_id='',arguments_json='{}')),response()])
        self.assertFalse(rt.submitted)
        self.assertEqual(answer['agent_run']['calls'][0]['status'],'failed')
        self.assertEqual(answer['agent_run']['status'],'needs_attention')

    def test_unfinished_plan_never_reports_completed(self):
        answer=self.invoke(Runtime(),[response(call('set_plan',steps=[{'id':'a','title':'Draft','skill_id':'document-create','person_id':'writer','depends_on':[]}])),response()])
        self.assertEqual(answer['agent_run']['status'],'needs_attention')
        self.assertEqual(answer['agent_run']['steps'][0]['status'],'blocked')

    def test_persisted_run_reopens_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'conversation.sqlite'
            store=ConversationStore(path); cid=store.create('Test')['id']
            measured={'status':'completed','statistics':{'skills_completed':2,'total_tokens':123}}
            store.save_agent_run(cid,measured)
            self.assertEqual(ConversationStore(path).get(cid)['agent_run'],measured)
            with self.assertRaises(FileNotFoundError): store.save_agent_run('missing',measured)


if __name__=='__main__': unittest.main()
