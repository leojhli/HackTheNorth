"""Benchmark bookkeeping must not present an interrupted/error run as acceptance."""
import pytest
from scripts.check_practice_assessment import check_fixture_outputs, run, summarize


def test_synthetic_reference_results_match_node():
    results = check_fixture_outputs()
    assert len(results) == 6
    assert next(row for row in results if row['id'] == 'zero_capacity')['actual'] is False


def test_report_separates_wrong_grades_from_guarded_model_errors():
    rows = [
        dict(expected='pass', actual='pass', seconds=1),
        dict(expected='pass', actual='follow_up', seconds=2),
        dict(expected='follow_up', actual='pass', seconds=3),
        dict(expected='follow_up', actual='operational_failure', error='ungrounded_local_pass', seconds=4),
    ]
    result = summarize(rows, 24)
    assert not result['complete'] and not result['independent_review_completed']
    assert result['matching_agent_labels'] == 1 and result['false_passes'] == 1
    assert result['correct_answers_rejected'] == 1
    assert result['operational_failures'] == result['ungrounded_passes_blocked'] == 1
    assert result['p95_seconds'] == 4
    assert summarize([], 24)['p95_seconds'] is None


def test_rerun_cannot_replace_existing_failure_evidence(tmp_path):
    path = tmp_path / 'report.json'
    path.write_text('existing failure evidence', encoding='utf-8')
    with pytest.raises(FileExistsError):
        run(path)
    assert path.read_text(encoding='utf-8') == 'existing failure evidence'
