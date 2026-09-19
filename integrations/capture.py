"""Saved working tree vs HEAD capture. Preview first; explicit --submit uploads approved scope."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import httpx
from backend.context import eligible, capture, digest
from backend.contracts import FileChange


def git(root, *args, check=True):
    return subprocess.run(['git', '-C', str(root), *args], check=check, capture_output=True).stdout


def collect(root: Path, scope: list[str], exclusions: list[str]):
    root = root.resolve()
    actual = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if actual != root:
        raise ValueError('Choose the Git repository root explicitly.')
    head = git(root, 'rev-parse', '--verify', 'HEAD', check=False).strip()
    names = (git(root, 'diff', 'HEAD', '--name-only', '-z') if head else git(root, 'ls-files', '--cached', '-z')).split(b'\0')
    names += git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0')
    changes, blocked = [], []
    for raw in sorted(set(names)):
        if not raw:
            continue
        name = raw.decode('utf-8', errors='strict').replace('\\', '/')
        if not eligible(name, scope, exclusions):
            continue
        if subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '-q', '--', name]).returncode == 0:
            continue
        path = root / name
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            blocked.append(name)
            continue
        if path.exists() and path.stat().st_size > 100_000:
            blocked.append(name)
            continue
        try:
            before = git(root, 'show', f'HEAD:{name}', check=False).decode('utf-8')
            after = path.read_text(encoding='utf-8') if path.is_file() else ''
            file = FileChange(path=name, before=before, after=after)
            checked = capture([file], scope, exclusions)
            if checked['files']:
                changes.append(file.model_dump())
            elif any(s['reason'] == 'binary_or_possible_secret' for s in checked['skipped']):
                blocked.append(name)
        except (UnicodeError, ValueError):
            blocked.append(name)
    if len(changes) > 30:
        raise ValueError('More than 30 files changed. Narrow the approved scope before uploading.')
    return {'files': changes, 'blocked': blocked, 'provenance': 'user_reported_manual',
            'idempotency_key': digest(changes), 'saved_files_only': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--scope', action='append', required=True, help='Approved relative file/directory (repeatable)')
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--api', default='http://127.0.0.1:8000')
    parser.add_argument('--session')
    parser.add_argument('--submit', action='store_true', help='Upload the explicitly scoped saved changes')
    parser.add_argument('--ask', help='Reconcile saved changes before requesting managed AI')
    args = parser.parse_args()
    payload = collect(args.repository, args.scope, args.exclude)
    if not args.submit:
        print(json.dumps(payload, indent=2))
        return
    if not args.session or not os.getenv('BEPROGRAM_TOKEN'):
        parser.error('--submit requires --session and BEPROGRAM_TOKEN in the environment')
    if payload['blocked']:
        parser.error('Blocked files require narrower scope or an explicit exclusion before submission.')
    if not args.api.startswith(('https://', 'http://127.0.0.1:', 'http://localhost:')):
        parser.error('Use HTTPS or a loopback API address')
    headers = {'Authorization': 'Bearer ' + os.environ['BEPROGRAM_TOKEN']}
    with httpx.Client(base_url=args.api, headers=headers, timeout=135) as client:
        if payload['files']:
            result = client.post(f'/v1/sessions/{args.session}/changes', json={k: payload[k] for k in ('files', 'provenance', 'idempotency_key')})
            result.raise_for_status()
            print(json.dumps(result.json(), indent=2))
        gate = client.get(f'/v1/sessions/{args.session}/gate')
        gate.raise_for_status()
        if args.ask:
            if not gate.json()['available']:
                raise SystemExit('Checkpoint unresolved. Open BeProgram to explain the change before managed Ask AI.')
            result = client.post(f'/v1/sessions/{args.session}/ask', json={'prompt': args.ask, 'idempotency_key': str(uuid.uuid4())})
            result.raise_for_status()
            print(result.json()['text'])


if __name__ == '__main__':
    main()
