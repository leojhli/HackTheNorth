"""Run daily: python -m backend.retention. Public chain records cannot be deleted here."""
import time
from sqlalchemy import select
from .config import settings
from .db import Database, Checkpoint, Operation


def expire_context(database, days=30):
    cutoff, count = time.time()-days*86400, 0
    with database.transaction() as db:
        for cp in db.scalars(select(Checkpoint).where(Checkpoint.created < cutoff)):
            if cp.snapshot.get('files'):
                cp.snapshot = {**cp.snapshot, 'files': [], 'expired': True}
                count += 1
        for op in db.scalars(select(Operation).where(Operation.created < cutoff, Operation.kind == 'github_import')):
            op.result = {'files': [], 'expired': True}
        for op in db.scalars(select(Operation).where(Operation.created < cutoff, Operation.kind == 'receipt')):
            # Never mutate a committed package. Remove the whole private package; its digest remains.
            if op.payload.get('manifest'):
                op.payload = {**op.payload, 'manifest': None, 'evidence_expired': True}
    return count


if __name__ == '__main__':
    print('Expired source snapshots:', expire_context(Database(settings().database_url)))
