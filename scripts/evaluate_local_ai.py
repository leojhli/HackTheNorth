"""20 actual-model evaluations with frozen agent labels and a human-review worksheet."""
import hashlib
import json
import math
import time
import shutil
import uuid
from pathlib import Path
from types import SimpleNamespace
from backend.assessment import LocalAssessor
from backend.config import Settings
from backend.context import capture
from backend.contracts import FileChange, Question
from backend.errors import AppError
from scripts.assessment_cases import CASES


def main(model=None, output='docs/assessment-review'):
    assessor = LocalAssessor(Settings(**({'ollama_model': model} if model else {})))
    assessor.ready()
    report = {'model': assessor.model_id, 'dataset_sha256': hashlib.sha256(Path('scripts/assessment_cases.py').read_bytes()).hexdigest(),
              'assessor_sha256': hashlib.sha256(Path('backend/assessment.py').read_bytes()).hexdigest(),
              'method': 'Actual local evaluations, fixed authored questions/rubrics. Agent labels, no human review. No question-generation benchmark.',
              'cases': []}
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    # Preserve annotations and previous measurements on later reruns.
    if (out / 'HUMAN_REVIEW.md').exists():
        archive = out / ('previous-' + uuid.uuid4().hex[:8])
        archive.mkdir()
        shutil.copyfile(out / 'HUMAN_REVIEW.md', archive / 'HUMAN_REVIEW.md')
        if (out / 'results.json').exists():
            shutil.copyfile(out / 'results.json', archive / 'results.json')
    for group in CASES:
        snapshot = capture([FileChange(path='src/example.ts', before=group['before'], after=group['after'])], ['src'], [])
        question = Question(decision='assess', concept=group['concept'], question=group['question'], reason='Behavior changes in the visible source.',
            rubric=group['rubric'], evidence=[{'path': 'src/example.ts', 'start_line': 1, 'end_line': 1, 'quote': group['after']}], important_distinct_use=False)
        cp = SimpleNamespace(snapshot=snapshot, question=question.model_dump())
        for kind, expected, answer in group['answers']:
            started = time.monotonic()
            entry = {'id': group['id'] + '-' + kind, 'kind': kind, 'expected': expected, 'answer': answer,
                     'before': group['before'], 'after': group['after'], 'question': group['question'], 'rubric': group['rubric']}
            try:
                result = assessor.evaluate(cp, [], answer)
                entry.update(actual=result.decision, evaluation=result.model_dump())
            except AppError as exc:
                entry.update(actual='operational_failure', error=exc.code)
            entry['seconds'] = round(time.monotonic() - started, 3)
            entry['matches_agent_label'] = entry['actual'] == expected
            report['cases'].append(entry)
            (out / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            print(entry['id'], 'expected=' + expected, 'actual=' + entry['actual'], entry['seconds'], flush=True)
    rows = report['cases']
    latencies = sorted(r['seconds'] for r in rows)
    report['summary'] = {
        'total': len(rows), 'matching_agent_labels': sum(r['matches_agent_label'] for r in rows),
        'false_passes': sum(r['expected'] != 'pass' and r['actual'] == 'pass' for r in rows),
        'complete_answers_not_passed': sum(r['expected'] == 'pass' and r['actual'] != 'pass' for r in rows),
        'operational_failures': sum(r['actual'] == 'operational_failure' for r in rows),
        'evaluation_p95_seconds': latencies[math.ceil(.95 * len(rows)) - 1],
        'human_review_completed': False,
    }
    (out / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    worksheet = ['# Assessment review worksheet', '',
        'Actual local model results against 20 fixed synthetic explanations. Expected labels were authored by the coding agent before this run. This is not completed human review or a production accuracy estimate.', '',
        'Reviewer: ______  Date: ______', '',
        'For each case, independently judge the code/answer before considering the model feedback. Record pass, follow-up or unable-to-assess, whether feedback is correct, and whether it reveals too much. Disagreements stay visible.', '',
        '## Run summary', '', '```json', json.dumps(report['summary'], indent=2), '```', '']
    for r in rows:
        worksheet += ['## ' + r['id'], '', 'Before:', '```javascript', r['before'], '```', 'After:', '```javascript', r['after'], '```',
            '**Question:** ' + r['question'], '', '**Rubric:** ' + '; '.join(r['rubric']), '', '**Explanation:** ' + r['answer'], '',
            '**Human decision / reason (fill in):** ______', '',
            '**Agent label:** ' + r['expected'] + ' | **Model/server outcome:** ' + r['actual'], '',
            '**Feedback:** ' + r.get('evaluation', {}).get('feedback', r.get('error', '')), '',
            '**Human feedback-quality notes (fill in):** ______', '']
    (out / 'HUMAN_REVIEW.md').write_text('\n'.join(worksheet), encoding='utf-8')
    print(json.dumps(report['summary']), flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Installed local model allowed by backend settings; does not change .env.')
    parser.add_argument('--output', default='docs/assessment-review')
    args = parser.parse_args()
    main(args.model, args.output)
