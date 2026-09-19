"""Build an offline human-review worksheet from a completed actual-model report."""
import argparse
import hashlib
import json
from pathlib import Path

TEMPLATE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CodeProof human review</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f7f8;color:#172c28;font:16px/1.6 system-ui,sans-serif}
main{max-width:900px;margin:32px auto;padding:0 20px}h1{line-height:1.2}h2{font-size:20px}
header{position:sticky;top:0;background:#fff;padding:12px 20px;border-bottom:1px solid #ccd8d0;display:flex;flex-wrap:wrap;gap:16px;align-items:center;z-index:1}
button{background:#215a43;color:white;border:0;border-radius:8px;padding:10px 16px;font:inherit;cursor:pointer}
button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #d88b00;outline-offset:2px}
article{background:white;border:1px solid #d5ded8;border-radius:16px;padding:24px;margin:24px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef2ef;padding:12px;border-radius:8px;font-size:14px}
blockquote{margin:12px 0;padding:12px 16px;border-left:3px solid #215a43;background:#f3f6f2}
label{display:block;margin:12px 0}select,input,textarea{font:inherit;padding:8px;border:1px solid #9aac9f;border-radius:6px;max-width:100%}textarea{width:100%;min-height:70px}details{margin:18px 0}summary{cursor:pointer;font-weight:650}.muted{color:#50655a;font-size:14px}
</style>
<header><strong id="progress">0 / 20 reviewed</strong><button id="export" type="button">Save review file</button><span id="saved" role="status"></span></header>
<main><h1>Review CodeProof's assessments</h1>
<p>For each example, read the code and explanation. Choose your own verdict first, then open the model result and judge its feedback. You can choose <strong>Unsure</strong>; do not guess. Agent labels are comparison data, not an answer key.</p>
<p>This page works offline, sends nothing, and never changes a CodeProof grade. Progress is saved in this browser when available. Use <strong>Save review file</strong> to export it into the project's <code>docs/release-review</code> folder. Partial exports remain labeled incomplete.</p>
<p id="provenance" class="muted"></p><label>Your name or initials <input id="reviewer" autocomplete="off"></label>
<section id="cases"></section></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const source=JSON.parse(document.getElementById('data').textContent);
const key='beprogram-human-review:'+source.report_sha256;
let state={reviewer:'',cases:{}};
try{state=JSON.parse(localStorage.getItem(key))||state}catch{}
if(!state.cases||typeof state.cases!=='object')state={reviewer:'',cases:{}};
const $=id=>document.getElementById(id);
function element(tag,text,parent){const el=document.createElement(tag);el.textContent=text;if(parent)parent.append(el);return el}
function select(parent,label,key,entry,options){const el=element('label',label+' ',parent), input=document.createElement('select');el.append(input);for(const [value,text] of options){const o=element('option',text,input);o.value=value}input.value=entry[key]||'';input.addEventListener('change',()=>{entry[key]=input.value;save()});return input}
function complete(entry){return !!entry?.decision&&!!entry?.feedback_quality}
function save(){let n=source.cases.filter(c=>complete(state.cases[c.id])).length;$('progress').textContent=n+' / '+source.cases.length+' reviewed';try{localStorage.setItem(key,JSON.stringify(state));$('saved').textContent='Progress saved in this browser.'}catch{$('saved').textContent='Use Save review file to keep your progress.'}}
$('provenance').textContent='Model: '+source.model+'. Fixed synthetic examples; this set was used during development and is not held-out accuracy. Report: '+source.report_sha256.slice(0,12);
$('reviewer').value=state.reviewer||'';$('reviewer').addEventListener('input',()=>{state.reviewer=$('reviewer').value;save()});
source.cases.forEach((c,index)=>{
 const entry=state.cases[c.id]||{decision:'',feedback_quality:'',notes:''};state.cases[c.id]=entry;
 const card=element('article','',$('cases'));element('h2',(index+1)+'. '+c.id,card);
 element('strong','Before',card);element('pre',c.before,card);element('strong','After',card);element('pre',c.after,card);
 element('p','Question: '+c.question,card);element('strong','Learner explanation',card);element('blockquote',c.answer,card);
 select(card,'Your verdict','decision',entry,[['','Choose...'],['pass','Sufficient explanation'],['follow_up','Needs a follow-up'],['unsure','Unsure / needs an expert']]);
 const details=element('details','',card);element('summary','Open the model result after choosing your verdict',details);
 element('p','Model outcome: '+c.actual+'. Agent expectation: '+c.expected+'.',details);
 element('p',c.evaluation?.feedback||('Operational error: '+(c.error||'unavailable')),details);
 if(c.evaluation?.next_question)element('p','Follow-up: '+c.evaluation.next_question,details);
 select(card,'Is the feedback accurate and relevant?','feedback_quality',entry,[['','Choose...'],['yes','Yes'],['no','No'],['unsure','Unsure'],['unavailable','No feedback: operational failure']]);
 const label=element('label','Notes (optional)',card),notes=element('textarea','',label);notes.value=entry.notes||'';notes.addEventListener('input',()=>{entry.notes=notes.value;save()});
});
$('export').addEventListener('click',()=>{
 const rows=source.cases.map(c=>({id:c.id,...state.cases[c.id]}));
 const completed=!!state.reviewer.trim()&&rows.every(complete);
 const output={schema:'beprogram-human-review-v1',report_sha256:source.report_sha256,model:source.model,dataset_sha256:source.dataset_sha256,assessor_sha256:source.assessor_sha256,reviewer:state.reviewer,exported_at:new Date().toISOString(),completed,cases:rows};
 const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='human-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 $('saved').textContent=completed?'Complete review exported. Uncertain/disputed cases still need resolution.':'Partial review exported; fill all verdicts, feedback checks and your initials to complete.';
});
save();
</script></html>'''


def build(report_path, output):
    data = Path(report_path).read_bytes()
    report = json.loads(data)
    if report.get('summary', {}).get('total') != 20 or len(report.get('cases', [])) != 20:
        raise ValueError('Use a completed 20-case report, not partial results.')
    report['report_sha256'] = hashlib.sha256(data).hexdigest()
    # Untrusted code/model output never becomes HTML or executable JavaScript.
    encoded = json.dumps(report, ensure_ascii=True).replace('<', '\\u003c')
    Path(output).write_text(TEMPLATE.replace('__DATA__', encoded), encoding='utf-8')
    print('Offline human review:', Path(output).resolve())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', default='docs/release-review/final/results.json')
    parser.add_argument('--output', default='docs/release-review/HUMAN_REVIEW.html')
    args = parser.parse_args()
    build(args.report, args.output)
