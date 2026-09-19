"""Create a disposable Git fixture; never modifies the user's existing project/history."""
import subprocess
import uuid
from pathlib import Path

BEFORE = 'export function uniqueTags(tags) {\n  return [...tags];\n}\n'
AFTER = 'export function uniqueTags(tags) {\n  return [...new Set(tags)];\n}\n'


def main():
    root = Path('.tools/demo-workspaces', 'campus-events-' + uuid.uuid4().hex[:8]).resolve()
    (root / 'src').mkdir(parents=True)
    source = root / 'src' / 'uniqueTags.ts'
    source.write_text(BEFORE, encoding='utf-8')
    def git(*args):
        subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
    git('init')
    git('add', 'src/uniqueTags.ts')
    git('-c', 'user.name=BeProgram demo', '-c', 'user.email=demo@localhost', '-c', 'commit.gpgsign=false', 'commit', '-m', 'Demo baseline')
    source.write_text(AFTER, encoding='utf-8')
    print('Open this folder in VS Code, choose scope src, and review its saved change:')
    print(root)
    print('This is synthetic source for a real local-model demo. No passing history was seeded.')


if __name__ == '__main__':
    main()
