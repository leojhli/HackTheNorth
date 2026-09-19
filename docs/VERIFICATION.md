# Release 0.4.0 verification - 19 September 2026

This section is current. Older evidence below is historical and may describe paid integrations no longer enabled.

- **63 backend tests passed**, 9 extension unit tests, 3 browser scenarios, production site/sidebar builds and 6 actual VS Code host groups. The host test used the exact extracted 0.4.0 archive; evaluator doubles verify state/integration, not grading quality. Two dependency deprecation warnings remain.
- VSIX SHA-256: `77a81a87be62b91d02189e04d4072b34b03c3ba37e1912fb620dfde047f8cde2`. Package metadata: `release-review/package.json`; host groups: `extension-host-results.json`.
- **Three consecutive real-model flows passed**: SQL parameter binding with follow-up, null guard with first-answer pass, nonmutating sort with follow-up; each persisted a pass, enabled a managed request, and survived service recreation. `release-review/final-flows.json`.
- **Beginner flow passed** with a simple question asking what the condition checks/returns; correct plain-language explanation accepted. `release-review/final-beginner.json`.
- **Six misconception/vague/instruction-override cases received follow-ups**, including incorrect SQL, null and sort explanations. `release-review/final-misconceptions.json`. No general injection-immunity claim.
- **20 actual evaluations matched 20 fixed agent labels**, no accepted false passes or operational failures in this run. p95 **5.36s**, maximum/cold first request **14.531s**. Dataset was reused in development, not held out; expected labels are agent-authored. `release-review/final/results.json` records model and exact code/data hashes. Human review is still pending.
- Compared Qwen3 4B Instruct and Qwen3.5 4B local weights; neither promoted because of unfair beginner rejection or response errors. Preserved failed candidate reports under `release-review/`; current model remains Qwen2.5-Coder 7B. Prompt revisions mean the final run is not a pure model-only comparison against earlier runs.
- Repeated startup reuses the workspace backend; controlled restart and read-only doctor passed. Actual synthetic missing-session request produced a redacted 404 lifecycle record. Local rotating logging and secrecy/fail-open behavior are tested. No hosted Sentry incident or delivery is claimed. Unrelated-port refusal is implemented; destructive interference with an unrelated live process was not attempted.
- Original UI preserved; current dark mobile and wide light sidebar screenshots visually inspected. Browser checks cover desktop/mobile, recovery/history and no page overflow. Screenshots are synthetic fixture data. Figma hosted pixel comparison remains unavailable; source ZIP is the visual basis.

## Remaining quality findings and acceptance

Passing workflow assertions do not mean generated code is correct. In the final SQL managed reply the model invented a null-email guard that the source does not contain. In the beginner managed reply it incorrectly claimed `canJoin(0, 0)` returns true; actual code returns false. Suggestions open for review and never auto-apply. Generated rubrics can also contain vague/incomplete limitations; one vague learner answer may be mislabeled a contradiction. Do not present reliable grading or correct code generation as established.

Open [the offline human worksheet](release-review/HUMAN_REVIEW.html), independently review the 20 cases, and export `human-review.json`. Run `python -m scripts.validate_review docs/release-review/human-review.json`. No review has been completed on the user's behalf. A real user's current-sidebar rehearsal is also pending. Optional voice, GitHub publication and Solana remain disabled/deferred; no cloud deployment was performed.

---

# Saved-answer quotation retry fix (19 September 2026)

The three-excerpt requirement incorrectly rejected a correct two-sentence answer. Passes now accept one to three distinct nonblank exact learner excerpts; semantic coherence checks remain unchanged. If a passing model response quotes nonexistent/source text, one extraction-only request sees learner explanations alone and must return verifiable excerpts. It uses the remaining operation budget. Missing/fabricated evidence still fails; this is not a proof of semantic correctness or prompt-injection immunity.

- **60 backend tests passed** (5.63 seconds, two existing warnings). Tests cover short quotations, missing/blank/fabricated/duplicate evidence, recovery input isolation and bounded timeout, unchanged follow-ups, same-key retry after failure, durable gate transition and completed-request deduplication.
- Actual reproduction using the user's saved answer/context returned pass with two matching quotes in 4.47 seconds. No raw learner text was written to this report, and no live history or grade was modified.
- Actual beginner demo passed question/follow-up/pass/managed request/history/recreation; inference took 4.45/3.73/3.56/2.23 seconds. See `beginner-demo-result.json`; prior report retained as `beginner-demo-before-quote-fix.json`.
- Six actual-model misconception/vague/instruction-override cases all received follow-ups. The script now accepts `--reference` and rejects partial reference reports clearly; run `python -m scripts.check_local_misconceptions --reference docs/local-model-smoke-before-beginner-prompts.json` to use the archived complete questions. See `local-model-misconceptions.json`. Prior outcomes are retained in `local-model-misconceptions-before-quote-fix.json`.
- Backend restarted on port 8000. The existing sidebar Retry reuses the saved answer. No extension/frontend changes or reinstall. Broader 20-case/human review is not repeated or marked complete by these checks; older three-quote assertions and fingerprints below are superseded.

# Beginner demo delivery (19 September 2026)

- New generator creates a complete, dependency-free Campus Game Night folder with HTML, CSS, event data, button logic, a small capacity helper, localhost preview launcher and plain-language START_HERE guide. Final folder: `.tools/demo-workspaces/campus-events-55e0e9c0`. Only `src/canJoin.js` differs from its committed baseline: a one-line guard refuses a full room. Capture verified exactly that one file; older folders/history remain untouched.
- Final browser check passed: 0/4/5/6 guests at capacity 5 and zero-capacity boundary; add/remove/reset; disabled full button; 1280px and 390px layouts; no overflow or browser errors. Screenshots: `screenshots/beginner-demo-desktop.png`, `screenshots/beginner-demo-mobile.png`.
- Final **49 backend tests passed** (5.04 seconds, two existing warnings). The BeProgram frontend and extension were unchanged; previous app browser/extension tests were not rerun as part of this fixture change.
- Actual final demo flow passed question, vague-answer follow-up, complete explanation, managed request, history and app recreation. Inference calls: 4.59/4.55/3.89/2.25 seconds. `beginner-demo-result.json` retains the full output. The question asks what the added if-statement checks; the passing feedback correctly explains the capacity boundary.
- This is not a clean model-quality pass: its reason imprecisely says "exceeds" rather than "reaches or exceeds", vague-answer flags call incompleteness a contradiction, and its generated Managed Ask AI test incorrectly says `canJoin(0, 0)` returns true. The browser check verifies false. No incorrect AI suggestion is applied automatically.
- Earlier comparison/prompt trials and an evidence-span failure are retained. Experimental global prompt/schema changes were entirely reverted after broader verification failed; the final assessor's SHA256 matches the prior 20-case report exactly. A fresh general smoke on the restored assessor still stopped at a valid SQL answer receiving an unfair follow-up (`local-model-smoke.json`). Previous successful evidence remains in `local-model-smoke-before-beginner-prompts.json`. Do not claim all actual-model examples passed this turn or that the underlying quality problem is solved.
- The final local backend and demo preview were restarted on 8000 and 8010. No API costs, new services, canned questions, seeded passes or automatic uploads were introduced.

# Focused demo and assessment review (19 September 2026)

This update supersedes the older counts and Solana acceptance target below.

Final calibration run: **18/20 outcomes matched the fixed agent labels**, with **zero accepted false passes**, one unfair follow-up on a complete answer and one operational refusal (`ungrounded_local_pass`) on a correct paraphrase. Thus two complete answers were not passed; the operational count overlaps that total. **Measured evaluation p95 was 75.765 seconds** (maximum 177.672 seconds), so the original under-ten-second target is not met. These are wall-clock measurements from this run, not a representative hardware benchmark. Human review remains incomplete.

- **49 backend tests passed** (9.03 seconds; two existing dependency deprecation warnings). New regressions cover disabled receipt routes making no RPC calls and the local model follow-up output contract. **3 browser scenarios passed** (18.6 seconds); website build passed with the existing bundle-size advisory. Default navigation has no verifier, its direct route explains that receipts are disabled, and mobile/desktop screenshots were refreshed.
- Solana remains implemented but disabled in local configuration. Its track claim is withdrawn. After restarting the final backend, `/v1/config` returned local inference enabled and receipts/voice/GitHub disabled; `/v1/verify` returned `503 receipts_disabled`.
- A real-model API rehearsal completed capture, question, weak-answer follow-up, complete-answer pass, managed request, history and restored app state. Four inference operations took 4.26, 4.77, 3.94 and 1.83 seconds. **This is integration evidence, not a clean assessment-quality pass:** the generated rubric falsely says Set does not preserve order; vague-answer feedback also credits reasoning not supplied by the learner. Raw evidence: `demo-rehearsal-result.json`.
- The response contract now requires quotation extraction before grading and an explicit follow-up question string. A passing empty question is normalized to public null; missing follow-up questions and unsupported passing evidence still fail closed. No fabricated replacement answer or forced pass is introduced.
- `assessment-review/` retains the baseline, unsuccessful trials, latest actual-model measurements and a blank human worksheet. Expected labels are agent-authored; after tuning, this is calibration data, not held-out accuracy. Semantic grading and question-generation defects remain open.
- `DEMO_REHEARSAL.md` and `python -m scripts.prepare_demo` provide a disposable Git example without modifying real projects or seeding history. Human review and operating the actual sidebar yourself remain pending. The extension source/package was unchanged in this milestone; its prior 7 unit tests / 6 host groups are historical verification, not rerun claims.

# Free local edition verification (19 September 2026)

This section supersedes the hosted-provider setup/acceptance instructions below. Earlier records remain historical evidence, not active services or current track claims.

- **47 backend tests passed** in the final run (12.16 seconds), with two third-party deprecation warnings. Includes native Ollama JSON-schema contract, blocked cloud endpoints/models, redirected endpoints, missing model, timeout, context limits, incomplete/malformed output, unsupported passing quotations, persistence/gate behavior and legacy keys unable to activate paid services.
- **3 browser scenarios passed** (15.4 seconds) against actual API/persistence with an explicit fixture evaluator. The new Connected services labels distinguish local assessment and disabled hosted features. Website/sidebar builds pass. The existing >500 KB website-bundle advisory remains; it is not a build failure.
- **7 extension unit tests and 6 VS Code host integration groups passed** for version 0.3.0. The host test ran the exact extracted final VSIX, not merely source. It verifies real webview/React handshake, CSP/token boundary, Git preview/approval, follow-up/version/restart, history/managed gate and SecretStorage clearing with a test-only evaluator.
- VSIX: `artifacts/beprogram-companion.vsix`; SHA256 `7c4b52307314dc836416062bc7a2fa786cdffb8da9927d85fb0a7970e2497810`. Packaged runtime files match source byte-for-byte. Updated host record: `docs/extension-host-results.json`.
- **Actual local inference:** portable Ollama v0.34.2, Qwen2.5-Coder 7B, RTX 2070 8 GB, 16 GB RAM. The official runtime ZIP SHA256 was checked and model download digest verification succeeded. Logs confirmed `Ollama cloud disabled: true`; dedicated server listens on 127.0.0.1:11435. `/v1/config` reports local_only, assessment available, hosted voice/GitHub disabled. Backend runs on loopback with SQLite/local auth.
- **Three actual-model flows passed** in an isolated database: SQL parameter binding (weak answer/follow-up/pass), null guard (first-answer pass), nonmutating sort (weak answer/follow-up/pass), each followed by a real local Managed Ask AI response. History survived app recreation. Final run: 11 inference calls, 1.45-4.89 seconds each after model load. An earlier cold-load call took 15.5 seconds. This is not the PRD's 20-request p95 benchmark. See `local-model-smoke.json`.
- **Six actual-model rejection checks stayed blocked:** five wrong/vague explanations got follow-ups; one grading-instruction attack still led the model to attempt a pass, but the server rejected it because its supporting quotations were not in the learner's answer. This last result is a server-side operational rejection, not a correct model grade. See `local-model-misconceptions.json`. No claim of general prompt-injection immunity is made.
- Visual evidence: desktop/mobile (1440/390 px), sidebar (360/800 px), dark/light scenarios pass; mobile checkpoint and wide light sidebar images were inspected. Original design tokens, layout and navigation remain. Screenshots use clearly synthetic test data. Source `index.css` and icons were not redesigned.

## Findings that changed implementation

The first model attempt skipped a meaningful SQL change because it lacked author motivation. Only the deterministic capture filter now skips identical/whitespace edits; local-model uncertainty stays unresolved. A second attempt invented query performance requirements. Prompts now constrain rubrics to visible purpose, mechanism and one relevant limit/tradeoff, and evaluate the latest answer afresh. A later grading-instruction attack exposed an unsupported pass. Local passing evaluations must now supply three exact excerpts from learner explanations; nonexistent quotations fail closed. A backend regression verifies that failed proof preserves the answer and keeps the gate locked.

All successful flow checks were repeated after these changes. Small-model judgment still needs broader review. **The 20-answer human review, representative held-out accuracy/false-pass evaluation, 20-request latency benchmark and a real user pilot remain outstanding.** Free local operation does not imply equivalent hosted-model quality or certified mastery. Conservative question handling may leave nonbehavioral edits beyond whitespace unresolved.

## Rerun the current checks

```powershell
.venv/Scripts/python.exe -m pytest tests -q --tb=short
.venv/Scripts/python.exe -m scripts.verify_local_ai
.venv/Scripts/python.exe -m scripts.check_local_misconceptions
# With Node/npm available:
npm --prefix apps/dashboard run build
npm --prefix apps/dashboard run test:e2e
npm --prefix apps/vscode-extension run test:host
```

Run the website build before backend tests, not concurrently: app creation mounts the built assets and Vite replaces that directory during a build. In this workspace, set `BEPROGRAM_BROWSER_EXECUTABLE` to the installed Chrome executable if Playwright Chromium is absent. Live scripts use synthetic source, temporary databases and actual local inference; they do not alter user projects, call paid services or publish anything.

Hosted OpenAI/ElevenLabs/Composio/Sentry acceptance is no longer a delivery target for this edition. Public deployment and live optional Devnet receipts remain separate, unverified work. The following historical record documents the previous implementation.

---

# Verification record

Recorded 19 September 2026. Local automated evidence is distinct from provider-backed acceptance.

**Current scope:** use the latest local release section at the end of this file. Earlier sections are historical; their paid-provider setup and acceptance instructions do not apply to the current local edition.

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

## Latest local release and beginner rehearsal — 19 September 2026

Supported release: **0.4.0**, local Ollama `qwen2.5-coder:7b`, FastAPI, SQLite and the existing React dashboard/sidebar. Only BeProgram Managed Ask AI is gated. Voice and GitHub publication are disabled; Solana is deferred. No paid-provider acceptance or public deployment is required for this edition.

Previously recorded release evidence in `IMPLEMENTATION_PLAN.md`: 63 backend tests, 9 extension unit tests, 3 browser scenarios, site/sidebar builds and 6 exact-package VS Code host groups passed. These suites were not rerun during this rehearsal preparation. Actual-model evidence is retained in [final flows](release-review/final-flows.json), [beginner flow](release-review/final-beginner.json) and [misconception checks](release-review/final-misconceptions.json).

The [frozen development evaluation](release-review/final/results.json) matched all 20 agent-authored labels, with recorded p95 5.36 seconds and cold maximum 14.531 seconds. This reused development set is not independent validation. Generated coding suggestions contained errors; passing automated flows does not establish reliable grading or suggestion quality.

Checks performed during this preparation: `python -m scripts.doctor` passed all readiness checks, including backend/model availability and token acceptance without printing the token. VS Code lists BeProgram 0.4.0 as installed. The archive SHA-256 matches [package metadata](release-review/package.json): `77a81a87be62b91d02189e04d4072b34b03c3ba37e1912fb620dfde047f8cde2`. A fresh isolated multi-file demo was generated and requested to open in VS Code. No user checkpoint result was fabricated.

**Still incomplete:** independent technical review of at least 20 representative explanations and a real person's sidebar rehearsal. The user can test clarity, navigation, waiting/retry behavior and history without certifying technical correctness. Do not treat beginner usability feedback as assessment-quality acceptance. See [the rehearsal guide](DEMO_REHEARSAL.md); the technical review worksheet remains available for a qualified reviewer.

## Latest: 0.4.1 visible actions and explanation help — 19 September 2026

- Added Managed Ask AI to the sidebar toolbar and passed-checkpoint screen, using the existing UI components. The action remains gated.
- Added Give up and explain for unresolved questions in both sidebar and dashboard. It requests a beginner explanation of the frozen code through local Ollama, saves it separately from learner attempts, and preserves checkpoint status/version and the locked gate. The explanation reappears after reload. History identifies help viewed; a later answer is not described as unaided. This does not implement or certify a fresh transfer-question assessment.
- Owner authorization, serial inference, cached repeat requests, output bounds, retry after model failure, project deletion and source retention apply. Explanation text expires with captured source; the help-viewed marker remains.
- **65 backend tests, 9 extension unit tests, 3 browser scenarios and 6 exact-package VS Code host groups passed.** Browser coverage includes give-up, persistence after reload, gate remaining locked, and the visible success-screen Managed Ask AI button. TypeScript/site/sidebar builds pass; existing dependency deprecations and dashboard chunk-size warning remain. The narrow explanation panel screenshot was inspected.
- [Actual-model explanation smoke](release-review/explanation-smoke.json) used synthetic capacity-check source and a disposable database. The explanation correctly described the comparison and equality boundary; the checkpoint remained pending and the gate unavailable. This single agent-inspected example does not establish independent model-quality acceptance.
- Packaged and installed 0.4.1, SHA-256 `9801f1a4f15374226cde44007aa4ede4bd08291758142f378aaaeec71113e34b`; [package metadata](release-review/package.json) identifies the exact host-tested archive. Backend restarted and doctor passed. Existing user history was preserved. Reload the user's VS Code window to activate the installed extension update.

Independent technical review and real user usability acceptance remain incomplete. The frozen 0.4.0 evaluation/worksheet is retained as historical evidence; it does not certify the new explanation feature.

## Latest: 0.4.2 practice after explanation — 19 September 2026

The user reported that the 0.4.1 experience worked well and explicitly selected practice after giving up. This is recorded as informal beginner usability feedback, not independent technical review or an observed completion of every acceptance step.

**Behavior:** after Give up and explain, Try a practice question generates a concrete new scenario from the same frozen code. A versioned operation retains its question/reference solution without overwriting the original question or attempts. Only answers submitted in the practice stage can earn `passed_with_help`. Help viewed, old answers, duplicate generation, failed inference and stale submissions cannot unlock the gate. Practice feedback addresses mistakes while retaining the frozen scenario. History and the success screen show Demonstrated with help; historical 0.4.1 results are not rewritten.

**Checks executed:** 76 backend tests, 10 extension unit tests, four browser scenarios and six exact-VSIX host groups passed. Coverage includes help prerequisite, owner isolation, stale versions/hash, invalid question rejection, failed generation/retry, restart, excluding original answers from practice grading, assisted-pass persistence, model-failure answer recovery, project deletion and guarded grade dimensions. Browser checks exercise both dashboard and sidebar practice through history and reload; narrow success and mobile assisted-history screenshots were inspected. TypeScript/site/sidebar builds pass. Existing dependency deprecations and dashboard chunk-size warning remain. An earlier backend test run overlapped frontend rebuilding and hit a transient missing-assets directory; the final run followed completion of the build.

**Actual-model evidence and failures:** initial practice generation repeated or assessed the original question. A later attempt produced a false pass on “8 is greater than or equal to 10”; [the initial failure](release-review/practice-initial-failure.json) is retained. Subsequent attempts encountered malformed/incoherent output and overlong follow-ups; [format failures](release-review/practice-format-failures.json), [coherence failures](release-review/practice-coherence-failures.json) and [the earlier flow](release-review/practice-before-format-fix.json) remain historical evidence. The release uses a dedicated exercise schema with a reference solution created before learner answers. The practice model returns bounded correctness dimensions, gaps, feedback and learner quotations; application code permits pass only when every dimension is correct with no contradiction or gap. It retains the same practice question for retries. Normal unaided assessment behavior is preserved.

The [final actual-model flow](release-review/practice-smoke.json) generated help and practice, rejected a wrong comparison, then saved the corrected explanation as `passed_with_help` and made the gate available. [Seven fixed practice regressions](release-review/practice-regressions.json) all matched agent-authored labels, including the previously accepted misconception, equality, correct reasoning and a vague answer. Rerun with `python -m scripts.check_practice_assessment`. These are narrow capacity-check development examples, not a held-out or independently reviewed quality estimate. Model-generated references, questions and feedback can still be incorrect.

**Delivery:** installed 0.4.2, SHA-256 `32efc1d372d6e7fda3179bab377d737ca0416f2e932d4f9e6f9b40ff62b7c2ca`. [Package metadata](release-review/package.json) identifies the extracted archive and final host report. Backend restarted and doctor passed; token and user history were preserved. Reload VS Code to activate the update. Independent technical review and usability acceptance of the new practice step remain open. No paid service, voice, Solana, GitHub publication or public deployment was enabled.
