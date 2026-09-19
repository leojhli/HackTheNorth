"""One database; JSON payloads are immutable evidence, never client-authoritative state."""
import time
import uuid
from contextlib import contextmanager
from sqlalchemy import create_engine, event, String, Text, Integer, Float, JSON, UniqueConstraint, ForeignKey, MetaData, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def uid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    metadata = MetaData(schema='beprogram')


class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(120))
    scope: Mapped[list] = mapped_column(JSON)
    exclusions: Mapped[list] = mapped_column(JSON, default=list)
    created: Mapped[float] = mapped_column(Float, default=time.time)


class CodingSession(Base):
    __tablename__ = 'sessions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner: Mapped[str] = mapped_column(String(128), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(24), default='active')
    created: Mapped[float] = mapped_column(Float, default=time.time)
    ended: Mapped[float | None] = mapped_column(Float, nullable=True)


class Checkpoint(Base):
    __tablename__ = 'checkpoints'
    __table_args__ = (UniqueConstraint('project_id', 'snapshot_hash'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner: Mapped[str] = mapped_column(String(128), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey('sessions.id', ondelete='CASCADE'), index=True)
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(24), default='pending')
    version: Mapped[int] = mapped_column(Integer, default=1)
    question: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str] = mapped_column(String(100))
    created: Mapped[float] = mapped_column(Float, default=time.time)
    passed_at: Mapped[float | None] = mapped_column(Float, nullable=True)


class Attempt(Base):
    __tablename__ = 'attempts'
    __table_args__ = (UniqueConstraint('checkpoint_id', 'key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner: Mapped[str] = mapped_column(String(128), index=True)
    checkpoint_id: Mapped[str] = mapped_column(ForeignKey('checkpoints.id', ondelete='CASCADE'), index=True)
    key: Mapped[str] = mapped_column(String(100))
    request_hash: Mapped[str] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(Integer)
    answer: Mapped[str] = mapped_column(Text)
    modality: Mapped[str] = mapped_column(String(24))
    state: Mapped[str] = mapped_column(String(24), default='evaluating')
    evaluation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created: Mapped[float] = mapped_column(Float, default=time.time)


class Operation(Base):
    __tablename__ = 'operations'
    __table_args__ = (UniqueConstraint('owner', 'kind', 'key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner: Mapped[str] = mapped_column(String(128), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    kind: Mapped[str] = mapped_column(String(40))
    key: Mapped[str] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created: Mapped[float] = mapped_column(Float, default=time.time)


class Lease(Base):
    __tablename__ = 'leases'
    owner: Mapped[str] = mapped_column(String(128), primary_key=True)
    token: Mapped[str] = mapped_column(String(36))
    expires: Mapped[float] = mapped_column(Float)


class RateWindow(Base):
    __tablename__ = 'rate_windows'
    owner: Mapped[str] = mapped_column(String(128), primary_key=True)
    started: Mapped[float] = mapped_column(Float)
    count: Mapped[int] = mapped_column(Integer)


class Database:
    def __init__(self, url):
        self.engine = create_engine(url, connect_args={'check_same_thread': False, 'timeout': 15} if url.startswith('sqlite') else {}, pool_pre_ping=True)
        if url.startswith('sqlite'):
            self.engine = self.engine.execution_options(schema_translate_map={'beprogram': None})
            @event.listens_for(self.engine, 'connect')
            def sqlite_config(connection, _):
                connection.execute('PRAGMA foreign_keys=ON')
                connection.execute('PRAGMA journal_mode=WAL')
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self):
        with self.sessions.begin() as db:
            yield db

    def migrate(self):
        if self.engine.dialect.name == 'postgresql':
            with self.engine.begin() as connection:
                connection.execute(text('CREATE SCHEMA IF NOT EXISTS beprogram'))
                connection.execute(text('REVOKE ALL ON SCHEMA beprogram FROM PUBLIC'))
                for role in ('anon', 'authenticated'):
                    exists = connection.scalar(text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role': role})
                    if exists:
                        connection.execute(text(f'REVOKE ALL ON SCHEMA beprogram FROM {role}'))
        Base.metadata.create_all(self.engine)
