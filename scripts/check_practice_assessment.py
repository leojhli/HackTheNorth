"""Reproducible live local practice benchmark; never reads or changes user history."""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from backend.assessment import LocalAssessor
from backend.config import Settings
from backend.context import capture
from backend.contracts import FileChange, Question
from backend.errors import AppError
from scripts.practice_cases import CASES, answers

ROOT = Path(__file__).resolve().parents[1]


def check_fixture_outputs():
    """Execute only fixed, reviewed repository fixtures; no model/user source."""
    bundled = sorted((ROOT / '.tools/node').glob('*/node.exe'))
    node = shutil.which('node') or (str(bundled[-1]) if bundled else None)
    if not node:
        raise RuntimeError('Node is required to check the synthetic expected values.')
    results = []
    for case in CASES:
        script = case['after'] + '\nconsole.log(JSON.stringify(' + case['invocation'] + '));'
        proc = subprocess.run([node, '--input-type=module'], input=script, text=True,
                              capture_output=True, timeout=10, check=True)
        actual = json.loads(proc.stdout)
        # Preserve JSON types: False must not match numeric zero in Python.
        if json.dumps(actual, sort_keys=True) != json.dumps(case['expected_value'], sort_keys=True):
            raise ValueError('Synthetic fixture expectation mismatch: ' + case['id'])
        results.append({'id': case['id'], 'invocation': case['invocation'], 'actual': actual})
    return results


def summarize(rows, expected_total):
    times = sorted(row['seconds'] for row in rows)
    return {
        'complete': len(rows) == expected_total,
        'total': len(rows), 'expected_total': expected_total,
        'matching_agent_labels': sum(row['actual'] == row['expected'] for row in rows),
        'false_passes': sum(row['expected'] != 'pass' and row['actual'] == 'pass' for row in rows),
        'correct_answers_rejected': sum(row['expected'] == 'pass' and row['actual'] == 'follow_up' for row in rows),
        'operational_failures': sum(row['actual'] == 'operational_failure' for row in rows),
        'ungrounded_passes_blocked': sum(row.get('error') == 'ungrounded_local_pass' for row in rows),
        'p95_seconds': times[math.ceil(.95 * len(times)) - 1] if times else None,
        'independent_review_completed': False,
    }


def run(output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: a rerun cannot silently erase a failure report.
    with path.open('x', encoding='utf-8') as stream:
        stream.write('{}\n')
    report = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'method': 'Fixed agent-authored practice questions and labels. Node checks only synthetic output values; it does not validate explanation grading. No generated-question or independent human accuracy claim.',
        'dataset_sha256': hashlib.sha256((ROOT / 'scripts/practice_cases.py').read_bytes()).hexdigest(),
        'assessor_sha256': hashlib.sha256((ROOT / 'backend/assessment.py').read_bytes()).hexdigest(),
        'cases': [],
    }
    total = sum(len(answers(case)) for case in CASES)

    def save():
        report['summary'] = summarize(report['cases'], total)
        path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    try:
        save()
        report['fixture_outputs'] = check_fixture_outputs()
        assessor = LocalAssessor(Settings())
        report['model'] = assessor.model_id
        report['context_size'] = assessor.config.ollama_context
        assessor.ready()
        for case in CASES:
            snapshot = capture([FileChange(path='src/example.js', before=case['before'], after=case['after'])], ['src'], [])
            question = Question(decision='assess', concept=case['concept'], question=case['question'],
                reason='Apply the saved mechanism to a specific new input.', rubric=case['rubric'],
                evidence=[{'path': 'src/example.js', 'start_line': 1, 'end_line': 1, 'quote': case['after']}],
                important_distinct_use=False)
            checkpoint = SimpleNamespace(snapshot=snapshot, question=question.model_dump(), practice=True)
            for kind, expected, answer in answers(case):
                row = {'id': case['id'] + '-' + kind, 'kind': kind, 'expected': expected,
                       'answer': answer, 'source': case['after'], 'question': question.model_dump()}
                began = time.monotonic()
                try:
                    evaluation = assessor.evaluate(checkpoint, [], answer)
                    row.update(actual=evaluation.decision, evaluation=evaluation.model_dump())
                except AppError as exc:
                    row.update(actual='operational_failure', error=exc.code)
                row['seconds'] = round(time.monotonic() - began, 3)
                report['cases'].append(row)
                save()
                print(row['id'], 'expected=' + expected, 'actual=' + row['actual'], flush=True)
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    finally:
        save()
    print(json.dumps(report['summary']), flush=True)
    return report['summary']['complete'] and all(row['actual'] == row['expected'] for row in report['cases'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='docs/release-review/practice-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json',
                        help='New report path; existing reports are never overwritten.')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output) else 1)
