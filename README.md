# BeProgram

Explain meaningful saved code changes, receive contextual questions and follow-ups, and keep private evidence of understanding. The live app uses the supplied Figma Make components, icons, dark/light tokens, and checkpoint/history layouts. The original prototype orchestration remains reference source; it is not the production entry point.

Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for milestone status and unmet acceptance checks. This repository is an implementation, not a claim that paid providers, an external coding assistant, or a deployment have been connected.

**VS Code is the primary learning surface.** Install the local artifacts/beprogram-companion.vsix through **Extensions: Install from VSIX…**, open a trusted Git project and click the BeProgram Activity Bar icon. Capture, questions, explanations, follow-ups, pause/retry and verified results stay in the sidebar. See [extension setup](apps/vscode-extension/README.md). The website remains the supporting dashboard.

## Run locally

Prerequisites: Python 3.12+, Node 22.12+, Git. This Windows workspace also has ignored local runtimes under `.tools`.

```powershell
./scripts/setup-local.ps1
./scripts/run-local.ps1
```

Open http://127.0.0.1:8000. The setup script creates `.env` only if absent, with an explicitly local identity and a random `LOCAL_DEV_TOKEN`. Enter that token in the local sign-in screen. It is not a Supabase password. Add your OpenAI key in `.env` to enable real assessments, then restart the API to load configuration changes. Keep secrets out of chat and Git.

Portable manual setup:

```sh
python -m venv .venv
# Windows: .venv/Scripts/activate; macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.lock.txt
cp .env.example .env
# Configure Supabase, or AUTH_MODE=local plus a random 32+ character LOCAL_DEV_TOKEN.
python -m backend.migrate
cd apps/dashboard
npm ci
npm run build
cd ../..
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

For frontend development, run `npm run dev` in `apps/dashboard` alongside the API on port 8000. Vite listens on 127.0.0.1:5173 and proxies `/v1`. OpenAPI contracts are at `/docs`.

## Core workflow

1. Connect an account, create a project, and specify approved source paths (for example `src`). Start the session.
2. Capture saved Git changes with the CLI below or [VS Code companion](apps/vscode-extension/README.md). Inspect the generated JSON before uploading it via **Review current changes**. There is no seeded passing history.
3. Submit an explanation. OpenAI evaluates intent, mechanism, and reasoning against the frozen snapshot. A vague explanation gets a focused follow-up; a complete first answer can pass immediately. Missing credentials or provider errors preserve unresolved state.
4. A persisted pass updates history and permits the next **Managed Ask AI** request. Other assistants and manual editing remain available. The website cannot see unsubmitted local edits.

```sh
python -m integrations.capture /path/to/git/project --scope src > capture.json
```

The companion compares saved working-tree content against HEAD, includes staged and unstaged changes without modifying the index, honors ignored/excluded files, rejects likely secrets/binaries, and uploads only explicitly approved scope. A fresh repository without HEAD captures eligible staged and untracked files. Context is capped at 200 changed and 300 surrounding lines and labeled when partial.

For CLI-controlled requests, set `BEPROGRAM_TOKEN` in your shell (not a command checked into Git), then:

```sh
python -m integrations.capture /path/to/project --scope src --submit --session SESSION_ID --ask "Help with the next change"
```

This reconciles saved changes before calling the managed assistant. The separate VS Code extension offers the same boundary and renders the checkpoint directly in its sidebar. It does not install hooks into Claude Code, Codex, or Copilot; those clients are not gated. Suggestions are returned in an editor document, not automatically applied to source files.

## Configuration

All service keys stay on the FastAPI server. `.env.example` lists the variables.

| Service | Configure | Behavior when absent |
| --- | --- | --- |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL` | Assessment/Ask AI unavailable; no fake evaluation |
| Supabase Auth | `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`; asymmetric signing keys | Use explicit local mode for development only; production refuses local mode |
| PostgreSQL | `DATABASE_URL=postgresql+psycopg://...` | SQLite for local development only |
| Sentry | `SENTRY_DSN` | Product still works; no telemetry delivery claim |
| ElevenLabs | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | Voice controls hidden; text available |
| Solana | `SOLANA_ENABLED=true`, Devnet RPC, funded test `SOLANA_ISSUER_KEY` JSON byte array, independently selected `SOLANA_TRUSTED_ISSUERS` | Receipt issuance hidden; verifier reports unknown/unavailable rather than success |
| Composio | `COMPOSIO_API_KEY`, `COMPOSIO_GITHUB_AUTH_CONFIG_ID` | GitHub controls hidden |

Supabase users should be invited/created through your configured Auth project; self-service signup/password recovery is not implemented. Configure asymmetric JWT signing (ES256/RS256), expected issuer and audience. The app never exposes a service-role key. PostgreSQL tables use a private `beprogram` schema, not the default public API schema. Do not add it to Supabase's exposed schemas.

## Optional integrations

- **Receipts:** connect a test wallet with message signing, sign a fresh scoped challenge, inspect the exact digest-only memo and disclosure, then approve. Signed transaction bytes and signature are persisted before broadcast. Reconciliation rebroadcasts only identical bytes. An expired transaction is shown as expired; replacement issuance is not automatic. Private evidence exports contain code and explanations—share deliberately. Devnet can reset. **Revocation is not supported.** Integrity and issuer identity do not establish assessment quality or current wallet control.
- **Independent verifier:** the website verifier reads trusted Devnet RPC directly, without reading the history database. A standalone verifier can run separately with its own trusted issuer list:

```sh
python apps/receipt-verifier/verify.py receipt.json --trusted-issuer ISSUER_PUBLIC_KEY
```

- **Voice:** actual browser microphone capture, visible recording/Stop/Cancel, 90-second client limit and 10 MB server limit, ElevenLabs transcription, editable transcript, then explicit text submission. No audio is saved in the application database; temporary spooled files are closed. Provider retention depends on the ElevenLabs account. In-editor microphone support is not claimed.
- **GitHub:** connect through Composio, enter an exact repository/PR, inspect frozen base/head and included scope, and approve capture. Only selected passed PR checkpoints can generate a summary. The exact comment/destination is previewed and approved separately. Head changes block publishing. An uncertain write is reconciled by its unique comment marker and never blindly retried. No merge, approval, or code modification occurs. No comments were published during development.

## Verification

```sh
python -m pytest tests -q --tb=short
cd apps/dashboard
npm run build
npx playwright install chromium
npm run test:e2e
```

On this Windows sandbox, Vite child processes, browser downloads, and pytest temporary databases require approved execution outside the sandbox. Tests use explicit evaluator/RPC/GitHub doubles and a disposable test database. Those doubles are never selectable in the live app. Automated UI tests run the built frontend against the actual FastAPI routes with a test-only evaluator.

Latest results: **29 backend tests and 3 browser scenarios passed**, TypeScript/Vite builds, 7 extension unit tests and 6 actual VS Code host integration check groups passed. Desktop/mobile and light-theme screenshots were inspected. If browser installation is unavailable, set `BEPROGRAM_BROWSER_EXECUTABLE` to an installed Chrome executable before `npm run test:e2e`.

See [docs/VERIFICATION.md](docs/VERIFICATION.md) for exact results and pending live checks. Twenty representative OpenAI answers still need human review before calling the PRD acceptance complete. No latency benchmark or sponsor eligibility is claimed.

## Deploy

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Build the Docker image, configure Supabase Auth/PostgreSQL and server secrets, run the migration, then serve the API/static app behind HTTPS. A deployment has not been created automatically.
