"""Summarize a person's exported review; never changes application grades."""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(report_path, review_path):
    raw = Path(report_path).read_bytes()
    report, review = json.loads(raw), json.loads(Path(review_path).read_text(encoding='utf-8'))
    if review.get('schema') != 'beprogram-human-review-v1' or review.get('report_sha256') != hashlib.sha256(raw).hexdigest():
        raise ValueError('The review belongs to a different report; use the exact report shown in its worksheet.')
    rows = review.get('cases', [])
    expected = {c['id']: c for c in report['cases']}
    if len(rows) != len(expected) or {r.get('id') for r in rows} != set(expected):
        raise ValueError('Review case IDs are missing, duplicated or unexpected.')
    complete = bool(str(review.get('reviewer', '')).strip()) and all(
        r.get('decision') in {'pass', 'follow_up', 'unsure'} and
        r.get('feedback_quality') in {'yes', 'no', 'unsure', 'unavailable'} for r in rows)
    return {'review_complete': complete, 'reviewer': review.get('reviewer', ''), 'cases': len(rows),
        'uncertain_verdicts': sum(r.get('decision') == 'unsure' for r in rows),
        'feedback_concerns': [r['id'] for r in rows if r.get('feedback_quality') != 'yes'],
        'model_disagreements': [r['id'] for r in rows if r.get('decision') in {'pass', 'follow_up'} and r['decision'] != expected[r['id']]['actual']],
        'note': 'Human-entered decisions; completion does not mean all model-quality concerns are resolved.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review')
    parser.add_argument('--report', default='docs/release-review/final/results.json')
    args = parser.parse_args()
    result = summarize(args.report, args.review)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['review_complete'] else 1)
