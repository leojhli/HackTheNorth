> Free local edition (0.4.0): run the backend with `./scripts/run-local.ps1`. Questions, evaluations and Managed Ask AI use local Qwen2.5-Coder through Ollama; no provider key or credits are needed. Use `LOCAL_DEV_TOKEN` to connect. Hosted voice, Composio and Sentry are disabled. Local inference may take up to two minutes; failed attempts remain unresolved and retryable. See the root README for model installation.

﻿# BeProgram for VS Code

BeProgram's main learning flow now lives in the VS Code sidebar: approved saved change → contextual question → explanation → follow-up when needed → saved result → next Managed Ask AI request. The sidebar reuses the Figma checkpoint components and visual tokens. The website supports history and settings. Receipts, voice and GitHub publication are disabled in this edition.

## Install and try it

1. Start the backend from the repository root with ./scripts/run-local.ps1. The launcher starts local Ollama with cloud features disabled. Run ./scripts/setup-local-ai.ps1 first if the runtime/model is missing. No API key is needed; unavailable local inference never produces a simulated pass.
2. Install artifacts/beprogram-companion.vsix using **Extensions: Install from VSIX…**. Alternatively run the command below.
3. Open and trust a local Git repository. Click **BeProgram** in the Activity Bar, or run **BeProgram: Open checkpoint** from the Command Palette.
4. Click **Connect account**. Enter the backend's LOCAL_DEV_TOKEN for local development, for this supported local edition. Tokens are entered in a native VS Code password prompt and stored in SecretStorage, never in the webview.
5. Choose an existing project or **Create project**. Approve the intended relative source paths and start the session. For this BeProgram repository, use apps/dashboard/src; a typical application might use src. Scope currently accepts literal files/directories, not globs.
6. Save a meaningful JS/TS edit. After five seconds the extension offers a capture preview; you can also click **Review current changes**. Inspect the JSON document, then approve the exact saved snapshot in the native confirmation prompt.
7. Answer and follow up **inside the sidebar**. Pause keeps the checkpoint unresolved. After a persisted pass, click **Continue coding**, then **Send AI request**. Approve capture reconciliation and enter your request in the native prompt. Suggestions open in an editor document.

    code --install-extension ./artifacts/beprogram-companion.vsix

The extension compares saved working-tree files against HEAD without changing staging. It supports staged and untracked files before the first commit, honors ignores/exclusions, rejects likely secrets/binaries, and bounds capture. Unsaved editor buffers are excluded.

## Commands

- **BeProgram: Open checkpoint** — focus the sidebar.
- **BeProgram: Connect and start scoped session** — token, repository/project and scope confirmation.
- **BeProgram: Review saved changes** — preview/approve capture and show its question.
- **BeProgram: Managed Ask AI** — reconcile saved changes, check the durable gate and request a suggestion.
- **BeProgram: Refresh saved state** — reconcile backend state after reconnect/outage.
- **BeProgram: End session** — preserve evidence and unresolved checkpoints.
- **BeProgram: Disconnect account** — delete the token for this server and clear local private state.
- **BeProgram: Open learning history** — explicitly open the supporting dashboard.

Configure beprogram.apiUrl in VS Code User Settings for a different backend. Only HTTPS or loopback HTTP origins are accepted; changing servers requires reconnecting. Account sign-in in the browser and the extension are separate. No secrets or token-bearing URLs are passed to the browser.

## Build and launch from source

From the repository root:

    ./scripts/setup-local.ps1
    ./scripts/run-local.ps1

Setup builds both the website and sidebar. For UI-only changes, run ./scripts/build-extension.ps1. Select **BeProgram Extension** in Run and Debug and press **F5**; open your chosen Git repository in that Extension Development Host.

With Node/npm on PATH:

    npm --prefix apps/vscode-extension ci
    npm --prefix apps/vscode-extension test
    npm --prefix apps/vscode-extension run test:host
    npm --prefix apps/vscode-extension run package

Create the repository's artifacts directory before packaging if absent. The host runner defaults to the installed Windows VS Code executable; set BEPROGRAM_VSCODE_EXECUTABLE on another platform. It launches an isolated user/extension profile and temporary Git fixture, plus the actual API with an explicitly test-only evaluator. It does not change your normal VS Code profile or call the live local model.

## Persistence, safety and limits

The server owns all assessment and gate decisions. Messages from the webview are validated against a fixed action list; there is no arbitrary HTTP, shell or pass command. The webview loads packaged assets under a restrictive CSP with direct network access disabled. API requests and SecretStorage remain in the extension host.

Submitted explanations, attempts and session/checkpoint state survive backend or editor restart. Unsent drafts survive webview disposal/recreation while the extension host remains alive; they are kept only in host memory and are lost on a full editor/host restart. Access-token expiry requires reconnecting; automatic Supabase refresh/OAuth handoff is not implemented.

Only **BeProgram Managed Ask AI** is controlled. Claude, Codex, Copilot, manual edits and external clients remain available. Code suggestions are not automatically applied. Browser voice remains optional because webview microphone support has not been verified; the complete text checkpoint needs no browser. History/settings and optional receipt actions deliberately open the dashboard.

This is a local development package, not a Marketplace publication. Provider-backed assessment quality and production service acceptance still require the configured credentials and checks described in the repository's verification record.


## Local readiness

Run `.venv/Scripts/python.exe -m scripts.doctor` from the repository. Repeated `./scripts/run-local.ps1` reuses the existing backend; use `-Restart` to load code/configuration changes. The sidebar reuses your saved local token between projects and shows elapsed processing time. A model error preserves the submitted explanation without granting a pass.
