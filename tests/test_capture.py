import subprocess
from pathlib import Path
from integrations.capture import collect


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, check=True).stdout


def test_saved_capture_preserves_index_and_excludes_ignored_secrets(tmp_path):
    run(tmp_path, 'init')
    run(tmp_path, 'config', 'user.email', 'fixture@example.test')
    run(tmp_path, 'config', 'user.name', 'Fixture')
    (tmp_path/'src').mkdir()
    file = tmp_path/'src'/'a.ts'
    file.write_text('export const count = 1;\n')
    (tmp_path/'.gitignore').write_text('src/ignored.ts\n')
    run(tmp_path, 'add', '.')
    run(tmp_path, 'commit', '-m', 'fixture')
    file.write_text('export const count = 2;\n')
    run(tmp_path, 'add', 'src/a.ts')
    file.write_text('export const count = 3;\n')
    (tmp_path/'src'/'ignored.ts').write_text('export const privateValue = 123;')
    (tmp_path/'src'/'secret.ts').write_text('const token = "sensitiveValue123";')
    before = run(tmp_path, 'diff', '--cached')
    result = collect(tmp_path, ['src'], [])
    assert len(result['files']) == 1
    assert 'count = 3' in result['files'][0]['after']
    assert result['blocked'] == ['src/secret.ts']
    assert run(tmp_path, 'diff', '--cached') == before


def test_fresh_repository_includes_staged_saved_source(tmp_path):
    run(tmp_path, 'init')
    (tmp_path/'src').mkdir()
    (tmp_path/'src'/'first.ts').write_text('export const first = 1;\n')
    run(tmp_path, 'add', 'src/first.ts')
    index = run(tmp_path, 'ls-files', '--stage')
    result = collect(tmp_path, ['src'], [])
    assert len(result['files']) == 1 and result['files'][0]['before'] == ''
    assert run(tmp_path, 'ls-files', '--stage') == index
