import difflib
import fnmatch
import hashlib
import json
import re
from pathlib import PurePosixPath
from .errors import AppError

EXCLUDED = {'.git', 'node_modules', 'dist', 'build', 'coverage', 'vendor', '.next', '__pycache__', '.venv', '.tools'}
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})|(?:api[_-]?key|password|secret|token)\s*[:=]\s*[\x22\x27][^\x22\x27\s]{8,}', re.I)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def safe_path(path):
    p = PurePosixPath(path.replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or ':' in path or not p.parts or path.startswith('~') or '\x00' in path:
        raise AppError('invalid_path', 'Use relative paths inside the approved project.')
    return p.as_posix()


def eligible(path, scope, exclusions):
    path = safe_path(path)
    parts = PurePosixPath(path).parts
    if any(p.lower() in EXCLUDED or p.lower().startswith('.env') for p in parts):
        return False
    if not path.endswith(('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs')) or path.endswith(('.min.js', '.d.ts', '.generated.ts')):
        return False
    def matches(rule):
        rule = rule.rstrip('/')
        return rule == '.' or path == rule or path.startswith(rule + '/') or fnmatch.fnmatchcase(path, rule)
    return any(matches(p) for p in scope) and not any(matches(p) for p in exclusions)


def capture(files, scope, exclusions):
    result, skipped, changed, context = [], [], 0, 0
    partial = False
    for item in sorted(files, key=lambda f: f.path):
        path = safe_path(item.path)
        if not eligible(path, scope, exclusions):
            skipped.append({'path': path, 'reason': 'excluded_or_outside_scope'})
            continue
        if '\x00' in item.before + item.after or SECRET.search(item.before + item.after):
            skipped.append({'path': path, 'reason': 'binary_or_possible_secret'})
            continue
        # Only remove whitespace outside string literals: stripping all whitespace can hide SQL/string changes.
        plain_lines = '`' not in item.before + item.after and '\\' not in item.before + item.after
        if item.before == item.after or (plain_lines and [s.strip() for s in item.before.splitlines() if s.strip()] == [s.strip() for s in item.after.splitlines() if s.strip()]):
            skipped.append({'path': path, 'reason': 'whitespace_only'})
            continue
        before, after = item.before.splitlines(), item.after.splitlines()
        matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
        ranges, edits = set(), []
        for tag, i, j, k, l in matcher.get_opcodes():
            if tag == 'equal':
                continue
            count = (j-i) + (l-k)
            if changed + count > 200:
                partial = True
                remaining = 200 - changed
                if remaining <= 0:
                    continue
                # Retain a bounded prefix from both sides, instead of silently treating a large edit as trivial.
                take_before = min(j-i, remaining // 2 if l-k else remaining)
                take_after = min(l-k, remaining-take_before)
                j, l = i+take_before, k+take_after
                count = take_before+take_after
            changed += count
            edits.append({'before_start': i+1, 'after_start': k+1, 'removed': before[i:j], 'added': after[k:l]})
            ranges.update(range(max(0, k-5), min(len(after), max(k+1, l)+5)))
        if not edits:
            continue
        lines = []
        for n in sorted(ranges):
            if context >= 300:
                partial = True
                break
            lines.append({'number': n+1, 'text': after[n]})
            context += 1
        result.append({'path': path, 'edits': edits, 'lines': lines, 'full_change_hash': digest({'before': item.before, 'after': item.after})})
    return {'files': result, 'changed_lines': changed, 'context_lines': context, 'partial': partial, 'skipped': skipped}


def validate_evidence(question, snapshot):
    for evidence in question.evidence:
        file = next((f for f in snapshot['files'] if f['path'] == evidence.path), None)
        if not file or evidence.end_line < evidence.start_line:
            raise ValueError('Unknown evidence span')
        lines = {line['number']: line['text'] for line in file['lines']}
        if any(n not in lines for n in range(evidence.start_line, evidence.end_line+1)):
            raise ValueError('Evidence outside captured context')
        if evidence.quote not in '\n'.join(lines[n] for n in range(evidence.start_line, evidence.end_line+1)):
            raise ValueError('Evidence quote not in source')
