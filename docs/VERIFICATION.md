# Verification record

Recorded 19 September 2026. Local automated evidence is distinct from provider-backed acceptance.

## VS Code sidebar delivery

The checkpoint flow now runs inside an actual VS Code sidebar, superseding the original browser-only companion. Version 0.2.0 is packaged at `artifacts/beprogram-companion.vsix` (12 archive entries, approximately 98 KB). Its SHA-256 is `ed632c4ebce9f4d071e537be4cf74151a686ae262624194a2578f680a17db585`.

- **7 extension unit tests passed:** validated message boundary, stale bindings, retry/idempotency preservation, busy operation rejection, trust/origin restrictions, token isolation/disconnect and Windows case-aware path containment.
- **6 integration check groups passed in installed VS Code:** real extension activation and React webview handshake; CSP/local resource restrictions; saved Git preview/cancel/approval; adaptive follow-up/stale rejection and controller restart recovery; persisted pass/matching dashboard history/managed response in the editor; SecretStorage disconnect and private-state clearing. The final run used the exact contents extracted from the delivered VSIX.
- **3 browser scenarios passed (15.2 seconds):** the two dashboard scenarios plus the compiled sidebar talking through the actual host controller to FastAPI. Sidebar coverage includes a draft surviving webview reload, pause without unlocking, follow-up/pass and controlled AI response without browser navigation.
- **29 backend tests passed (7.77 seconds)** after the extension work, with the same two dependency deprecation warnings. Website and sidebar TypeScript/build checks pass. Sidebar JavaScript is approximately 261 KB (79 KB gzip).

Host tests use an isolated VS Code profile, temporary Git repository, real SecretStorage/documents/webview and the actual API. Native consent/input prompts are automated by test injection; assessment is explicitly a test-only provider. This verifies extension integration, not live OpenAI assessment quality. Tests did not install anything into the user's normal profile or publish an extension.

Rendered sidebar evidence (synthetic test data; original Figma tokens/components): [narrow checkpoint](screenshots/vscode-sidebar-checkpoint.png), [verified result](screenshots/vscode-sidebar-verified.png), [wide light theme](screenshots/vscode-sidebar-light-wide.png). Widths 360px and 800px were visually inspected, with no horizontal page overflow. Packaged webview assets do not fetch remote fonts; original font-family tokens use local/system fallbacks.

Rerun with Node/npm on PATH:

```sh
npm --prefix apps/vscode-extension run build
npm --prefix apps/vscode-extension test
npm --prefix apps/vscode-extension run test:host
npm --prefix apps/vscode-extension run package
```

The host runner defaults to installed Windows VS Code; configure `BEPROGRAM_VSCODE_EXECUTABLE` for another location/platform. Packaging runs syntax checks, build and unit tests before writing the artifact. A final cleanup syntax regression was caught and corrected before the successful packaged-host run. The Windows drive-case bug found in the first host run has explicit regression coverage.

## Executed checks

| Check | Result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest tests -q --tb=short` | **29 passed**, 2 third-party deprecation warnings; latest run 3.99 seconds |
| `npm run build` in `apps/dashboard` | TypeScript and Vite production build pass; chunk-size warning at approximately 513 KB / 143 KB gzip |
| `npm run test:e2e` | **3 passed** in installed Chrome; actual API/database, explicitly test-only evaluator |
| Extension syntax/build/unit/host checks | Pass; actual installed VS Code and final package verified as described above |
| `python -m compileall -q backend integrations apps/receipt-verifier` | Pass |
| `python -m backend.migrate` | Local SQLite schema bootstrap succeeds |
| Running actual app on `127.0.0.1:8000` | `/health` healthy, homepage 200, unauthenticated projects 401, authenticated projects 200 |
| Production bundle inspection | Test evaluator response and simulated PR-comment marker absent |
| Figma source preservation | ZIP `src/index.css` and `src/lib/icons.tsx` unchanged byte-for-byte |

The test suite covers pass/follow-up, duplicates, stale versions, owner isolation, provider outages, retry preservation, restart and lease recovery, ended-session lock, three failures without false pass, malformed pass rejection, scope conflicts, deletion/retention, large bounded edits, saved Git index preservation, staged files before first commit, actual RSA JWT signature/issuer/audience/expiry/role checks, and redaction of emitted Sentry envelopes. It also checks wallet challenge replay, signed transaction persistence before uncertain broadcast, receipt tamper/unknown issuer, selected PR head/preview/owner checks, comment timeout reconciliation, and transcription review before submission.

The browser flow exercises sign-in, project creation, start, approved capture, question, weak answer, follow-up, reload recovery, pass, managed request, actual persisted two-attempt history, scope settings/reload and absent optional services. The independent verifier is reachable without sign-in and reports unknown issuers honestly. There were no page JavaScript errors during the learning flow. Tests explicitly inject provider doubles; the application has no mock-evaluator mode.

## Visual inspection

Screens were inspected at 1440×1000 and 390×844, including mobile evidence and light theme. The original responsive checkpoint composition, colors, typography tokens, icons, badges and history/evidence composition are reused. Captured source scrolls within its panel; the mobile page has no horizontal document overflow. Input labels and modal keyboard/focus behavior were corrected without replacing the visual system.

Saved test screenshots:

- [Desktop checkpoint](screenshots/desktop-checkpoint.png)
- [Mobile checkpoint](screenshots/mobile-checkpoint.png)
- [Desktop evidence](screenshots/desktop-evidence.png)
- [Mobile evidence](screenshots/mobile-evidence.png)
- [Light evidence](screenshots/light-evidence.png)

These contain synthetic test records; the evidence model is labeled `test-only-fixture`. They are not screenshots of a live OpenAI assessment. The Figma plugin exposed the source inventory but its resource URLs were unreadable. The user's ZIP supplied the actual components. A hosted Figma pixel comparison could not be performed.

For local reruns with installed Chrome when Playwright's browser download is unavailable:

```powershell
$env:BEPROGRAM_BROWSER_EXECUTABLE = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
cd apps/dashboard
npm run test:e2e
```

The Playwright browser download encountered a Windows/OneDrive installation-lock error; tests used isolated headless Chrome with a fresh profile. No existing browser profile was accessed. Build processes and some temporary-file tests needed approved execution outside the Windows sandbox.

## Live acceptance still required

Configure credentials locally or in the deployment secret manager; never paste them into chat. Record actual outputs and failures, without exporting source/answers into telemetry.

1. **OpenAI/core:** configure the key/model, run three consecutive real demos including immediate pass, follow-up/pass, trivial edit suppression and provider outage/retry. Review at least 20 representative explanations with a human, including paraphrases, vague correct-looking answers, misconceptions and insufficient context. Measure 20 real requests and report p95 against the PRD's 10-second target; verify the 30-second provider timeout/retry experience. No model-quality or latency acceptance claim exists yet.
2. **Auth/database:** use invited Supabase users with asymmetric JWT signing; demonstrate two real users cannot access each other's evidence. Migrate the private schema into the selected PostgreSQL instance, verify API-role grants and test simultaneous/stale operations and backup restoration there. Local SQLite and generated RSA tests do not certify the remote service.
3. **VS Code live pilot:** install the local VSIX, connect the chosen Git root with a real user token, preview/approve an eligible saved change, complete the sidebar checkpoint against live OpenAI and send the next managed request. Automated host/capture/persistence checks now pass; actual human prompt interaction, expired-token reconnect and paid-provider assessment still need the configured pilot. Other coding assistants remain outside the claimed integration boundary.
4. **Sentry:** set DSN, cause an authorized demo failure, and locate the redacted error, trace and log by opaque correlation ID. Demonstrate an actual improvement using delivered data. Memory-transport payload tests and local bug fixes are recorded, but no event delivery is claimed.
5. **Solana, optional:** use a funded Devnet-only issuer and test wallet. Sign a fresh challenge, inspect/approve the exact memo, confirm real issuance and independently verify the export with a separately selected trusted issuer. Test tampering, wrong issuer, reused challenge, RPC outage and known-signature reconciliation. No transaction was broadcast in development; revocation is unsupported.
6. **ElevenLabs, optional:** configure accessible voice/model credentials; test permission denial, real microphone capture, stop/cancel, identifier correction, explicit reviewed-text submission, playback/stop and provider failure. Browser controls and server contracts exist; live audio has not been exercised.
7. **Composio/GitHub, optional:** configure GitHub auth, connect as the actual BeProgram user, import an explicitly selected authorized PR and inspect frozen base/head/files. Pass its checkpoint, inspect the exact comment preview and approve a demo publication. Verify stale-head rejection and read-after-timeout reconciliation. No GitHub account was connected or comment posted during development.
8. **Deployment:** execute the supplied Docker/compose assets on a Docker-capable host, configure HTTPS/origins/proxy limits, test persistence/restart, backups/retention and private-schema exposure. Docker was not installed here; no deployment/domain was created.

Optional service failures do not count as learning failures and must never unlock a checkpoint. P2 retrieval, hints/transfer questions, instructors and other languages are deferred, as documented in the plan.
