# BeProgram implementation plan

Living plan: 19 September 2026. This is the current status and remaining work. Earlier chronological notes are preserved in [implementation history](docs/IMPLEMENTATION_HISTORY.md); historical provider claims and test counts there do not override this plan.

## Product and release scope

BeProgram is a VS Code extension plus a supporting local dashboard. A learner approves a saved JS/TS Git change, answers a grounded question, receives an adaptive follow-up or pass, and sees durable evidence. Only the next BeProgram Managed Ask AI request is gated. Other assistants and manual edits remain independent.

Functionality source: `C:/Users/Mathe/Downloads/PRD.md.md` (version 3.0, inspected again). The earlier `BeProgram_PRD_v3.md` path is no longer present. Visual source remains the supplied Figma Make ZIP; reuse its components, tokens and navigation. No redesign.

User decisions superseding the original PRD: no paid APIs/subscriptions/credits; local inference and local SQLite/token auth; Solana disabled and deferred; beginner-friendly demonstration. Hosted OpenAI/Sentry/ElevenLabs/Composio track claims are withdrawn. Optional feature behavior may use a genuinely local/free replacement, but sponsor eligibility is not implied. No public deployment or GitHub publication is authorized by development/testing alone.

## Eight-hour finish budget

These are effort/time limits, not a claim that model quality or optional integrations are guaranteed. Protect the last two hours for release verification and human rehearsal. If P0 is still unstable with six hours left, pause optional integrations as the PRD specifies.

| Window | Milestone | Deliverables and dependencies | Verification / exit |
| --- | --- | --- | --- |
| 0-2 h | A: assessment reliability | Reproduce known failures; compare one newer free local model using unchanged labels; only adopt with observed improvement. Keep strict output/provenance checks and saved-answer recovery. | Three real flows, central-misconception rejection, 20 measured evaluations and generated-question review. Report false passes, unfair rejections, errors and p95 separately. |
| 2-4 h | B: core usability and operations | Idempotent startup, local health/diagnostics, useful redacted lifecycle logs, clear model/setup/retry messages. Reuse current auth and DB. | Repeated startup, occupied/unrelated port, model outage, no secrets/source in diagnostics, recovery and retention checks. |
| 4-6 h | C: optional slice, only if A/B stable | Prefer a small free read-aloud capability if installed offline voices are available. Recording/transcription and direct GitHub publication need separate feasibility and real consent/testing; do not fake them. | Actual supported surface works with stop/cancel/text fallback; unsupported capability stays unavailable. If P0 fails, spend this window on P0 instead. |
| 6-8 h | D: release and rehearsal | Build dashboard/sidebar, unit/browser/actual host tests, package verified VSIX, update run guide and evidence register. Prepare human review and three repeatable demos. | Exact packaged extension verified, mobile/desktop layout checked, startup/restart/auth/state flows pass. User reviews 20 answers and rehearses actual sidebar. |

## PRD requirement status

| Requirement | Current evidence | Remaining work |
| --- | --- | --- |
| CORE-01 scoped authenticated sessions | Local token, SecretStorage, owner scope, start/end/restore implemented and tested | Reduce setup friction; actual user rehearsal |
| CORE-02 saved change capture | Git HEAD/working tree capture, preview, scope/exclusions, bounds, partial label, duplicate/whitespace suppression | Broader missing-context and rename heuristics remain limited; no universal AI-turn hook |
| CORE-03 grounded questions | Local model, exact AFTER source evidence validation, preserved snapshots | Model has invented rubric claims; improve and review question accuracy |
| CORE-04 evaluation/follow-up | Real text evaluation and adaptive follow-ups; latest saved-answer quote bug fixed | Human review, false-pass/false-rejection assessment; general SQL smoke previously failed |
| CORE-05 durable gate | Version/idempotency/transaction/lease checks, restart/retry, only persisted pass unlocks managed request | Fresh end-to-end release verification |
| CORE-06 history/evidence | Dashboard and sidebar actual records; project deletion; no seeded success | Release UI checks and user pilot |
| OBS-01 operations | Hosted Sentry disabled; historical redaction tests exist | Useful local lifecycle/error/duration evidence; no Sentry track claim |
| SOL-01/02 | Implementation retained, disabled routes block RPC; hidden in core navigation | Explicitly deferred by user, no active receipt acceptance |
| VOICE-01/02 | Hosted adapters disabled; text works | Optional local playback feasibility; STT unimplemented in free edition |
| GH-01/02 | Hosted Composio adapter disabled; local Git works | Direct free GitHub replacement unimplemented, no connection or approved PR; not required for core release |
| LEARN-01 explanation and transfer practice | 0.4.2: explanation followed by a frozen fresh practice question, separate attempts and `passed_with_help` | User explicitly selected this next step; independent grading-quality and new-flow usability review remain open |
| SEARCH-01 | Not implemented | P2 deferred; no need established for extra infrastructure |

## Architecture and existing contracts

Frontend: Figma-exported React/Vite/TypeScript dashboard routes `/`, `/history`, `/history/:id`, `/settings`; `/verify` reports disabled receipts. VS Code Activity Bar webview reuses checkpoint components with a validated host bridge and strict CSP. Preserve desktop/mobile, light/dark, loading, empty, unavailable, follow-up and passed states. Native host owns secrets and Git capture. Unsaved explanation drafts are memory-only; submitted answers are durable.

Backend: FastAPI/Pydantic + SQLAlchemy; one SQLite database in supported local mode. Tables: projects, sessions, checkpoints (frozen snapshot/question), attempts, operations, leases, rate_windows. Owner identities come from auth. Private reads and writes are authorized. Database changes need explicit migrations. Historic Supabase/Postgres production support is separate and not currently deployment-verified.

API: project/scope/session CRUD, `/v1/sessions/{id}/changes`, `/v1/checkpoints/{id}`, `/answers`, `/retry`, `/gate`, `/ask`, `/v1/history`, `/health`, `/v1/config`. No endpoint directly marks a checkpoint passed. Typed failures preserve state; stale versions conflict; idempotent retries cannot duplicate a pass or external write. API docs are available locally at `/docs`.

Integration: saved-file events notify after a debounce; source upload requires preview approval. Before Managed Ask AI, the extension captures/reconciles eligible changes and checks persisted state. AI suggestions open in a document and do not modify source. No claimed ability to pause Copilot, Claude or Codex.

Local inference: dedicated loopback Ollama, cloud disabled, bounded context/output/timeouts and validated installed local weights. Current qwen2.5-coder:7b has known semantic errors. A candidate model comparison must preserve label files and provenance, with rollback available. No hosted fallback. Candidate download uses disk/bandwidth but no subscription or inference credits.

## Credentials, setup and operational boundaries

Only `LOCAL_DEV_TOKEN` is needed for the supported local edition; generated on setup, kept in ignored `.env` and VS Code SecretStorage. Never paste it into chat or logs. `.env.example` documents loopback/model/DB settings. Optional provider keys cannot activate disabled paid adapters. Model weights/runtime are outside OneDrive in `%LOCALAPPDATA%/BeProgram/ollama`.

Run `./scripts/run-local.ps1`; install `artifacts/beprogram-companion.vsix`. Supported release is local-only. Do not expose local auth publicly. Public hosting, DNS, PostgreSQL, TLS and OAuth require a separate verified deployment plan and are not promised free. See `docs/DEPLOYMENT.md` for current boundaries.

## Testing and acceptance

Current release: 0.4.2, with 76 backend tests, 10 extension unit tests, four browser scenarios and six exact-package host groups passing. Test doubles prove API/state/UI behavior, not model judgment. Seven targeted actual-model practice regressions and one actual explanation/practice/rejection/pass flow passed after the development fixes documented in verification. These agent-authored checks do not establish independent accuracy. Older calibration and package results remain historical evidence.

Mandatory release checks: no paid calls; owner isolation; wrong token rejection; meaningful capture and trivial suppression; correct first-answer pass and follow-up/pass; invalid output/outage recovery; restart/dedup/stale state; history; next managed request; three consecutive real demos; 20 independently human-reviewed explanations. Measure at least 20 requests; original p95 <10 seconds is a target, not assumed. Optional failures cannot change learning state.

## Open risks and decisions

- Local model can produce wrong rubrics or feedback even when schema/provenance checks pass. Human review cannot be completed by the coding assistant; record blanks honestly.
- The excerpt-repair call is a documented exception to the PRD's one evaluator-call preference: at most one extraction-only recovery, inside the remaining operation budget; it cannot choose the grade.
- Prior question/format tweaks improved one case but regressed another. Freeze samples before comparing models; no relabeling to inflate success.
- Hardware load/cold start affects latency. No benchmark guarantees across machines.
- No actual microphone, authorized remote PR, paid service or public deployment is available. Optional scope must stay explicit.
- Existing user history/token/demo folders are preserved. Do not commit secrets or simulate successful external services.

## Current milestone log

- A started: re-read actual PRD, audited implementation and preserved historical plan. Next: bounded local-model comparison and current assessment evidence.

- A comparison checkpoint: with identical assessor/dataset, current Qwen2.5-Coder 7B matched 19/20 but accepted one central misconception; p95 4.453s. Qwen3 4B Instruct matched 19/20 with zero false passes and one operational output error on a complete answer; p95 5.5s, including a 10.016s first/cold failure. Both full reports and untouched labels are in `docs/release-review/`. Candidate is installed, not yet selected as the application default. Next: real flow and output-error investigation, without relabeling cases.
- B independent work: repeated startup now detects the existing workspace backend and runs a read-only doctor; unrelated processes are never stopped. Local logs contain allowlisted operation/category, opaque correlation ID, duration and status only, rotated at 1 MB plus three backups. 63 backend tests pass, including diagnostics secrecy and log failure isolation; repeated startup verified against the running app.

- A constraint discovered: Qwen3 4B Instruct passed the broader flow suite but rejected the beginner explanation by inventing concurrent-system/input-validation requirements. A bounded prompt change did not correct that behavior. Candidate is not promoted. Revise the one-candidate spike to allow one final smaller Qwen3.5 4B comparison (official local weights, no hosted inference), keeping optional work paused. This is justified by a demonstrated P0 failure, not a new feature or track. If it cannot meet the core checks, release remains a prototype with explicit quality limitations; do not claim stable grading.

- B verified: 63 backend tests, nine extension unit tests, TypeScript/site/sidebar builds and three browser scenarios pass. Sidebar now shows elapsed local-processing time without a fake progress percentage. Connecting another project reuses the existing server-scoped SecretStorage token; unauthorized tokens prompt once, outages preserve the token. Browser tests moved to configurable port 8020 to avoid the actual demo preview on 8010; test DB cleanup now disposes connections even after startup failure.
- Human review preparation: user agreed to review 20 assessments. An offline HTML worksheet and fingerprint-bound export validator are implemented. Browser test verified 20 cards, local progress persistence and incomplete export labeling in an isolated automated profile; this is not human-review evidence. Populate the final worksheet only after the model choice is frozen.

- A decision: final Qwen3.5 comparison matched 15/20 fixed labels, with zero false passes, four operational failures and one complete answer rejected; p95 5.672s. Its beginner flow passed, broader SQL flow failed. A synthetic retry succeeded, so the output problem is intermittent; no claim of a diagnosed/fixed format defect. Neither candidate is promoted. Keep Qwen2.5-Coder 7B, freeze release prompts, measure a fresh final report and expose remaining errors to human review. Candidate reports remain intact.
- C deferred: demonstrated P0 grading uncertainty takes priority under the PRD's cut rule. Voice and GitHub publication remain unavailable, Solana remains explicitly deferred. This release is a local prototype until model-quality and human rehearsal acceptance are resolved.
- D underway: 0.4.0 package built with nine passing unit tests; exact archive extracted to an isolated host-test workspace. Human checklist will reference the frozen final report, including any failures. No grades/history modified for demonstration.

- A release checks: frozen Qwen2.5-Coder 7B + scope/quote guidance matched 20/20 fixed labels (zero observed false passes/errors), p95 5.36s, cold maximum 14.531s. Three consecutive actual full flows, six rejection cases and the simple beginner flow pass. This reused agent-authored set is not held-out accuracy. Final generated questions/feedback were inspected; managed responses still hallucinate a null guard and an incorrect zero-capacity result. A is automated-flow verified, model-quality acceptance remains open.
- B/D verified: 63 backend tests, nine unit tests, three browser scenarios, site/sidebar builds and six exact-VSIX host groups pass. Package 0.4.0 fingerprint in docs/release-review/package.json. Backend restarted without deleting history; doctor passes; actual synthetic missing-session request produces redacted local telemetry. Mobile and wide light sidebar screenshots inspected. No hosted deployment/publication.
- Human deliverable ready: docs/release-review/HUMAN_REVIEW.html contains final 20 cases, independent verdict/feedback fields, local progress and fingerprint-bound JSON export. User has the link and save instructions. Await real review and hands-on sidebar rehearsal; do not mark these complete or claim the entire PRD finished. Optional C remains deferred due observed P0 model-quality risks.

- Usability update 0.4.1: user requested visible Managed Ask AI and a give-up explanation. Added sidebar/success-screen buttons and an authenticated, checkpoint-scoped local explanation, saved using existing operation records. Reading help does not submit an answer, pass, or unlock the gate; history records help viewed even after later answers. This is a teaching aid, not completion of the deferred transfer-question feature. Source-derived explanation text expires with source retention. Existing Figma styling and disabled integrations remain intact. Independent technical review remains incomplete; the user can perform beginner usability testing without certifying model correctness.

- User feedback after 0.4.1: “everything works well.” Recorded as informal beginner usability feedback, not an independently observed full acceptance checklist or technical model review. User then explicitly selected practice after giving up.
- 0.4.2: fresh practice now follows explanation help. Original questions and attempts remain unchanged; practice has its own frozen reference solution, stage version and subsequent attempts. Correct practice answers receive `passed_with_help`; old answers, reading help and retries cannot pass it. Initial local-model experiments included a false pass and invalid output; those failures are retained in `docs/release-review/practice-*.json`. Dedicated exercise generation and dimension-based practice evaluation address the observed regressions. Seven fixed capacity checks and one actual flow pass; broader independent validation remains open.
