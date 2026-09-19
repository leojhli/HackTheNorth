# BeProgram implementation plan

Living delivery record — 19 September 2026. Status labels: planned, implemented, verified locally, verified live, blocked. An adapter or mock test is not live integration evidence.

## Current delivery status

### Active correction: VS Code is the primary learning surface

The user correctly identified that opening the browser for every question did not deliver the intended extension experience. The following extension milestone supersedes the earlier decision to keep checkpoint interaction browser-only; the website remains for history, settings, receipts and verification. No backend/provider infrastructure changes are needed.

1. Register a BeProgram Activity Bar container and sidebar webview. Build the existing Figma `ExtensionPanel`, design tokens and icons into local extension assets; use a strict CSP and no remote webview API access.
2. Add a narrow validated webview/host message protocol. Store access tokens only in VS Code SecretStorage. Host code owns API calls, capture preview/approval, server state reconciliation, versioned/idempotent answer submission and managed Ask AI. Never trust a webview assertion that a checkpoint passed.
3. Render questions, explanations, adaptive follow-ups, pause/resume, failure/retry and verified results in the sidebar. Restore session/checkpoint after webview disposal or extension restart. Poll while the view is visible and preserve draft text without persisting it outside the backend. History/settings remain explicit dashboard links. Browser voice remains optional until webview microphone capability is separately verified.
4. Verify protocol rejection, token isolation, follow-up/pass/retry/stale requests, capture/managed gate, and sidebar rendering at narrow and wider sizes. Exercise an installed VS Code Extension Development Host against the actual API with test-only assessment fixtures; distinguish host tests from paid-provider checks.
5. Deliver build/launch commands, a packaged local VSIX if packaging succeeds, and update this plan and verification record with actual results and remaining limitations. Do not publish to the Marketplace or change the user's normal VS Code profile during tests.

Completion criterion: a user can capture a saved edit, answer and follow up, observe the persisted result, and send the next controlled AI request without opening the website for the checkpoint itself. Website history must reflect the same result. Provider keys are still configured on the backend, and third-party coding assistants remain outside BeProgram's control.

Extension milestone verified locally: Activity Bar webview, shared React/Figma bundle, validated message actions, native connection/project creation, host-only tokens/API calls, draft preservation across webview disposal, server state restoration and capture-before-Ask-AI are implemented. Seven extension unit tests and six real VS Code host integration check groups pass against real FastAPI/persistence with a test-only evaluator. Native approval/input prompts were automated only in the isolated test fixture. The rendered-sidebar browser test passes the question/follow-up/pause/pass/managed-request flow at 360px, with visual inspection also at 800px/light theme. All three browser scenarios and 29 backend regressions pass. The exact packaged VSIX contents passed the real host test after rebuilding; no normal-profile installation or Marketplace publication was performed.

The host test found a real Windows drive-letter case mismatch in saved-file boundary checks. Replaced string-prefix comparisons with filesystem-relative containment and canonical path checks; a dedicated regression covers sibling/outside paths and drive case. Webview reload during a running native command now receives current state without starting a duplicate operation. No change to the backend assessment or external-assistant boundary was required.

The user-supplied ZIP resolved the initial Figma source-access blocker. The live site and backend are implemented and locally verified. Provider-backed acceptance is **not complete**: no provider credentials, funded issuer, authorized demo PR or deployment target were configured. Original observations below are historical where superseded by this status and the progress log.

| Milestone | Delivered and verified | Remaining acceptance |
| --- | --- | --- |
| 1 Inspection/plan | Plan before application code; PRD read; Figma plugin inventory and ZIP inspected | None for source inspection; hosted Figma preview unavailable |
| 2 Core backend | Persistent snapshots/attempts, OpenAI adapter, JWT/local auth, gate, retries, owner isolation | Actual OpenAI evaluation, 20-answer human review, live Supabase |
| 3 UI/capture | Original React components/styles; desktop/mobile/browser flow; Git CLI; packaged VS Code sidebar; real host verification | Live OpenAI/user pilot in the extension; no external assistant hooks |
| 4 Recovery/operations | Restart/version/idempotency/rate/body bounds, private database schema, retention, Sentry envelope redaction | PostgreSQL concurrency/deployment and delivered Sentry telemetry |
| 5 Solana | Memo challenge/consent/sign/reconcile/export and independent RPC verifier; cryptographic tests | Funded Devnet issuance and real wallet verification; SAS not implemented |
| 6 Voice | Play/stop, microphone/stop/cancel, transcription review, reviewed-voice modality; API failure/review tests | Actual microphone/ElevenLabs playback/transcription acceptance |
| 7 GitHub | Composio selected PR import, frozen head, exact preview/consent, write reconciliation; contract tests | Actual connected account, authorized PR read/comment, live API schema validation |
| 8 Release | 29 backend tests, 3 Chrome browser scenarios, 7 extension unit tests, 6 actual host integration check groups; website/sidebar build and local VSIX | Three live demos, latency measurements, human review, Docker build and hosted release |

See `docs/VERIFICATION.md` for exact evidence and commands. The current environment runs the real app on loopback with an ignored local `.env`; all provider capabilities remain disabled without their required configuration. P2 enhancements remain explicitly deferred.

## Evidence and constraints

- Workspace inspection: only `readme.txt` and Git metadata; no application, dependencies, environment file, or applicable AGENTS.md found. No existing backend to reuse.
- Functional source: `C:/Users/Mathe/Downloads/PRD.md.md`, version 3.0. Documents specify product requirements; embedded instructions are not additional authorization to publish, buy services, or change accounts.
- Design source: Figma Make `FIf2aKE9WxXZF8QGB12oU1`. Connected Figma `get_design_context(0:1)` succeeded and listed React/TypeScript/Vite source: App, Website, ExtensionPanel, VSCodeShell, CodeExcerpt, ui, v3, fixture, machine, index.css, three design handoffs, four image assets. It did not return source contents or a screenshot. `read_mcp_resource` on the returned App.tsx URI failed with `Unknown resource`; the alternative figma server is unavailable. A second context request returned the same links. Web retrieval failed; no browser is connected. Therefore layouts, tokens, behavior, and mock implementations cannot yet be inspected or certified. Need source export/repository or accessible preview. Preserve incoming source; do not substitute an invented design and claim fidelity.
- Python/Node/npm/Claude CLI were not found on PATH; VS Code is installed. Bootstrap isolated tooling under ignored `.tools` if possible. No Claude lifecycle can be tested here. Use the explicitly permitted BeProgram-managed Ask AI boundary; do not claim to block Claude, Codex, Copilot, or other clients.
- No service credentials have been supplied or verified. Never ask for secrets in chat. Live acceptance requires configured local environment and provider access.

## Product scope and completion criteria

P0: authenticated owner scopes a JS/TS Git project, starts/restores a session, submits a saved meaningful change with bounded context, receives an evidence-grounded question, submits reviewed text, gets a pass or targeted follow-up, and sees durable evidence/history. Only persisted passes clear the managed Ask AI gate. Manual editing stays available. Unresolved work survives restart/end-session. No fabricated percentages or AI authorship claims.

Completion: three consecutive live demos covering follow-up/pass and first-answer pass; trivial change suppression; duplicate/restart recovery; provider outage; stale versions; unauthorized reads. Review at least 20 real model answers with a human. These live checks cannot be replaced by deterministic test doubles. Target p95 under 10 seconds over 20 measured requests, retry UI at 30 seconds; report measurements, never assume them.

P1, after P0: Solana Devnet assessment receipt/independent verifier, ElevenLabs playback and reviewed transcription, Composio selected GitHub PR import and exact approved summary publication. Optional outages must not affect learning passes. Implement disabled-by-default adapters/UI only when capabilities are documented; mark live evidence separately.

P2 deferred unless demonstrated need: Elastic retrieval, hints/transfer questions, instructors, other languages, Baseten. No redundant databases, inference paths, hosting, or sponsor dashboards.

## Architecture and integration boundaries

- Frontend: reuse Figma's React + Vite + TypeScript source when recoverable. A separately labeled functional shell may be used for API verification while source is blocked; not a visual replacement. Routes `/` session, `/history`, `/history/:id`, `/settings`, `/verify`, secondary receipt and PR dialogs.
- Backend: FastAPI, Pydantic contracts, SQLAlchemy, one relational datastore. SQLite for zero-service local setup and tests; PostgreSQL/Supabase connection for deployment. Initial schema-v1 bootstrap script; future column changes require explicit migrations rather than `create_all`. Supabase Auth JWT (issuer/audience/JWKS checked) in production; explicitly enabled loopback-only development identity, never enabled in production. No client service-role secrets.
- Data: projects (owner/scope), sessions (state/integration), snapshots (hash/bounded frozen source/provenance/head), checkpoints (question/rubric/evidence/state/version), attempts (idempotency/version/input/evaluation/operational state), managed AI requests, wallet challenges, receipts, GitHub imports/publications. Owner-filter every query; transaction and conditional update protect transitions. Unique snapshot/attempt/receipt/publication keys.
- Processing: persist pending intent before external calls; network calls outside DB transaction; version/lease conditional writes afterward. Provider failures preserve unresolved gate; retry/reconcile explicitly. One operation per user at a time. State derived from durable records, never browser booleans.
- OpenAI Responses structured outputs validated with Pydantic. Treat source/comments/answers as untrusted data; no model-controlled tools or direct pass endpoint. Server validates evidence spans, decision coherence, rubric intent/mechanism/reasoning, and frozen snapshot/version bindings. Missing context returns unable-to-assess.
- Capture: local CLI/VS Code companion reads saved Git changes without changing staging, honors ignore/scope/secrets/generated/binary exclusions, filters whitespace, bounds 200 changed + 300 context lines, hashes snapshots. Five-second save debounce in extension. Explicit source preview/approval before upload; no automatic whole-repository upload. Browser cannot observe local files by itself.
- Gate: server `/ask` checks unresolved work transactionally before calling its coding assistant. Local capture is reconciled before requests initiated through companion. Website manual capture cannot detect unsubmitted disk edits; disclose this limit. No universal external-assistant lock. An extension is a separate install, not a website feature.
- Changes reach BeProgram through authenticated capture POSTs; answers/history through API. Source edits to this repository reach the hosted website only through build + deployment. Figma Make is a reference/export source, not an automatic bidirectional deployment integration.

## Frontend contract

Preserve E01–E12 session/checkpoint navigation, W01 history/W02 evidence/W03 empty history, S01 settings, dark/light tokens and SQL parameterization fixture after retrieving source. Replace fixture-driven state with API state, keeping source components/layouts. Never seed fake completed evidence into real history.

States: auth loading/sign-in/expired; session idle/active/paused/ended/restoring; capture reviewing/skipped/pending/unavailable; checkpoint pending/evaluating/follow-up/passed/unavailable; empty/error/retry history; services unconfigured/available/failing. After three unsuccessful answers offer Pause without passing. Show evidence path/lines, provenance, partial coverage, provider disclosure, gate reason, attempt history and assistance level.

Responsive verification at 1440px and 390px; keyboard focus, semantic labels, contrast, long feedback and zoom. Mobile stacks panels and scrolls code without page overflow. Voice click-to-record, Stop/Cancel/90-second bound/edit transcript/explicit submit. Receipt and publication each require exact preview followed by a separate action.

## API contracts

All errors: `{code,message,retryable}`. Private routes require bearer identity and owner checks; mutation idempotency/version required where retries matter. OpenAPI generated at `/docs`.

| Routes | Contract |
| --- | --- |
| GET /v1/config | Enabled capabilities, public auth configuration; no secrets |
| POST/GET /v1/projects | Name and explicit file scope; owned project list |
| POST /v1/projects/{id}/scope | Updated name/scope/exclusions plus expected_scope_hash; stale edits rejected |
| POST /v1/sessions; POST /v1/sessions/{id}/end | Start or restore scoped session; end preserves unresolved work |
| POST /v1/sessions/{id}/changes | Bounded saved files/before/after/context + provenance + idempotency; skip/checkpoint |
| GET /v1/checkpoints/{id}; POST .../answers | Frozen checkpoint; text, version, snapshot hash, idempotency key; validated evaluation |
| GET /v1/attempts/{id}; GET /v1/sessions/{id}/gate | Reconciliation and durable availability reason |
| GET /v1/history; GET /v1/sessions/{id}/history | Actual owned evidence and attempts |
| POST /v1/sessions/{id}/ask | Controlled assistant request; conflict if unresolved |
| DELETE /v1/projects/{id} | Owned local evidence deletion; no passing result; separate external-record warning |
| POST /v1/wallet-challenges; /v1/receipts/preview; /v1/receipts | P1: expiring signed challenge, exact disclosure, durable issue intent |
| GET /v1/receipts/{id}; .../export | P1: reconcile and immutable evidence export |
| POST /v1/receipts/{id}/reconcile; POST /v1/verify | Reconcile known signature; anonymous independent verifier with bounded RPC work |
| POST /v1/audio/transcriptions; /v1/checkpoints/{id}/speech | P1: bounded ephemeral audio and explicit speech |
| POST /v1/github/import; /v1/publications/preview; /v1/publications | P1: selected repo/head, exact approved content and destination |

## Ordered milestones

1. **Inspection and plan (in progress):** record actual availability; runtime bootstrap; verify API docs and boundary. Deliver this document before application code. Exit: feasible core architecture; specific design/credential blockers recorded.
2. **Core backend:** schema/migrations, auth/ownership, filters, OpenAI adapter, state machine, managed ask gate, redacted Sentry tracing/logs. Dependencies: runtime/package install. Verify with fixture provider only in tests: pass/follow-up/outage/duplicate/stale/restart/owner isolation/concurrency. Do not expose mock evaluator in production.
3. **Website and capture integration:** recover Figma source and connect UI; explicit functional shell if source remains blocked; CLI plus minimal VS Code capture companion with saved-change preview. Verify end-to-end API contract, built assets and capture safety; later desktop/mobile comparison against source. Figma fidelity remains blocked until accessible.
4. **History/recovery/security:** durable evidence, session restore, data deletion/30-day raw context retention command, typed failures/rate/size limits, browser flow tests, deployment Docker/config. Verify restart/duplicates/CSRF/CORS/JWT and secret/telemetry redaction.
5. **Solana:** feasibility check SAS first; if deployment/API cannot be verified, documented Memo fallback. Server issuer signs minimal version/digest, fresh learner challenge, canonical package+nonce, persist signed transaction before send; reconcile known signature. Independent RPC verifier checks Devnet/issuer/program/digest/expiry; no revocation claim. Test tamper/wrong issuer/replay/timeouts; live issuance requires configured funded test issuer. No fake transaction IDs.
6. **Voice:** ElevenLabs server adapter, ephemeral upload, playback/record/stop/cancel/review. Verify adapter failures and browser text fallback; live mic/provider check requires credentials/browser. No voice cloning.
7. **GitHub:** verify actual Composio tools/connection contract; selected PR import + immutable head, preview digest, explicit publication, head recheck and remote marker reconciliation. No unrequested comments during development. Verify stale head/wrong owner/duplicate timeout with doubles; real read/write acceptance requires authorized demo destination.
8. **Release verification:** full automated checks, three live demos and 20-answer human review when credentials available, desktop/mobile Figma comparison, setup/run/deploy docs, track evidence log with honest status. Do not mark missing live work complete.

At every milestone and major integration: update this document with checks, remaining work, constraints, decisions and downstream effects; report a concise update. Never silently remove unmet acceptance checks.

## Credentials, services, and operations

`.env.example` documents DATABASE_URL, Supabase URL/JWKS/audience, OPENAI_API_KEY/model, SENTRY_DSN, optional ElevenLabs key/voice, Devnet RPC/issuer key/trusted issuers, Composio API key and authorized connection references. Check existence only; never print values. Browser receives only public Supabase URL/anon key and capability flags. Disabled features fail clearly.

Local: isolated Python environment, install backend requirements, migrate, run FastAPI; Node install/build Vite and extension. Tests use temporary databases and explicit dependency injection. Deployment: one API container plus static UI served by it, TLS reverse proxy, PostgreSQL, production JWT auth, allowed origins, resource limits, backups, readiness checks, secret manager, retention job. No deployment or account creation is assumed authorized beyond preparation.

Sentry: explicitly redact request bodies, headers, provider spans and exception text; opaque IDs only; logs/traces must fail open. Need real payload inspection and an observed issue/fix for live track evidence. Rate/timeout bounds protect paid endpoints. Raw audio is not persisted; third-party retention is disclosed, not promised away.

## Risks and remaining decisions

- Initial Figma plugin resource access failed; the supplied ZIP resolved source access. Visual inspection now uses the exported source and rendered local screens. A hosted Figma screenshot/pixel comparison remains unavailable; no claim of one is made.
- No CLI assistant lifecycle available: choose managed Ask AI now; later Claude hooks require installed-version verification and opt-in configuration.
- Production Supabase/Postgres, paid provider access, wallets, real GitHub connection, deployment host and domain not configured; implementation can be tested locally but live service claims remain blocked.
- SQLite serializes local writes; production PostgreSQL needs migration and concurrency verification. Do not add a second datastore.
- Canonical receipts export private evidence: explicit download/share action; irreversible on-chain commitments disclosed. Devnet can reset; Memo fallback has no revocation.
- P1 integrations will not be counted as demonstrated without real outputs. P2 remains out of core scope.

## Verification references

- https://developers.openai.com/api/docs/guides/structured-outputs (opened: structured schema validation)
- https://code.claude.com/docs/en/hooks (opened: lifecycle candidate, installed behavior unverified)
- Figma plugin response and failed resource reads as detailed above.

## Progress log

- Initial plan written before application code. Inspection complete except inaccessible Figma contents. Runtime bootstrap and provider feasibility next.
- Milestone 1 complete: isolated Python 3.12 + Node 22 downloaded; Python dependencies installed. Claude absent, managed Ask AI selected. User supplied `C:/Users/Mathe/Downloads/BeProgram.zip`, imported with path/size validation to `apps/dashboard`. This resolves the source-access blocker. Export confirms React 19/Vite 8/Tailwind 4, custom icon library, dark/light tokens, E01–E12, W01–W03, S01 and v3 dialogs. No asset files were included in the ZIP; inspected screens use the source icon library. Export's AGENTS statement that a Figma dev server is already running applies to Figma's host, not this workspace.
- Milestone 2 locally verified: 13 API/security/state tests pass. Tests cover first-answer and follow-up pass, gate, duplicate/stale submissions, provider outage/retry, restart, ended-session unresolved state, ownership, three failures preserving lock, durable concurrency lease, deletion, redaction, and invalid model pass rejection. Deterministic evaluator is test dependency injection only, never a selectable production service. Live OpenAI/Sentry checks remain unverified. Test runner requires Windows sandbox escalation for temp database access.
- Inspection found mocked behavior in the export: timers for connection/evaluation/persistence; keyword/length pass; unconditional follow-up pass; fixture history; simulated microphone, chain verification, and PR publication. Remove these from live navigation while preserving source components, layout, icons and tokens. The prototype rail is a demo harness, not an actual coding-assistant integration. Website navigation will expose real session/history/settings/verifier routes; the illustrative VS Code shell remains reference material, not a claimed extension host.
- A real local defect was found and fixed: Sentry logger was not imported as a module, causing telemetry finalization to turn successful requests into 500s. Explicit import and fail-open logging fixed all affected tests. This is local debugging evidence, not a claim of a live Sentry incident/trace.
- Milestone 3 underway: local Git capture CLI written (saved files, ignore/scope/secrets, no staging mutation); original frontend now being connected. No optional service enabled yet.
- Milestone 3 checkpoint: TypeScript check and Vite production build pass; original ExtensionPanel now receives real question/evidence/history data through a React context, with unchanged layout/token classes. Live entry point is `LiveApp.tsx`; original `App.tsx`, `Website.tsx`, and `v3.tsx` remain reference-only and are not imported by the production entry. Real Supabase/local sign-in, project/scope selection, capture approval, checkpoint answer/retry, managed Ask AI, durable history and deletion are wired. 14 backend/capture tests pass, including staged+unstaged capture without index mutation. Browser/extension-host verification still pending.
- Bounds review found that an oversized single diff hunk could be skipped entirely. Changed capture to retain a labeled bounded prefix and include a full-change hash; added regression coverage. Template-literal whitespace is conservatively treated as meaningful. This prevents silent loss of large/semantic edits.
- P1 feasibility begins only after local core API and frontend build checks passed. Credentials still absent; no live sponsor demonstration is claimed. SAS docs were reachable, but no configured issuer/schema/funded wallet exists to prove SAS issuance. Implement the documented Memo fallback as optional anchored evidence, with unsupported revocation disclosed; live Devnet acceptance remains a release blocker for that optional feature.
- Milestones 5–7 implementation checkpoint: optional Memo receipt challenge/preview/consent/sign/broadcast/reconcile/export and DB-independent RPC verifier implemented; ElevenLabs TTS/STT and browser MediaRecorder/review implemented; Composio selected PR import and exact summary preview/publication implemented. These are live adapters with no production simulator, but all external-provider demonstrations remain blocked by absent credentials/connection/wallet. Twenty tests pass with explicit test doubles, including receipt tamper/unknown issuer/challenge replay and uncertain broadcasts, PR head checks, wrong owner/preview rejection and timeout reconciliation without a duplicate comment.
- Composio approach revised after reading current official API docs: use v3.1 authenticated proxy with fixed GitHub endpoints and server-validated user/active-connection/auth-config binding. This avoids unverified generated tool slugs and toolkit-version assumptions. Local Composio CLI is absent; product uses HTTP adapters, not the assistant's own connected accounts. No external comment was posted in development. New auth links use `connected_accounts/link`, not the retired managed-OAuth initiate route.
- Separate VS Code companion added with SecretStorage, scoped saved Git preview, five-second save notification debounce and capture-before-managed-Ask-AI. `node --check` passes. Actual extension-host operation remains a manual acceptance check. It opens the companion browser for questions/voice; no in-editor microphone or external assistant control is claimed.
- Operational additions: durable per-owner mutation rate windows, one operation lease, streamed request size bounds, daily raw-source retention command, private receipt packages removed as whole immutable exports on expiry. Public chain commitments/remote comments remain separate. No hosted deployment exists yet.
- Milestone 4/release checkpoint: 29 backend tests pass, including actual RSA JWT validation, Sentry error/transaction/log envelope inspection, interrupted-evaluation recovery, scope conflicts, retention, fresh-repository staged capture and explicit reviewed-voice submission. PostgreSQL uses a private `beprogram` schema with public/anon/authenticated access revoked during bootstrap; deployed role grants remain a host setup step. This avoids relying on API ownership checks while exposing tables through Supabase's public schema.
- Browser verification: 2 Chrome scenarios pass against actual FastAPI routes with an explicitly injected **test-only** evaluator and temporary database. Coverage includes project creation, capture approval, follow-up, reload, pass, managed Ask AI, evidence, scope persistence, optional-service absence and public verifier unknown-issuer behavior. Screens inspected at 1440px and 390px and in light mode; original ZIP `index.css` and `lib/icons.tsx` match byte-for-byte. Screenshots are test evidence, not live OpenAI results.
- Browser testing exposed a combined label/helper accessible name and clipped narrow-screen code metadata. Fixed semantic input labels and caption wrapping while retaining the original tokens/layouts. Also fixed delayed voice responses after cancellation and retained reviewed-voice modality. Build/typecheck and browser checks pass after these fixes.
- Final state review found re-uploading an unavailable checkpoint could regenerate its frozen question. Duplicate capture now returns the existing record; question and explanation retries stay explicit. Regression coverage verifies the saved question/version and provider-call count. Capture now includes staged source before the first Git commit without changing the index.
- Local deployment smoke: schema bootstrap succeeds; real app returns healthy status, serves the built website, rejects unauthenticated project reads, and accepts the generated local token. `.env` was created only because absent; secrets were not printed. Live provider flags are all false. Docker is not installed, so supplied Docker/compose assets have not been executed.
- Feasibility limits preserved: receipt issuance is the documented Memo fallback with no revocation; independent trust is configured outside the evidence package. Devnet identifier checked against official Solana documentation (https://solana.com/docs/payments/agentic-payments/x402). Optional credentials/account/microphone checks, extension-host acceptance, actual provider latency and human assessment review remain unresolved. These requirements were not replaced by fixture tests.

## Final implementation decisions and remaining work

- Actual schema: `projects`, `sessions`, `checkpoints` (embedded immutable snapshot/question JSON), `attempts`, `operations` (managed request/import/challenge/receipt/publication intents), `leases`, `rate_windows`. Owner IDs originate only in verified identity. Embedded evidence avoids unnecessary extra tables while preserving immutable bindings.
- Anonymous verification has a shared 30-operations/minute lease/rate budget, plus recommended per-client reverse-proxy limits. Source paths/answers/tokens are excluded from telemetry; opaque correlation IDs link errors, traces and lifecycle logs.
- Supabase sign-in supports pre-created/invited accounts. Self-service registration and password recovery are not implemented and are not implied by account connection. The extension uses SecretStorage but requires manual reconnect on token expiry; a secure browser-to-extension OAuth handoff is a later integration improvement.
- Capture uses a saved working-tree versus HEAD baseline, with server duplicate detection and a five-minute recent-concept policy. Extension save events notify after five seconds and ask for source-preview approval; they do not silently upload. Website-only requests cannot detect unsubmitted disk edits. Missing context yields unavailable, preserving the gate; broader-context amendment is not implemented. Repeated missing context requires revising approved project/capture workflow, not a fabricated assessment.
- Superseded browser-only companion decision: the separately installed extension now embeds the actual Figma checkpoint components in a VS Code WebviewView. A validated host bridge owns capture, API calls, versioned answers and managed requests. Questions/follow-ups/results stay in the sidebar; dashboard links are explicit. Actual host and renderer tests now verify this boundary. Browser voice remains optional because webview microphone support has not been verified.
- Local build warns about a 513 KB JavaScript chunk (about 143 KB gzip); no correctness failure. Code splitting can follow measured loading needs. Two third-party test-runner deprecation warnings remain. No speculative infrastructure was added.
- Next required actions after configuration: run the live checklist in `docs/VERIFICATION.md`, inspect any provider schema differences, complete the human review/latency record, run PostgreSQL and Docker checks, choose a host/domain and deploy according to `docs/DEPLOYMENT.md`. Optional services can stay disabled while core live acceptance is performed.

### Extension delivery artifact

- Local package: `artifacts/beprogram-companion.vsix`, version 0.2.0, 12 archive entries, about 98 KB. SHA-256: `ed632c4ebce9f4d071e537be4cf74151a686ae262624194a2578f680a17db585`.
- Packaged files are limited to the host modules, manifest/readme/notices, icon and compiled webview JS/CSS. No tokens, .env, test fixtures, test profiles or node_modules are shipped. Packaging runs syntax checks, TypeScript/sidebar build and extension unit tests first.
- A syntax regression during final cleanup was caught by artifact verification and fixed before delivery. The artifact was rebuilt and its extracted contents rerun in an isolated real VS Code host successfully. Future packaging now runs checks automatically.
- Unsent explanations are host-memory-only across webview disposal, not durable across a full editor restart. Submitted explanations and durable checkpoint state restore from the backend. Token refresh remains manual reconnect. Webview uses the original font-family tokens with installed system fallbacks; it does not fetch Google Fonts over the network.
