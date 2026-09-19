"""Actual local tool-selection evidence on synthetic multi-file snapshots."""
import hashlib
import json
import time
from pathlib import Path
from backend.assessment import LocalAssessor
from backend.config import Settings
from backend.context_agent import ContextAgent
from backend.errors import AppError


def file(path, text):
    return {'path':path,'lines':[{'number':i+1,'text':line} for i,line in enumerate(text.splitlines())]}


def main(output):
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        stream.write('{}')
    main_file=file('src/main.js','import { limit } from "./limit.js";\nexport function full(n) { return n >= limit; }')
    limit_file=file('src/limit.js','// Old note: capacity used to be 100.\nexport const limit = 5;')
    noise=file('src/colors.js','export const colors = ["blue", "red"];')
    cases=[('dependency_and_stale_comment',{'files':[main_file,limit_file,noise],'partial':False},'answered'),
           ('missing_dependency',{'files':[main_file,noise],'partial':True},'needs_context')]
    assessor=LocalAssessor(Settings())
    report={'model':assessor.model_id,'agent_sha256':hashlib.sha256(Path('backend/context_agent.py').read_bytes()).hexdigest(),
        'method':'Actual local tool decisions; synthetic approved excerpts. Expected routes are agent-authored. Text correctness needs separate review. No user project or remote service accessed.', 'cases':[]}
    try:
        for name,context,expected in cases:
            began=time.monotonic()
            entry={'name':name,'approved_context':context,'expected_outcome':expected}
            decisions=[]
            original=assessor.generate
            def record_decision(*args,**kwargs):
                result=original(*args,**kwargs)
                if hasattr(result,'action') or hasattr(result,'tool'):
                    decisions.append(result.model_dump())
                return result
            assessor.generate=record_decision
            try:
                result=ContextAgent(assessor).run('For full(5), does src/main.js return true or false? Explain the actual comparison.',context)
                entry.update(result)
                entry['route_matches']=result['outcome']==expected and (expected!='answered' or set(result['read_paths'])=={'src/main.js','src/limit.js'})
            except AppError as exc:
                entry.update(outcome='operational_failure',error=exc.code,route_matches=False)
            finally:
                assessor.generate=original
                entry['observed_tool_decisions']=decisions
            entry['seconds']=round(time.monotonic()-began,3)
            report['cases'].append(entry)
            path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            print(name,entry['outcome'],entry['route_matches'],flush=True)
    finally:
        report['complete']=len(report['cases'])==len(cases)
        report['routes_match']=report['complete'] and all(c['route_matches'] for c in report['cases'])
        report['independent_quality_review']=False
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report['routes_match']


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='docs/release-review/context-agent-'+str(time.time_ns())+'.json')
    raise SystemExit(0 if main(parser.parse_args().output) else 1)
