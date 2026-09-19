"""Selected GitHub operations through Composio's documented authenticated proxy.

No arbitrary tools/URLs, no assistant-generated writes, no automatic write retry.
"""
import base64
import re
import time
from urllib.parse import quote, urlparse
from typing import Literal
import httpx
from pydantic import Field
from sqlalchemy import select
from .contracts import Strict, FileChange
from .context import digest, eligible, safe_path, capture
from .db import Project, Checkpoint, Operation
from .service import owned, PASSING
from .errors import AppError


class PRInput(Strict):
    project_id: str
    repository: str = Field(pattern=r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
    number: int = Field(ge=1, le=10000000)


class SummaryInput(Strict):
    checkpoint_ids: list[str] = Field(min_length=1, max_length=20)


class PublishInput(Strict):
    preview_id: str
    approved_digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    consent: Literal[True]


class ComposioGitHub:
    def __init__(self, config):
        self.config = config

    def core(self, method, path, body=None):
        if not self.config.composio_api_key or not self.config.composio_github_auth_config_id:
            raise AppError('github_unconfigured', 'Configure the Composio GitHub auth integration on the server.', 503)
        try:
            r = httpx.request(method, 'https://backend.composio.dev/api/v3.1'+path,
                headers={'x-api-key': self.config.composio_api_key}, json=body, timeout=20)
            r.raise_for_status()
            return r.json() if r.content else {}
        except Exception:
            raise AppError('github_unavailable', 'Composio/GitHub is unavailable or access was denied. No automatic publication retry will occur.', 503, True) from None

    def link(self, owner):
        result = self.core('POST', '/connected_accounts/link', {'user_id': owner, 'auth_config_id': self.config.composio_github_auth_config_id,
            'callback_url': self.config.app_origin.rstrip('/')+'/settings'})
        redirect = result.get('redirect_url', '')
        url = urlparse(redirect)
        if url.scheme != 'https' or not (url.hostname == 'composio.dev' or (url.hostname or '').endswith('.composio.dev')):
            raise AppError('connection_invalid', 'Provider returned an unexpected authentication URL.', 503)
        return {'redirect_url': redirect, 'connection_id': result.get('connected_account_id')}

    def connection(self, owner):
        result = self.core('GET', '/connected_accounts?user_ids='+quote(owner, safe='')+'&toolkit_slugs=github&statuses=ACTIVE')
        accounts = [c for c in result.get('items', []) if c.get('user_id') == owner and c.get('toolkit', {}).get('slug') == 'github'
                    and c.get('auth_config', {}).get('id') == self.config.composio_github_auth_config_id and c.get('status') == 'ACTIVE' and not c.get('is_disabled')]
        if len(accounts) != 1:
            raise AppError('github_connection_required', 'Connect exactly one GitHub account for this BeProgram user and auth configuration.', 409)
        return accounts[0]['id']

    def proxy(self, owner, endpoint, method='GET', body=None):
        connection = self.connection(owner)  # Re-check ownership and revocation before every external operation.
        result = self.core('POST', '/tools/execute/proxy', {'connected_account_id': connection, 'endpoint': endpoint,
            'method': method, 'body': body, 'parameters': [{'name': 'Accept', 'value': 'application/vnd.github+json', 'type': 'header'},
                {'name': 'X-GitHub-Api-Version', 'value': '2022-11-28', 'type': 'header'}]})
        if not isinstance(result.get('status'), int) or not 200 <= result['status'] < 300:
            raise AppError('github_permission_or_response', 'GitHub rejected the selected operation. Check repository permissions.', 502, True)
        return result['data']

    def pr(self, owner, repository, number):
        result = self.proxy(owner, f'/repos/{repository}/pulls/{number}')
        if result['base']['repo']['full_name'].casefold() != repository.casefold() or result['number'] != number:
            raise AppError('wrong_repository', 'Provider returned a different PR destination.', 409)
        return result

    def comments(self, owner, repository, number):
        comments = []
        for page in range(1, 6):
            batch = self.proxy(owner, f'/repos/{repository}/issues/{number}/comments?per_page=100&page={page}')
            if not isinstance(batch, list):
                raise AppError('invalid_comments', 'Cannot reconcile the remote comment list.', 503, True)
            comments.extend(batch)
            if len(batch) < 100:
                return comments
        raise AppError('reconciliation_limit', 'More than 500 comments; reconcile manually before publishing again.', 409)

    def publish(self, owner, repository, number, body):
        return self.proxy(owner, f'/repos/{repository}/issues/{number}/comments', 'POST', {'body': body})

    def unlink(self, owner):
        connection = self.connection(owner)
        self.core('DELETE', '/connected_accounts/'+quote(connection, safe=''))
        return {'disconnected': True, 'remote_comments_removed': False}


class GitHubService:
    def __init__(self, core, adapter):
        self.core, self.adapter, self.database = core, adapter, core.database

    def import_pr(self, owner, data):
        with self.core.serial(owner) as lease:
            with self.database.transaction() as db:
                project = owned(db, Project, data.project_id, owner)
            pr = self.adapter.pr(owner, data.repository, data.number)
            if pr.get('changed_files', 101) > 100:
                raise AppError('pr_too_large', 'Choose a PR with at most 100 changed files for this bounded prototype.', 422)
            head, base = pr['head']['sha'], pr['base']['sha']
            paths = self.adapter.proxy(owner, f'/repos/{data.repository}/pulls/{data.number}/files?per_page=100')
            selected = [f for f in paths if eligible(f['filename'], project.scope, project.exclusions)]
            if not selected or len(selected) > 30:
                raise AppError('pr_scope', 'Select a project scope containing 1–30 eligible PR files.', 422)
            files = []
            for f in selected:
                def content(repository, name, sha):
                    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
                        raise AppError('invalid_repo', 'Invalid repository returned by provider.', 502)
                    value = self.adapter.proxy(owner, f'/repos/{repository}/contents/{quote(safe_path(name), safe="/")}?ref={quote(sha, safe="")}')
                    if value.get('type') != 'file' or value.get('encoding') != 'base64' or value.get('size', 100001) > 100000:
                        raise AppError('pr_file_bounds', 'An approved PR file exceeds the saved context bounds.', 422)
                    return base64.b64decode(value['content']).decode('utf-8')
                before = '' if f['status'] == 'added' else content(data.repository, f.get('previous_filename', f['filename']), base)
                after = '' if f['status'] == 'removed' else content(pr['head']['repo']['full_name'], f['filename'], head)
                file = FileChange(path=f['filename'], before=before, after=after)
                if capture([file], project.scope, project.exclusions)['files']:
                    files.append(file.model_dump())
            if not files:
                raise AppError('no_eligible_changes', 'No eligible meaningful PR changes remained after filtering.', 422)
            # Prevent mixing a changed pull-request files listing with an older head snapshot.
            if self.adapter.pr(owner, data.repository, data.number)['head']['sha'] != head:
                raise AppError('stale_pr_head', 'The PR changed while importing. Import it again.', 409, True)
            key = digest({'project': project.id, 'repository': data.repository, 'number': data.number, 'head': head, 'files': files})
            with self.database.transaction() as db:
                self.core.verify_lease(db, owner, lease)
                op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'github_import', Operation.key == key))
                if not op:
                    op = Operation(owner=owner, project_id=project.id, kind='github_import', key=key, state='imported',
                        payload={'repository': data.repository, 'number': data.number, 'head': head, 'base': base,
                            'title': pr.get('title', '')[:300], 'included_files': [f['path'] for f in files], 'partial': len(files) < len(paths)}, result={'files': files})
                    db.add(op); db.flush()
                return {'id': op.id, **op.payload, 'capture': {'files': files, 'pr_import_id': op.id, 'provenance': 'unknown', 'idempotency_key': key}}

    def preview(self, owner, data):
        with self.core.serial(owner), self.database.transaction() as db:
            checkpoints = [owned(db, Checkpoint, id, owner) for id in sorted(set(data.checkpoint_ids))]
            if any(c.status not in PASSING or not c.snapshot.get('pr_import_id') for c in checkpoints):
                raise AppError('publication_scope', 'Select only passed checkpoints from an imported PR.', 409)
            refs = [c.snapshot['pr'] for c in checkpoints]
            if any(r['repository'] != refs[0]['repository'] or r['number'] != refs[0]['number'] or r['head'] != refs[0]['head'] for r in refs):
                raise AppError('publication_scope', 'All selected checkpoints must refer to the same repository, PR and frozen head.', 409)
            ref = refs[0]
            key = digest({'checkpoints': [(c.id,c.version) for c in checkpoints], 'repository': ref['repository'], 'number': ref['number'], 'head': ref['head']})
            existing = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'publication', Operation.key == key))
            if existing:
                if existing.state == 'awaiting_consent':
                    existing.payload = {**existing.payload, 'expires': int(time.time())+600}
                return self.public(existing)
            def clean(value):
                return re.sub(r'[^\w .()/\-]', '', value)[:120]
            body = '### BeProgram comprehension summary\n\nReviewed commit: `' + ref['head'] + '`\n\nConcepts demonstrated on selected captured changes:\n'
            body += '\n'.join('- ' + clean(c.question['concept']) for c in checkpoints)
            body += f'\n\nCoverage: {len(checkpoints)} selected checkpoint(s), bounded excerpts only. This does not cover the entire PR or prove authorship or general mastery. Private answers, retries and source excerpts are excluded.'
            marker = '<!-- beprogram-publication:'+key+' -->'
            body += '\n\n'+marker
            payload = {'repository': ref['repository'], 'number': ref['number'], 'head': ref['head'], 'body': body,
                'marker': marker, 'checkpoint_ids': [c.id for c in checkpoints], 'expires': int(time.time())+600}
            payload['digest'] = digest({k:payload[k] for k in ('repository','number','head','body','checkpoint_ids')})
            op = Operation(owner=owner, project_id=checkpoints[0].project_id, kind='publication', key=key, state='awaiting_consent', payload=payload)
            db.add(op); db.flush()
            return self.public(op)

    def public(self, op):
        return {'id':op.id,'state':op.state,**{k:op.payload[k] for k in ('repository','number','head','body','digest','expires')},'result':op.result}

    def get(self, owner, id):
        with self.database.transaction() as db:
            op = owned(db, Operation, id, owner)
            if op.kind != 'publication':
                raise AppError('not_found', 'Publication not found.', 404)
            return self.public(op)

    def publish(self, owner, data):
        with self.core.serial(owner) as lease:
            with self.database.transaction() as db:
                op = owned(db, Operation, data.preview_id, owner)
                if op.kind != 'publication' or op.payload['digest'] != data.approved_digest:
                    raise AppError('preview_mismatch', 'Approve the exact comment and destination.', 409)
                if op.state == 'published':
                    return self.public(op)
                p = op.payload
                if p['expires'] < time.time() and op.state == 'awaiting_consent':
                    raise AppError('preview_expired', 'This publication preview expired. Refresh the preview.', 409)
            # A remote marker is reconciled even if the PR head subsequently changes.
            comments = self.adapter.comments(owner, p['repository'], p['number'])
            existing = next((c for c in comments if p['marker'] in c.get('body', '') and c.get('body') == p['body']), None)
            if existing:
                return self.persist(owner, op.id, existing, lease)
            if op.state in ('submitting','uncertain'):
                raise AppError('publication_uncertain', 'No matching comment is visible yet. Publication remains uncertain; it will not be posted twice. Reconcile later or inspect the PR manually.', 409, True)
            pr = self.adapter.pr(owner, p['repository'], p['number'])
            if pr['head']['sha'] != p['head']:
                raise AppError('stale_pr_head', 'This PR has new commits. Import the current head and regenerate the summary.', 409)
            with self.database.transaction() as db:
                self.core.verify_lease(db, owner, lease)
                row = owned(db, Operation, op.id, owner); row.state = 'submitting'
            try:
                remote = self.adapter.publish(owner, p['repository'], p['number'], p['body'])
                return self.persist(owner, op.id, remote, lease)
            except Exception:
                with self.database.transaction() as db:
                    row = owned(db, Operation, op.id, owner); row.state = 'uncertain'
                raise AppError('publication_uncertain', 'The publication result is uncertain. Reconcile this same preview; do not create a new comment.', 503, True) from None

    def persist(self, owner, id, remote, lease):
        url = remote.get('html_url', '')
        with self.database.transaction() as db:
            self.core.verify_lease(db, owner, lease)
            row = owned(db, Operation, id, owner)
            expected = f"https://github.com/{row.payload['repository']}/pull/{row.payload['number']}#issuecomment-"
            if not url.startswith(expected) or not isinstance(remote.get('id'), int):
                raise AppError('publication_response', 'Unexpected comment reference. Reconcile the intended PR.', 503, True)
            row.state, row.result = 'published', {'comment_id':remote['id'],'url':url}
            return self.public(row)
