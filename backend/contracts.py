from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ProjectInput(Strict):
    name: str = Field(min_length=1, max_length=120)
    scope: list[str] = Field(min_length=1, max_length=50)
    exclusions: list[str] = Field(default_factory=list, max_length=50)

    @field_validator('scope', 'exclusions')
    @classmethod
    def paths(cls, values):
        from .context import safe_path
        for value in values:
            safe_path(value.rstrip('/'))
        return values


class SessionInput(Strict):
    project_id: str


class ScopeInput(ProjectInput):
    expected_scope_hash: str = Field(pattern=r'^[a-f0-9]{64}$')


class FileChange(Strict):
    path: str = Field(min_length=1, max_length=500)
    before: str = Field(max_length=100_000)
    after: str = Field(max_length=100_000)


class ChangeInput(Strict):
    files: list[FileChange] = Field(min_length=1, max_length=30)
    provenance: Literal['observed_ai_turn', 'user_reported_manual', 'unknown'] = 'unknown'
    idempotency_key: str = Field(min_length=8, max_length=100)
    pr_import_id: str | None = None


class AnswerInput(Strict):
    answer: str = Field(min_length=3, max_length=8000)
    version: int = Field(ge=1)
    snapshot_hash: str = Field(pattern=r'^[a-f0-9]{64}$')
    idempotency_key: str = Field(min_length=8, max_length=100)
    modality: Literal['text', 'reviewed_voice'] = 'text'


class AskInput(Strict):
    prompt: str = Field(min_length=3, max_length=8000)
    idempotency_key: str = Field(min_length=8, max_length=100)


class Evidence(Strict):
    path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=2000)


class Question(Strict):
    decision: Literal['assess', 'skip', 'unable_to_assess']
    concept: str = Field(min_length=1, max_length=120)
    question: str = Field(max_length=2000)
    reason: str = Field(min_length=1, max_length=2000)
    rubric: list[str] = Field(max_length=6)
    evidence: list[Evidence] = Field(max_length=5)
    important_distinct_use: bool

    @model_validator(mode='after')
    def grounded(self):
        if self.decision == 'assess' and (not self.evidence or not self.question or len(self.rubric) < 3):
            raise ValueError('Assessment requires evidence, question and intent/mechanism/reasoning rubric')
        return self


class Evaluation(Strict):
    decision: Literal['pass', 'follow_up', 'unable_to_assess']
    intent_correct: bool
    mechanism_correct: bool
    reasoning_correct: bool
    central_contradiction: bool
    feedback: str = Field(min_length=1, max_length=3000)
    evidence: list[str] = Field(max_length=6)
    gaps: list[str] = Field(max_length=6)
    next_question: str | None

    @model_validator(mode='after')
    def coherent(self):
        if self.decision == 'pass' and (not all([self.intent_correct, self.mechanism_correct, self.reasoning_correct]) or self.central_contradiction or self.gaps or self.next_question):
            raise ValueError('Incoherent pass')
        if self.decision == 'follow_up' and not self.next_question:
            raise ValueError('Follow-up question required')
        return self
