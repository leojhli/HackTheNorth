# Three-minute core demo

The story: BeProgram asks a developer to explain a meaningful saved code change, follows up on missing reasoning, saves the evidence and enables the next BeProgram-managed AI request. Everything uses local inference. No wallets, receipts, sponsor dashboards or cloud setup belong in this walkthrough.

## Before presenting

1. Start the app with `./scripts/run-local.ps1` if it is not already running. Check http://127.0.0.1:8000/v1/config: local model available, receipts/voice/GitHub disabled. Start the app/model well before the demo to avoid cold-load delays.
2. Install `artifacts/beprogram-companion.vsix` in VS Code if needed. Do not enter an OpenAI key; connect with the local app token from `.env` in the native VS Code password prompt. Keep `.env` closed while screen sharing.
3. Run the command below to create an isolated Git folder. Each run makes a new folder and never resets your real repository:

   ```powershell
   .venv/Scripts/python.exe -m scripts.prepare_demo
   ```

4. Open the printed folder in VS Code, trust your generated fixture, create a BeProgram project and use scope `src`. The baseline copies an array; the saved edit deduplicates it with a Set. The source is deliberately synthetic; questions and results must come from the real local model.
5. The final 20-case run measured 75.765-second evaluation p95; the three-minute schedule below is a target, not verified presentation timing. Watch latency during rehearsal: sustained GPU use can be slower than the first few requests, so leave time for processing rather than promising instant grading. Rehearse once using a fresh fixture. Do not claim exact wording or a guaranteed pass: the question/rubric can vary. Keep the dashboard history link ready.

## Walkthrough

| Time | Action and explanation |
| --- | --- |
| 0:00-0:25 | Show `src/uniqueTags.ts` and its Git diff. Explain that working code alone does not show whether you understand its behavior. |
| 0:25-0:50 | In BeProgram, review the saved change, inspect the exact capture preview and approve. The local model generates a question about the change. |
| 0:50-1:20 | Give a deliberately vague answer in your own words, such as “It handles duplicates better.” Show the follow-up and that Managed Ask AI remains unavailable. |
| 1:20-2:05 | Explain the actual mechanism: Set keeps one occurrence of each value in insertion order; spreading it produces a new array; the input is not mutated; case-sensitive strings stay distinct and objects are compared by identity. Submit the explanation. |
| 2:05-2:30 | Show the saved assessment, then ask Managed Ask AI for one test for duplicate tags. Its real local response opens in an editor document. It does not automatically edit source. |
| 2:30-3:00 | Open learning history and show the captured code, explanations and feedback. State that only BeProgram's own assistant is gated; other assistants and manual editing stay available. |

## Recovery and honest claims

- If the model asks another relevant question, answer it. If it demands something unsupported by the source, preserve that result as a quality finding; do not force a pass or edit the database.
- If inference fails, show the saved answer and retry. The failure is not a wrong answer, and the checkpoint stays unresolved. Narrow the next demo capture if context is too large.
- If time runs out, show the documented earlier actual-model run and explicitly label it as recorded evidence. Do not call a fixture test or screenshot a live model result.
- Refresh/reopen once during rehearsal to check saved state. Confirm that a trivial whitespace edit does not trigger a new question.
- Remaining limitations: local model judgment needs human validation, local-only deployment, synthetic test cases, no universal assistant lock, no voice or PR publication in this edition.

## Human review before the event

Open `docs/assessment-review/HUMAN_REVIEW.md`. Independently judge each of the 20 explanations and record a decision and feedback notes. Those blanks are intentionally not filled by the coding assistant. Automated agreement with agent-authored expected labels does not complete human review.

Re-run the evaluation set with `.venv/Scripts/python.exe -m scripts.evaluate_local_ai` only when investigating a model/prompt change. Results are in `docs/assessment-review/results.json`; reruns archive the previous worksheet and results in a unique `previous-*` folder before generating a new blank worksheet.

## Automated rehearsal evidence

`python -m scripts.verify_local_ai --demo` runs this fixture through actual capture/question/follow-up/pass/managed request/history/restart behavior using the local model and a disposable database. The completed flow is saved in `docs/demo-rehearsal-result.json`. Its generated rubric incorrectly claims Set loses insertion order, and its vague-answer feedback credits unexplained mechanism knowledge. Treat it as successful integration evidence with known assessment defects. This verifies the API/model flow; installing and operating the sidebar yourself is still a separate human rehearsal.
