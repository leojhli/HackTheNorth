import time
from types import SimpleNamespace
from contextlib import contextmanager
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from .db import Project, CodingSession, Checkpoint, Attempt, Operation, Lease, RateWindow, uid
from .context import capture, digest, validate_evidence, eligible
from .contracts import Question, Evaluation
from .errors import AppError

PASSING = {'passed', 'passed_with_help'}
RESOLVED = PASSING | {'skipped'}


def owned(db, model, id, owner):
    item = db.get(model, id)
    if not item or item.owner != owner:
        raise AppError('not_found', 'This record is not available.', 404)
    return item


def record(item):
    value = {col.name: getattr(item, col.name) for col in item.__table__.columns if col.name != 'owner'}
    if isinstance(item, Project):
        value['scope_hash'] = digest({'name': item.name, 'scope': item.scope, 'exclusions': item.exclusions})
    return value


class CheckpointService:
    def __init__(self, database, assessor, config):
        self.database, self.assessor, self.config = database, assessor, config

    @contextmanager
    def serial(self, owner):
        """Database lease: one inference operation per owner, including across server workers."""
        token, now = uid(), time.time()
        try:
            with self.database.transaction() as db:
                db.execute(delete(Lease).where(Lease.owner == owner, Lease.expires < now))
                db.add(Lease(owner=owner, token=token, expires=now+self.config.lease_seconds))
                db.flush()
                rate = db.get(RateWindow, owner)
                if rate and rate.started > now-60:
                    if rate.count >= 30:
                        raise AppError('rate_limited', 'Too many operations. Wait a minute before retrying.', 429, True)
                    rate.count += 1
                elif rate:
                    rate.started, rate.count = now, 1
                else:
                    db.add(RateWindow(owner=owner, started=now, count=1))
        except IntegrityError:
            raise AppError('operation_busy', 'An operation is still processing. Reconcile or retry shortly.', 409, True) from None
        try:
            yield token
        finally:
            with self.database.transaction() as db:
                db.execute(delete(Lease).where(Lease.owner == owner, Lease.token == token))

    def verify_lease(self, db, owner, token):
        lease = db.get(Lease, owner)
        if not lease or lease.token != token or lease.expires < time.time():
            raise AppError('stale_operation', 'This operation expired. Reconcile before retrying.', 409, True)

    def projects(self, owner):
        with self.database.transaction() as db:
            return [record(p) for p in db.scalars(select(Project).where(Project.owner == owner).order_by(Project.created.desc()))]

    def create_project(self, owner, data):
        with self.serial(owner), self.database.transaction() as db:
            project = Project(owner=owner, **data.model_dump())
            db.add(project)
            db.flush()
            return record(project)

    def update_scope(self, owner, id, data):
        with self.serial(owner), self.database.transaction() as db:
            project = owned(db, Project, id, owner)
            desired = data.model_dump(exclude={'expected_scope_hash'})
            if record(project)['scope_hash'] != data.expected_scope_hash and record(project)['scope_hash'] != digest(desired):
                raise AppError('stale_scope', 'Project settings changed. Refresh before saving.', 409)
            project.name, project.scope, project.exclusions = data.name, data.scope, data.exclusions
            return record(project)

    def start(self, owner, project_id):
        with self.serial(owner), self.database.transaction() as db:
            owned(db, Project, project_id, owner)
            existing = db.scalar(select(CodingSession).where(CodingSession.owner == owner, CodingSession.status == 'active'))
            if existing:
                if existing.project_id != project_id:
                    raise AppError('active_session', 'End the active session before starting another project.', 409)
                return record(existing)
            session = CodingSession(owner=owner, project_id=project_id)
            db.add(session)
            db.flush()
            return record(session)

    def sessions(self, owner):
        with self.database.transaction() as db:
            return [record(s) for s in db.scalars(select(CodingSession).where(CodingSession.owner == owner).order_by(CodingSession.created.desc()))]

    def end(self, owner, session_id):
        with self.serial(owner), self.database.transaction() as db:
            session = owned(db, CodingSession, session_id, owner)
            session.status, session.ended = 'ended', time.time()
            return record(session)

    def unresolved(self, db, project_id):
        return db.scalar(select(Checkpoint).where(Checkpoint.project_id == project_id, Checkpoint.status.not_in(RESOLVED)).order_by(Checkpoint.created))

    def gate(self, owner, session_id):
        with self.database.transaction() as db:
            session = owned(db, CodingSession, session_id, owner)
            pending = self.unresolved(db, session.project_id)
            lease = db.get(Lease, owner)
            busy = bool(lease and lease.expires > time.time())
            available = session.status == 'active' and not pending and not busy
            return {'available': available, 'checkpoint_id': pending.id if pending else None,
                    'reason': 'checkpoint_unresolved' if pending else 'session_ended' if session.status != 'active' else 'operation_in_progress' if busy else 'ready',
                    'integration': 'codeproof_managed', 'external_assistants_controlled': False,
                    'scope': 'Only submitted saved changes; other coding assistants and unsubmitted edits are outside this gate.'}

    def checkpoint(self, owner, id):
        with self.database.transaction() as db:
            cp = owned(db, Checkpoint, id, owner)
            return self.detail(db, cp)

    def detail(self, db, cp):
        if cp.status == 'evaluating':
            lease = db.get(Lease, cp.owner)
            if not lease or lease.expires < time.time():
                cp.status, cp.last_error = 'unavailable', 'interrupted_evaluation'
                for pending in db.scalars(select(Attempt).where(Attempt.checkpoint_id == cp.id, Attempt.state == 'evaluating')):
                    pending.state, pending.error = 'failed', 'interrupted_evaluation'
        value = record(cp)
        attempts = list(db.scalars(select(Attempt).where(Attempt.checkpoint_id == cp.id).order_by(Attempt.created)))
        value['attempts'] = [record(a) for a in attempts]
        practice = self.practice_operation(db, cp)
        practice_data = practice.result if practice else None
        value['practice_question'] = practice_data['question'] if practice_data else None
        value['practice_started_version'] = practice_data['started_version'] if practice_data else None
        evaluations = [a.evaluation for a in attempts if a.state == 'completed' and a.evaluation and (not practice_data or a.version >= practice_data['started_version'])]
        value['current_question'] = next((e['next_question'] for e in reversed(evaluations) if e.get('next_question')), None) or (value['practice_question'] or cp.question or {}).get('question')
        value['can_pause'] = sum(e['decision'] == 'follow_up' for e in evaluations) >= 3
        help_op = db.scalar(select(Operation).where(Operation.owner == cp.owner, Operation.kind == 'checkpoint_explanation', Operation.key == cp.id, Operation.state == 'completed'))
        value['explanation_viewed'] = bool(help_op)
        value['learning_explanation'] = help_op.result.get('text') if help_op and help_op.result else None
        return value

    def practice_operation(self, db, cp):
        return db.scalar(select(Operation).where(Operation.owner == cp.owner, Operation.kind == 'checkpoint_practice', Operation.key == cp.id, Operation.state == 'completed'))

    def start_practice(self, owner, id, data):
        """Freeze a new question, retaining the original question and all earlier attempts."""
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                cp = owned(db, Checkpoint, id, owner)
                existing = self.practice_operation(db, cp)
                valid_versions = {cp.version, existing.payload['version']} if existing else {cp.version}
                if data.version not in valid_versions or data.snapshot_hash != cp.snapshot_hash:
                    raise AppError('stale_version', 'Refresh the checkpoint before starting practice.', 409)
                if existing:
                    return self.detail(db, cp)
                if cp.status in RESOLVED or not cp.question or cp.question.get('decision') != 'assess':
                    raise AppError('not_answerable', 'This checkpoint is not awaiting practice.', 409)
                if not cp.snapshot.get('files'):
                    raise AppError('context_expired', 'This saved source expired; practice cannot be generated.', 409)
                help_op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'checkpoint_explanation', Operation.key == id, Operation.state == 'completed'))
                if not help_op or not help_op.result or not help_op.result.get('text'):
                    raise AppError('explanation_required', 'Read the code explanation before starting assisted practice.', 409)
                explanation = help_op.result['text']
                version, snapshot_hash = cp.version, cp.snapshot_hash
            try:
                question = Question.model_validate(self.assessor.practice(cp, explanation))
                validate_evidence(question, cp.snapshot)
                if question.decision != 'assess' or question.question.casefold().strip() == cp.question['question'].casefold().strip():
                    raise ValueError('Practice needs a distinct assessment question')
                question.concept = cp.question['concept']
            except AppError:
                raise
            except Exception:
                raise AppError('invalid_practice', 'The model did not produce a valid fresh question. Your explanation is saved; try again.', 503, True) from None
            with self.database.transaction() as db:
                self.verify_lease(db, owner, lease)
                cp = owned(db, Checkpoint, id, owner)
                if cp.version != version or cp.snapshot_hash != snapshot_hash or not cp.snapshot.get('files'):
                    raise AppError('stale_version', 'The checkpoint changed. Refresh before trying again.', 409)
                cp.version += 1
                cp.status, cp.last_error = 'pending', None
                db.add(Operation(owner=owner, project_id=cp.project_id, kind='checkpoint_practice', key=id,
                    state='completed', payload={'version': version, 'snapshot_hash': snapshot_hash},
                    result={'question': question.model_dump(), 'started_version': cp.version}))
                db.flush()
                return self.detail(db, cp)

    def explain(self, owner, id):
        """Offer saved teaching material without submitting an answer or clearing the gate."""
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                cp = owned(db, Checkpoint, id, owner)
                op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'checkpoint_explanation', Operation.key == id))
                if op and op.state == 'completed':
                    return self.detail(db, cp)
                if cp.status in RESOLVED or not cp.question or cp.question.get('decision') != 'assess':
                    raise AppError('not_answerable', 'Open an unresolved question before requesting an explanation.', 409)
                if not cp.snapshot.get('files'):
                    raise AppError('context_expired', 'This saved source has expired; an explanation cannot be generated.', 409)
                version, snapshot_hash = cp.version, cp.snapshot_hash
            text = self.assessor.explain(cp)
            if not isinstance(text, str) or not text.strip() or len(text) > 24000:
                raise AppError('invalid_explanation', 'The model could not produce an explanation. Your checkpoint is unchanged; try again.', 503, True)
            with self.database.transaction() as db:
                self.verify_lease(db, owner, lease)
                cp = owned(db, Checkpoint, id, owner)
                if cp.version != version or cp.snapshot_hash != snapshot_hash or not cp.snapshot.get('files'):
                    raise AppError('stale_version', 'The checkpoint changed. Refresh before trying again.', 409)
                db.add(Operation(owner=owner, project_id=cp.project_id, kind='checkpoint_explanation', key=id,
                    state='completed', payload={'checkpoint_id': id, 'snapshot_hash': snapshot_hash}, result={'text': text}))
                db.flush()
                return self.detail(db, cp)

    def change(self, owner, session_id, data):
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                session = owned(db, CodingSession, session_id, owner)
                if session.status != 'active':
                    raise AppError('session_ended', 'Start a session before submitting changes.', 409)
                project = owned(db, Project, session.project_id, owner)
                if data.pr_import_id:
                    imported = owned(db, Operation, data.pr_import_id, owner)
                    if imported.kind != 'github_import' or imported.project_id != project.id:
                        raise AppError('invalid_import', 'This PR import does not belong to the project.', 409)
                    expected = imported.result.get('files', []) if imported.result else []
                    if digest([f.model_dump() for f in data.files]) != digest(expected):
                        raise AppError('import_mismatch', 'PR assessment must use the exact imported files.', 409)
                snap = capture(data.files, project.scope, project.exclusions)
                if not snap['files']:
                    return {'status': 'skipped', 'reason': 'No eligible meaningful changes within bounds.', 'capture': snap}
                snap['provenance'] = data.provenance
                if data.pr_import_id:
                    snap['pr_import_id'] = data.pr_import_id
                    snap['pr'] = imported.payload
                snapshot_hash = digest({'files': snap['files'], 'pr_import_id': data.pr_import_id})
                request_hash = digest(data.model_dump(exclude={'idempotency_key'}))
                op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'change', Operation.key == data.idempotency_key))
                if op and (op.payload['request_hash'] != request_hash or op.payload['session_id'] != session_id):
                    raise AppError('idempotency_conflict', 'This request key was used for different content.', 409)
                existing = db.scalar(select(Checkpoint).where(Checkpoint.project_id == project.id, Checkpoint.snapshot_hash == snapshot_hash))
                if existing:
                    # Re-uploading cannot rewrite a question already bound to saved attempts.
                    # Question/provider retries have their own explicit version-preserving endpoints.
                    return {'status': existing.status, 'checkpoint': self.detail(db, existing), 'duplicate': True}
                pending = self.unresolved(db, project.id)
                if pending and (not existing or pending.id != existing.id):
                    raise AppError('checkpoint_unresolved', 'Resolve the existing checkpoint before submitting another change. Keep new edits locally.', 409)
                if not existing:
                    existing = Checkpoint(owner=owner, project_id=project.id, session_id=session.id,
                        snapshot_hash=snapshot_hash, snapshot=snap, status='pending', model=getattr(self.assessor, 'model_id', 'test-only-fixture'))
                    db.add(existing)
                    db.flush()
                # An analysis interrupted by process death remains pending and can be retried explicitly.
                existing.last_error = None
                cp_id = existing.id
                recent = [c.question for c in db.scalars(select(Checkpoint).where(Checkpoint.project_id == project.id, Checkpoint.status.in_(PASSING), Checkpoint.passed_at > time.time()-300))]
                if not op:
                    op = Operation(owner=owner, project_id=project.id, kind='change', key=data.idempotency_key, state='processing',
                                   payload={'request_hash': request_hash, 'session_id': session_id}, result={'checkpoint_id': cp_id})
                    db.add(op)
            try:
                question = Question.model_validate(self.assessor.question(snap, recent))
                validate_evidence(question, snap)
                if question.decision == 'assess' and not question.important_distinct_use and any(q and q['concept'].casefold() == question.concept.casefold() for q in recent):
                    question.decision = 'skip'
                    question.reason = 'Recent concept cooldown: ' + question.reason
                with self.database.transaction() as db:
                    self.verify_lease(db, owner, lease)
                    cp = owned(db, Checkpoint, cp_id, owner)
                    if not cp.snapshot.get('files'):
                        raise AppError('context_expired', 'The saved source expired while generating the question. No question was saved.', 409)
                    cp.question = question.model_dump()
                    cp.status = {'assess': 'pending', 'skip': 'skipped', 'unable_to_assess': 'unavailable'}[question.decision]
                    cp.last_error = 'context_insufficient' if cp.status == 'unavailable' else None
                    return {'status': cp.status, 'checkpoint': self.detail(db, cp)}
            except Exception as exc:
                with self.database.transaction() as db:
                    self.verify_lease(db, owner, lease)
                    cp = owned(db, Checkpoint, cp_id, owner)
                    cp.status, cp.last_error = 'unavailable', exc.code if isinstance(exc, AppError) else 'invalid_assessment'
                if isinstance(exc, AppError):
                    raise
                raise AppError('invalid_assessment', 'The assessment response could not be validated. Retry without losing this snapshot.', 503, True) from None

    def retry_question(self, owner, id):
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                cp = owned(db, Checkpoint, id, owner)
                if cp.status not in {'pending', 'unavailable'} or (cp.question and cp.question.get('decision') == 'assess'):
                    raise AppError('not_retryable', 'This checkpoint already has a question.', 409)
                snapshot = cp.snapshot
                if not snapshot.get('files'):
                    raise AppError('context_expired', 'Source context has expired. Capture a new change in a new project.', 409)
            try:
                q = Question.model_validate(self.assessor.question(snapshot, []))
                validate_evidence(q, snapshot)
            except Exception as exc:
                raise exc if isinstance(exc, AppError) else AppError('invalid_assessment', 'Question generation failed validation.', 503, True)
            with self.database.transaction() as db:
                self.verify_lease(db, owner, lease)
                cp = owned(db, Checkpoint, id, owner)
                if not cp.snapshot.get('files'):
                    cp.status, cp.last_error = 'unavailable', 'context_expired'
                else:
                    cp.question = q.model_dump()
                    cp.model = getattr(self.assessor, 'model_id', 'test-only-fixture')
                    cp.status = {'assess': 'pending', 'skip': 'skipped', 'unable_to_assess': 'unavailable'}[q.decision]
                    cp.last_error = None
                    return self.detail(db, cp)
            # Commit the unavailable state before returning the typed conflict.
            raise AppError('context_expired', 'The saved source expired while generating the question. No question was saved.', 409)

    def answer(self, owner, id, data):
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                cp = owned(db, Checkpoint, id, owner)
                request_hash = digest(data.model_dump(exclude={'idempotency_key'}))
                attempt = db.scalar(select(Attempt).where(Attempt.checkpoint_id == id, Attempt.key == data.idempotency_key))
                if attempt:
                    if attempt.request_hash != request_hash:
                        raise AppError('idempotency_conflict', 'This answer key was used for different content.', 409)
                    if attempt.state == 'completed':
                        return self.detail(db, cp)
                if cp.version != data.version or cp.snapshot_hash != data.snapshot_hash:
                    raise AppError('stale_version', 'Refresh the checkpoint before answering.', 409)
                if cp.status in RESOLVED or not cp.question or cp.question['decision'] != 'assess':
                    raise AppError('not_answerable', 'This checkpoint is not awaiting an explanation.', 409)
                if not cp.snapshot.get('files'):
                    raise AppError('context_expired', 'This source context expired; it cannot be assessed.', 409)
                practice = self.practice_operation(db, cp)
                help_op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'checkpoint_explanation', Operation.key == id, Operation.state == 'completed'))
                if help_op and not practice:
                    raise AppError('practice_required', 'Start a fresh practice question after reading the explanation.', 409)
                previous = [record(a) for a in db.scalars(select(Attempt).where(Attempt.checkpoint_id == id, Attempt.state == 'completed').order_by(Attempt.created))]
                evaluation_checkpoint = cp
                if practice:
                    previous = [a for a in previous if a['version'] >= practice.result['started_version']]
                    evaluation_checkpoint = SimpleNamespace(snapshot=cp.snapshot, question=practice.result['question'], practice=True)
                if not attempt:
                    attempt = Attempt(owner=owner, checkpoint_id=id, key=data.idempotency_key, request_hash=request_hash,
                        version=data.version, answer=data.answer, modality=data.modality)
                    db.add(attempt)
                    db.flush()
                attempt.state, attempt.error = 'evaluating', None
                cp.status = 'evaluating'
                attempt_id = attempt.id
            try:
                result = Evaluation.model_validate(self.assessor.evaluate(evaluation_checkpoint, previous, data.answer))
            except Exception as exc:
                with self.database.transaction() as db:
                    self.verify_lease(db, owner, lease)
                    cp, attempt = owned(db, Checkpoint, id, owner), owned(db, Attempt, attempt_id, owner)
                    cp.status, attempt.state = 'unavailable', 'failed'
                    cp.last_error = attempt.error = exc.code if isinstance(exc, AppError) else 'invalid_evaluation'
                if isinstance(exc, AppError):
                    raise
                raise AppError('invalid_evaluation', 'The evaluation response failed validation. Your explanation is saved; retry safely.', 503, True) from None
            with self.database.transaction() as db:
                self.verify_lease(db, owner, lease)
                cp, attempt = owned(db, Checkpoint, id, owner), owned(db, Attempt, attempt_id, owner)
                if cp.version != data.version or cp.snapshot_hash != data.snapshot_hash:
                    raise AppError('stale_version', 'A newer result exists. Refresh this checkpoint.', 409)
                if not cp.snapshot.get('files'):
                    # Retention runs independently of the inference lease. Keep
                    # the submitted answer, but never persist a grade after expiry.
                    cp.status, attempt.state = 'unavailable', 'failed'
                    cp.last_error = attempt.error = 'context_expired'
                else:
                    attempt.state, attempt.evaluation = 'completed', {**result.model_dump(), 'model': getattr(self.assessor, 'model_id', 'test-only-fixture')}
                    cp.status = {'pass': 'passed_with_help' if practice else 'passed', 'follow_up': 'needs_followup', 'unable_to_assess': 'unavailable'}[result.decision]
                    cp.version += 1
                    cp.last_error = None
                    if result.decision == 'pass':
                        cp.passed_at = time.time()
                    db.flush()
                    return self.detail(db, cp)
            raise AppError('context_expired', 'The saved source expired during assessment. Your answer is saved, but no grade was recorded.', 409)

    def history(self, owner, session_id=None):
        with self.database.transaction() as db:
            query = select(Checkpoint).where(Checkpoint.owner == owner)
            if session_id:
                session = owned(db, CodingSession, session_id, owner)
                query = query.where(Checkpoint.project_id == session.project_id)
            return [self.detail(db, cp) for cp in db.scalars(query.order_by(Checkpoint.created.desc()))]

    def ask(self, owner, session_id, data):
        with self.serial(owner) as lease:
            with self.database.transaction() as db:
                session = owned(db, CodingSession, session_id, owner)
                request_hash = digest({'session_id': session_id, 'prompt': data.prompt})
                op = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'ask', Operation.key == data.idempotency_key))
                if op:
                    if op.payload['request_hash'] != request_hash:
                        raise AppError('idempotency_conflict', 'This request key was used for a different prompt.', 409)
                    if op.state == 'completed':
                        return op.result
                if session.status != 'active' or self.unresolved(db, session.project_id):
                    raise AppError('gate_locked', 'Resolve the project checkpoint and start a session before the next managed AI request.', 409)
                project = owned(db, Project, session.project_id, owner)
                scope_hash = record(project)['scope_hash']
                if op and 'context_checkpoint_id' in op.payload:
                    if op.payload['scope_hash'] != scope_hash:
                        raise AppError('ask_context_changed', 'Project scope changed during this request. Send a new request using the current scope.', 409)
                    cp = owned(db, Checkpoint, op.payload['context_checkpoint_id'], owner) if op.payload['context_checkpoint_id'] else None
                    if cp and (cp.project_id != project.id or cp.snapshot_hash != op.payload['snapshot_hash']):
                        raise AppError('ask_context_changed', 'The saved code context changed. Send a new request.', 409)
                else:
                    cp = db.scalar(select(Checkpoint).where(Checkpoint.owner == owner, Checkpoint.project_id == project.id).order_by(Checkpoint.created.desc(), Checkpoint.id.desc()))
                context_files = [{'path': f['path'], 'lines': f['lines']} for f in (cp.snapshot.get('files', []) if cp else [])
                    if f.get('lines') and eligible(f['path'], project.scope, project.exclusions)]
                if op and op.payload.get('had_context') and not context_files:
                    raise AppError('ask_context_changed', 'The code used for this interrupted request expired or left the scope. Send a new request.', 409)
                reason = 'approved_snapshot' if context_files else 'no_capture' if not cp else 'source_expired' if cp.snapshot.get('expired') else 'no_eligible_source'
                context = {'checkpoint_id': cp.id if cp else None, 'snapshot_hash': cp.snapshot_hash if cp else None,
                    'captured_at': cp.created if cp else None, 'files': [f['path'] for f in context_files],
                    'partial': bool(cp and (cp.snapshot.get('partial') or len(context_files) != len(cp.snapshot.get('files', [])))), 'reason': reason}
                context_binding = {'context_checkpoint_id': cp.id if cp else None, 'snapshot_hash': cp.snapshot_hash if cp else None,
                    'scope_hash': scope_hash, 'had_context': bool(context_files)}
                if not op:
                    op = Operation(owner=owner, project_id=session.project_id, kind='ask', key=data.idempotency_key, state='processing', payload={'request_hash': request_hash, **context_binding})
                    db.add(op)
                    db.flush()
                elif 'context_checkpoint_id' not in op.payload:
                    # Upgrade an interrupted request created before context binding existed.
                    op.payload = {**op.payload, **context_binding}
                op_id = op.id
            text = self.assessor.ask(data.prompt, {'source': 'approved_saved_after_excerpts', 'files': context_files, 'partial': context['partial']})
            if not isinstance(text, str) or not text.strip() or len(text) > 24000:
                raise AppError('invalid_assistant_response', 'The local assistant returned an invalid response. Retry your saved request.', 503, True)
            result = {'text': text, 'context': context, 'integration': 'codeproof_managed', 'files_modified': False}
            with self.database.transaction() as db:
                self.verify_lease(db, owner, lease)
                op = owned(db, Operation, op_id, owner)
                current_project = owned(db, Project, session.project_id, owner)
                if record(current_project)['scope_hash'] != scope_hash:
                    raise AppError('ask_context_changed', 'Project scope changed. Send a new request.', 409)
                if context_files:
                    current_cp = owned(db, Checkpoint, context['checkpoint_id'], owner)
                    if not current_cp.snapshot.get('files'):
                        raise AppError('ask_context_changed', 'The saved code expired while processing. Send a new request.', 409)
                op.state, op.result = 'completed', result
            return result

    def delete_project(self, owner, id):
        with self.serial(owner), self.database.transaction() as db:
            db.delete(owned(db, Project, id, owner))
        return {'deleted': True, 'external_records_removed': False, 'learning_pass_issued': False}
