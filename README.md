# CodeProof

Understand the code you build with AI. CodeProof is a VS Code extension with a local dashboard: review saved changes, explain them, receive feedback, and keep your learning history.

Questions and coding suggestions run locally using Ollama and `qwen2.5-coder:7b`. No paid model API or inference credits are required.

## Start

From this workspace in PowerShell:

```powershell
./scripts/run-local.ps1
```

Keep the terminal open. The dashboard is at http://127.0.0.1:8000.

For a new installation, run `./scripts/setup-local.ps1` first. Requirements: Windows, Python 3.12+, Node 22.12+, Git, VS Code, and approximately 10 GB of free disk for the runtime and model. Initial setup downloads dependencies and weights.

Install `artifacts/codeproof-companion.vsix` through VS Code's **Extensions: Install from VSIX** command. Open CodeProof in the Activity Bar and connect using the private `LOCAL_DEV_TOKEN` from your ignored `.env`. The extension remembers it securely. Never share the token or display `.env` during a presentation.

## Use CodeProof

1. Open a local Git project and choose a small folder scope, such as `src`.
2. Make and save a meaningful JavaScript or TypeScript change.
3. Choose **Review saved changes**, inspect the preview, and approve it.
4. Answer the question in your own words and complete any follow-up.
5. If stuck, choose **Give up and explain**, then **Try a practice question**. Passing practice records **Demonstrated with help**.
6. After passing, use **Managed Ask AI** for a coding suggestion. Review results in **History**.

Only CodeProof's Managed Ask AI is gated. Other assistants remain available. Suggestions open for review and do not automatically edit files. The local model can give incorrect feedback or code; its correctness has not been independently validated.

## Manage projects

Open http://127.0.0.1:8000/projects or click **Projects** in the dashboard.

- **New project** creates a CodeProof record with your chosen folder scope.
- **Delete project** removes its saved sessions and learning history after confirmation.
- Your actual code files and folders remain on your computer.

See [project management](docs/PROJECT_MANAGEMENT.md).

## Try a small example

With the backend running, use another terminal:

```powershell
.venv/Scripts/python.exe -m scripts.prepare_demo --check --open
```

This creates a separate Git example and opens VS Code. Choose scope `src` and approve its prepared change. Follow the [beginner walkthrough](docs/BEGINNER_TEST.md).

## Troubleshooting

```powershell
.venv/Scripts/python.exe -m scripts.doctor
./scripts/run-local.ps1 -Restart
```

The doctor checks readiness without printing credentials. Restart after backend or configuration changes. If a checkpoint is too large, use a fresh project with a smaller scope and one small change.

To release the model's memory, run `./scripts/stop-local-ai.ps1`.

## Privacy and configuration

The app uses SQLite history and local-token authentication. `.env.example` documents configuration. Approved source excerpts expire after 30 days when the retention job runs; submitted answers remain until project deletion.

Optional Sentry Logs and Tracing require both `SENTRY_ENABLED=true` and a project DSN. Telemetry is disabled by default and excludes source, prompts, answers, and the local token. Set `SENTRY_ENABLED=false` to disable it. Bounded local logs are stored in `.tools/logs`.

Voice, GitHub publication, and Solana receipts are disabled. The supported setup is local-only; see [operation and deployment details](docs/DEPLOYMENT.md).

## Development

```powershell
.venv/Scripts/python.exe -m pytest tests -q
npm --prefix apps/dashboard run build
npm --prefix apps/dashboard run test:e2e
npm --prefix apps/vscode-extension test
```

FastAPI serves the React dashboard. SQLite stores history, and the extension handles Git capture and secure token storage. API documentation is at http://127.0.0.1:8000/docs.
