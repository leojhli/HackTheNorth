"""Create a disposable Git fixture; never modifies the user's existing project/history."""
import subprocess
import sys
import uuid
from pathlib import Path

TEMPLATE = Path(__file__).with_name('demo_template')
BEFORE = 'export function canJoin(guestCount, capacity) {\n  return true;\n}\n'
AFTER = (TEMPLATE / 'src/canJoin.js').read_text(encoding='utf-8')
DEMO_CASE = {
    'name': 'Demo: game night capacity', 'path': 'src/canJoin.js',
    'before': BEFORE, 'after': AFTER,
    'weak': 'It fixes the signup.',
    'good': 'This stops us adding more people when the event is full. If the number is five or more, it returns false, which means no. With four guests the check is false, so it reaches return true and someone can join. This function only checks for room; the button code actually adds the person.'
}


def main():
    root = Path('.tools/demo-workspaces', 'campus-events-' + uuid.uuid4().hex[:8]).resolve()
    root.mkdir(parents=True)
    for template in TEMPLATE.rglob('*'):
        if template.is_file() and '__pycache__' not in template.parts:
            target = root / template.relative_to(TEMPLATE)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(template.read_bytes())
    python = sys.executable.replace("'", "''")
    (root / 'start-demo.ps1').write_text(
        "$ErrorActionPreference = 'Stop'\n& '" + python + "' (Join-Path $PSScriptRoot 'serve.py')\n", encoding='utf-8')
    (root / '.gitignore').write_text('__pycache__/\n*.pyc\n', encoding='utf-8')
    source = root / 'src' / 'canJoin.js'
    source.write_text(BEFORE, encoding='utf-8')
    def git(*args):
        subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
    git('init')
    git('add', '.')
    git('-c', 'user.name=BeProgram demo', '-c', 'user.email=demo@localhost', '-c', 'commit.gpgsign=false', 'commit', '-m', 'Demo baseline')
    source.write_text(AFTER, encoding='utf-8')
    print('Open this folder in VS Code, choose scope src, and review its saved change:')
    print(root)
    print('Read START_HERE.md. Run ./start-demo.ps1 there to preview the event page.')
    print('This is synthetic source for a real local-model demo. No passing history was seeded.')


if __name__ == '__main__':
    main()
