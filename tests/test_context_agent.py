from types import SimpleNamespace
import json
import pytest
from backend.context_agent import ContextAgent, dependencies
from backend.errors import AppError


CONTEXT = {'files':[
    {'path':'src/main.js','lines':[{'number':1,'text':'import {limit} from "./limit.js"; export const full = n => n >= limit;'}]},
    {'path':'src/limit.js','lines':[{'number':1,'text':'export const limit = 5;'}]},
    {'path':'src/noise.js','lines':[{'number':1,'text':'UNRELATED_MARKER'}]},
], 'partial':True}


def assessor(actions):
    calls = []
    def generate(messages, schema, timeout_seconds):
        assert 0 < timeout_seconds <= 120
        calls.append(json.loads(messages[1]['content']))
        action = next(actions)
        tool = 'inspect_module:' + action['path'] if action['action']=='inspect_module' else action['action']
        # Deliberately allow malformed mock choices to exercise application checks.
        return SimpleNamespace(tool=tool, missing_context=action['path'] if action['action']=='need_context' else '')
    def answer(prompt, context, timeout):
        calls.append(context)
        return 'At five it is full.'
    return SimpleNamespace(config=SimpleNamespace(operation_timeout=120),generate=generate,answer_from_context=answer), calls


def test_agent_selects_dependency_after_read_and_excludes_unrelated_source():
    model, calls = assessor(iter([
        dict(action='inspect_module',path='src/main.js'),
    ]))
    result = ContextAgent(model).run('Is five full?', CONTEXT)
    assert 'read_excerpts' not in calls[0]
    assert 'UNRELATED_MARKER' not in json.dumps(calls)
    assert result['outcome']=='answered' and result['read_paths']==['src/main.js','src/limit.js']
    assert len(calls[-1]['files']) == 2


@pytest.mark.parametrize('actions', [
    [dict(action='inspect_module',path='../.env')],
    [dict(action='answer',path='')],
])
def test_unknown_or_unread_context_cannot_produce_answer(actions):
    model, calls = assessor(iter(actions))
    with pytest.raises(AppError, match='invalid_context_action'):
        ContextAgent(model).run('Help', CONTEXT)
    assert not any('files' in c for c in calls)


def test_missing_context_returns_actionable_request_without_reading_extra_files():
    model, calls = assessor(iter([dict(action='need_context',path='src/missing.js')]))
    result = ContextAgent(model).run('What does missing do?', CONTEXT)
    assert result['outcome']=='needs_context' and result['read_paths']==[]
    assert 'approve' in result['text'] and 'src/missing.js' in result['text']
    assert len(calls)==1


def test_import_resolution_stays_in_inventory_and_refuses_ambiguity():
    def source(text): return {'path':'src/main.js','lines':[{'number':1,'text':text}]}
    assert dependencies(source('import x from "./limit";'), {'src/limit.js':{}})==(['src/limit.js'],[])
    assert dependencies(source('import x from "./limit";'), {'src/limit.js':{},'src/limit.ts':{}})[1]==['ambiguous module src/limit']
    assert dependencies(source('import x from "../../private.js";'), {})[1]==['missing module ../private.js']
    assert dependencies(source('import x from "some-package";'), {})[1]==['external module some-package']


def test_dependency_limit_and_cycles_are_bounded():
    def file(path,text):return {'path':path,'lines':[{'number':1,'text':text}]}
    model,calls=assessor(iter([dict(action='inspect_module',path='src/a.js')]))
    context={'files':[file('src/a.js','import b from "./b.js";'),file('src/b.js','import a from "./a.js";')],'partial':False}
    result=ContextAgent(model).run('Explain a',context)
    assert result['outcome']=='answered' and len(result['read_paths'])==2
    model,calls=assessor(iter([dict(action='inspect_module',path='src/a.js')]))
    context={'files':[file('src/'+a+'.js','import x from "./'+b+'.js";') for a,b in [('a','b'),('b','c'),('c','d'),('d','a')]],'partial':False}
    result=ContextAgent(model).run('Explain a',context)
    assert result['outcome']=='needs_context' and len(result['read_paths'])==3
    assert len(calls)==1  # No guessed final answer after reaching the limit.
