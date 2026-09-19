# PRD review — local release 0.4.3

Reviewed against the original PRD and current user constraints on 19 September 2026. This is an engineering review, not human model-quality acceptance. Existing Figma UI, local Ollama/Qwen2.5-Coder, FastAPI, SQLite and the Managed Ask AI boundary remain the supported scope.

| Requirement | Current position | Remaining work / limit |
| --- | --- | --- |
| CORE-01 session/auth | Local-token ownership, scoped project/session, saved session restoration and token reuse implemented | Beginner feedback is positive but not a full observed acceptance checklist; hosted auth is outside scope |
| CORE-02 capture | Saved Git preview/approval, exclusions, bounds, duplicate and whitespace handling implemented | No universal assistant hooks; broader rename and missing-context heuristics remain limited |
| CORE-03 questions | Frozen source, exact source-evidence validation and local generation implemented | Valid schemas/quotes cannot guarantee correct questions or rubrics; independent technical review remains open |
| CORE-04 assessment | Follow-up/pass, saved-answer recovery and practice grading implemented | Known small-model semantic errors remain; no claim of validated grading accuracy |
| CORE-05 gate/recovery | Persisted pass required; duplicate/version/lease/restart checks; reading help does not pass | Only BeProgram Managed Ask AI is controlled; manually editing and other assistants remain available |
| Managed coding request | 0.4.3 now supplies the latest approved AFTER excerpts, labels files/time/partial coverage, binds retry context and rechecks scope | Previously it received only the prompt. Suggestions can still be wrong, including an observed zero-capacity error; they are not executed or auto-applied |
| CORE-06 history | Actual questions, submitted explanations, feedback and assisted-practice evidence retained | No independently certified mastery. Human technical review remains incomplete |
| OBS-01 | Local redacted lifecycle logs, readiness doctor, startup reuse/restart and failure categories | Hosted Sentry and its sponsor claim are outside the free edition |
| LEARN-01 | Read explanation → fresh frozen practice → `passed_with_help`; previous answers excluded from practice evaluation | New practice flow still needs user usability feedback and independent semantic review |
| Privacy/retention | Scoped capture, auth, source expiration and deletion; 0.4.3 removes code-derived managed responses when their source expires | Retention runs through the documented job, not a promise that merely waiting triggers cleanup |
| Release verification | Current unit/API/browser/host verification recorded in [verification](VERIFICATION.md) | Test doubles verify behavior; real-model samples do not replace independent review |
| SOL-01/02 | Deferred by user | Remains disabled |
| VOICE-01/02 and GH-01/02 | Unavailable in agreed local scope | Do not enable paid adapters or publish anything |
| SEARCH-01 | Deferred | No extra retrieval infrastructure justified yet |
| Public deployment | Not delivered | Separate scope; local delivery does not imply authorization to publish |

## Findings addressed in this review

1. Managed Ask AI lacked approved source context. It now receives only the latest approved AFTER excerpts from the current project that remain within its current scope. No unapproved filesystem read, additional upload, prior learner answer or private rubric is included.
2. Interrupted managed requests could otherwise drift to newer code. A request now stores a snapshot reference and scope fingerprint; retries reuse that snapshot or require a new request if its authorization/context changed. Raw source is not duplicated in operation payloads.
3. Context-derived replies require retention handling. Source expiry clears those saved replies, and expiry during inference prevents saving the response.
4. Practice regression tests referenced by the previous notes were absent from this checkout. Coverage was restored in [test_practice.py](../tests/test_practice.py). The current suite is rerun rather than reporting historical counts as fresh results.

## Evidence limits discovered during review

The 0.4.1/0.4.2 notes refer to `explanation-smoke.json`, `practice-smoke.json`, `practice-regressions.json`, earlier `practice-*.json` reports and `scripts/check_practice_assessment.py`. Those files were absent when this review started. Their earlier claims remain historical notes; they are not currently reproducible from those missing files. No missing report was recreated as if it were the original run.

Current managed-response samples are preserved in [initial errors](release-review/managed-context-initial-errors.json) and [latest smoke](release-review/managed-context-smoke.json). The latter includes execution of the known synthetic fixture: `canJoin(4,5)`, `canJoin(5,5)`, `canJoin(0,0)` returned `true`, `false`, `false`. The model still incorrectly suggested `true` for the last input. Its absent-context answer improved to unknown after a bounded prompt adjustment. This is one narrow agent-inspected sample, not independent validation.

## Next priorities

Latest hardening fixed source-expiry races during question generation, retry and grading. Final verification now has 89 backend tests, four browser scenarios and six packaged-host groups passing. The installed extension remains 0.4.3; the backend update is active.

The new 24-case practice benchmark has executable synthetic reference outputs, but its explanation labels are still agent-authored. The retained baseline has zero application-level false passes and two rejected ungrounded model passes. A candidate prompt introduced two false passes and was reverted. Three fresh core flows pass state assertions while still exposing wrong rubric/suggestion content. See [latest verification](VERIFICATION.md) for preserved reports; this is not independent quality acceptance.

The user can use [the beginner checklist](BEGINNER_TEST.md) to report clarity, waiting time and recovery without taking responsibility for technical review.

Keep optional integrations deferred. Focus next on independently reviewable assessment/suggestion examples, preserving failure evidence, and beginner feedback on practice/recovery. Broader model reliability is unresolved; adding source context fixes an information gap but does not establish correctness. The user should not be asked to certify code they cannot confidently assess.
