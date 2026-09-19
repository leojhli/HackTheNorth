# BeProgram - free local edition

A VS Code learning checkpoint for meaningful saved code changes, with a supporting history dashboard. Questions, adaptive evaluation and Managed Ask AI run on **Qwen2.5-Coder through local Ollama**. No model API key, paid plan, subscription, trial or inference credits are required. The app and SQLite history run on your own computer.

The existing Figma components and styling are retained; navigation hides the deferred receipt verifier. Only BeProgram Managed Ask AI is gated; Claude, Codex, Copilot and manual editing remain independent. Model suggestions open in an editor document and are not automatically applied.

## Windows setup

Requirements: Python 3.12+, Node 22.12+, Git and VS Code. This workspace already has Python/Node under `.venv`/`.tools`. Local AI needs approximately 10 GB of free disk including the download/runtime/model. The inspected PC has 16 GB RAM and an RTX 2070 with 8 GB VRAM. CPU execution is possible but can be substantially slower.

```powershell
./scripts/setup-local.ps1
./scripts/run-local.ps1
```

Setup installs dependencies, builds the site/sidebar, creates `.env` only if absent, installs a checksum-verified portable Ollama runtime and downloads the local model. The first download requires internet (about 1.5 GB runtime ZIP + 4.7 GB model). Runtime and models live in `%LOCALAPPDATA%/BeProgram/ollama`, outside OneDrive. No administrator installer, account, startup service or system PATH modification is used.

For this existing workspace, the configuration has already been converted to local AI. On later launches, use `./scripts/run-local.ps1`. It starts the model server, then the backend at http://127.0.0.1:8000. Keep that backend terminal open.

1. Install `artifacts/beprogram-companion.vsix` with VS Code's **Extensions: Install from VSIX...** and reload if prompted. Version 0.4.0 reuses your saved token between projects and shows elapsed local inference time.
2. Open a trusted local Git project and click BeProgram in the Activity Bar.
3. Connect using `LOCAL_DEV_TOKEN` from your ignored `.env`. This randomly generated local password is **not an API key**. The extension stores it in VS Code SecretStorage.
4. Choose project scope (for this repository, try `apps/dashboard/src`), save a meaningful edit, review the source preview and approve capture.
5. Answer the question, complete any follow-up and use Managed Ask AI after the persisted pass. History is also available in the dashboard.

The model server runs separately in the background. To release its memory:

```powershell
./scripts/stop-local-ai.ps1
```

## Configuration and troubleshooting

`.env.example` contains all settings needed for the free local flow. Keep `.env` private. Existing provider keys are unnecessary; legacy OpenAI keys are ignored and hosted voice/Composio/Sentry cannot be enabled by setting old keys.

| Setting | Purpose |
| --- | --- |
| `AUTH_MODE=local`, `LOCAL_DEV_TOKEN` | Loopback-only local identity; no sign-up service |
| `DATABASE_URL=sqlite:///./beprogram.db` | Persistent local history |
| `OLLAMA_URL=http://127.0.0.1:11435` | Isolated local model endpoint; remote endpoints rejected |
| `OLLAMA_MODEL=qwen2.5-coder:7b` | Default free downloaded weights |
| `OLLAMA_CONTEXT=16384` | Context window; conservative input bounds prevent silent truncation |
| `OPERATION_TIMEOUT=120`, `LEASE_SECONDS=180` | Local inference time budget and durable operation lease |

If the model is missing, run `./scripts/setup-local-ai.ps1`. If unavailable, run `./scripts/start-local-ai.ps1`, then Refresh in BeProgram. The config endpoint checks installed model metadata; a green availability result is not an assessment-quality guarantee. A failed generation preserves the checkpoint and never grants a false pass. Initial model loading takes longer than subsequent calls.

If your machine struggles, use the smaller model:

```powershell
./scripts/setup-local-ai.ps1 -Model qwen2.5-coder:3b
# Set OLLAMA_MODEL=qwen2.5-coder:3b in .env, then restart BeProgram.
```

The smaller model may assess reasoning less reliably. The configured default and smaller fallback both use local weights. Experimental Qwen3/Qwen3.5 candidates were evaluated but not promoted because they introduced assessment errors. Ollama Cloud is disabled by the launcher; the backend rejects remote model metadata and never falls back to a hosted model. Input exceeding the configured context budget fails explicitly. For a saved oversized checkpoint, increase `OLLAMA_CONTEXT` up to 32768 if memory permits and retry; use smaller scopes for future projects. Do not silently discard evidence to obtain a pass.

## Other operating systems

Install the free Ollama runtime from https://ollama.com/download, then run a dedicated local server:

```sh
OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 ollama serve
# In another terminal:
OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen2.5-coder:7b
python -m venv .venv
# Activate .venv for your shell.
pip install -r backend/requirements.lock.txt
cp .env.example .env
# Set LOCAL_DEV_TOKEN to a freshly generated random value of at least 32 characters.
python -m backend.migrate
cd apps/dashboard
npm ci
npm run build
cd ../..
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

For frontend development use `npm run dev` in `apps/dashboard`; Vite proxies `/v1` to port 8000. API contracts are at `/docs`. The local capture CLI remains available:

```sh
python -m integrations.capture /path/to/git/project --scope src > capture.json
```

Capture checks saved Git changes against HEAD without changing staging. It excludes ignored/generated/binary/likely-secret files, bounds context, previews approved source and preserves source provenance. A diff does not establish AI authorship.

## Optional features and track changes

- **Voice:** hosted ElevenLabs speech and transcription are disabled. Typed explanations remain the complete supported input path; there is no simulated or secretly cloud-backed voice replacement.
- **GitHub publication:** Composio is disabled. Local Git capture still works; no PR comment is published. A direct free GitHub adapter is future work.
- **Telemetry:** hosted Sentry delivery is disabled; there is no monitoring subscription requirement.
- **Solana:** deferred by product decision. Receipts and the verifier are hidden from the core demo; disabled API routes do not contact Solana. The implementation is retained for possible future use, but the Solana track is no longer targeted. No wallet or blockchain setup is needed.
- **Hosting/auth:** local SQLite and the token remove the need for Supabase or hosted infrastructure for this demo. Historical production Supabase/PostgreSQL support remains separate, optional and unverified in this delivery.

OpenAI, ElevenLabs, Composio, Sentry and Solana are no longer active track claims in this edition. Prior implementation evidence is retained as history. Overall/developer-tool eligibility and any local-model track must be checked against actual event rules; no prize eligibility is asserted.

## Verification

```sh
python -m pytest tests -q --tb=short
python -m scripts.verify_local_ai  # Actual local inference, synthetic examples, disposable DB
python -m scripts.check_local_misconceptions
cd apps/dashboard
npm run build
npm run test:e2e
cd ../vscode-extension
npm test
npm run test:host
npm run package
```

Browser/host tests inject explicit test-only evaluators, never production mocks. The live local smoke command uses the actual model for three different changes, vague-answer follow-ups, immediate pass, persistence/restart and managed requests. It writes synthetic evidence to `docs/local-model-smoke.json`. See `docs/VERIFICATION.md` for results and remaining quality checks.

Current release evidence and model-quality limitations are recorded in [verification](docs/VERIFICATION.md). Automated UI/state tests use explicit test evaluators; they do not establish real-model judgment quality.

A small local model is not guaranteed to match a hosted model's judgment. Keep the original human-review requirement: review at least 20 representative explanations before claiming reliable assessment quality. No cloud bill is required, but the computer, disk, electricity and initial download are your own resources.

See `IMPLEMENTATION_PLAN.md` for the living delivery record and `docs/DEPLOYMENT.md` for operation and deployment boundaries.

## Next: review and rehearse

See [the three-minute demo guide](docs/DEMO_REHEARSAL.md) and [the offline 20-answer human-review worksheet](docs/release-review/HUMAN_REVIEW.html). Create a fresh isolated Git example with `python -m scripts.prepare_demo`. Run the actual local evaluation set with `python -m scripts.evaluate_local_ai`; agent-authored expected labels are not a completed human review.

## Readiness and recovery

```powershell
.venv/Scripts/python.exe -m scripts.doctor
./scripts/run-local.ps1          # Reuses this workspace's running backend
./scripts/run-local.ps1 -Restart # Loads backend code or .env changes
```

The launcher refuses to stop an unrelated process on port 8000. Local lifecycle logs rotate at `.tools/logs/lifecycle.jsonl` (1 MB plus three backups). They contain operation names, opaque correlation IDs, outcome categories and durations; source, answers and tokens are excluded. Logging failure does not change the learning result. Disable with `LOCAL_LOGS_ENABLED=false`.

The supported delivery is a local prototype. Review model feedback and suggestions: a valid response can still contain a misconception or unfair grading. No test result substitutes for the 20-case human review and your VS Code rehearsal.
