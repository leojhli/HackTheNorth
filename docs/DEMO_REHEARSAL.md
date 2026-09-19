# Beginner-friendly core demo

The story: BeProgram asks a developer to explain a meaningful saved code change, follows up on missing reasoning, saves the evidence and enables the next BeProgram-managed AI request. Everything uses local inference. No wallets, receipts, sponsor dashboards or cloud setup belong in this walkthrough.

## Before presenting

For nontechnical testing, use [the beginner usability checklist](BEGINNER_TEST.md). The technical review worksheet below is for a reviewer who can assess the code; it is not a requirement that a beginner certify model correctness.

1. Start the app with `./scripts/run-local.ps1` if it is not already running. Check http://127.0.0.1:8000/v1/config: local model available, receipts/voice/GitHub disabled. Start the app/model well before the demo to avoid cold-load delays.
2. Install `artifacts/beprogram-companion.vsix` in VS Code if needed. Do not enter an OpenAI key; connect with the local app token from `.env` in the native VS Code password prompt. Keep `.env` closed while screen sharing.
3. Run the command below to create an isolated Git folder. Each run makes a new folder and never resets your real repository:

   ```powershell
   .venv/Scripts/python.exe -m scripts.prepare_demo
   ```

4. Open the printed folder in VS Code, trust your generated fixture, create a BeProgram project and use scope `src`. Read `START_HERE.md` in that folder. It contains a runnable Campus Game Night website with several files. Only `src/canJoin.js` is changed: a new `if` check returns `false` when five or more guests are signed up. Previously it always returned `true`. Run `./start-demo.ps1` inside the generated folder and visit http://127.0.0.1:8010 to try the buttons. The source is deliberately synthetic; questions and results must come from the real local model.
5. Earlier calibration had slow and incorrect assessments; see the current release report in `docs/release-review/final/results.json`. The three-minute schedule below is a target, not verified presentation timing. Watch latency during rehearsal: sustained GPU use can be slower than the first few requests, so leave time for processing rather than promising instant grading. Rehearse once using a fresh fixture. Do not claim exact wording or a guaranteed pass: the question/rubric can vary. Keep the dashboard history link ready.

## Walkthrough

| Time | Action and explanation |
| --- | --- |
| 0:00-0:25 | Show the signup page and the tiny `src/canJoin.js` Git diff. Explain that working code alone does not show whether you understand its behavior. |
| 0:25-0:50 | In BeProgram, review the saved change, inspect the exact capture preview and approve. The local model generates a question about the change. |
| 0:50-1:20 | Give a deliberately vague answer in your own words, such as “It fixes the signup.” Show the follow-up and that Managed Ask AI remains unavailable. |
| 1:20-2:05 | Explain in your own words: if the count is five or more, the function returns false (no). With four guests it reaches return true (yes). The helper answers yes/no; the button code adds the guest. Submit the explanation. |
| 2:05-2:30 | Show the saved assessment, then ask Managed Ask AI for one test for a full five-person event. Its real local response opens in an editor document. It does not automatically edit source. |
| 2:30-3:00 | Open learning history and show the captured code, explanations and feedback. State that only BeProgram's own assistant is gated; other assistants and manual editing stay available. |

## Recovery and honest claims

- If the model asks another relevant question, answer it. If it demands something unsupported by the source, preserve that result as a quality finding; do not force a pass or edit the database.
- If inference fails, show the saved answer and retry. The failure is not a wrong answer, and the checkpoint stays unresolved. Narrow the next demo capture if context is too large.
- If time runs out, show the documented earlier actual-model run and explicitly label it as recorded evidence. Do not call a fixture test or screenshot a live model result.
- Refresh/reopen once during rehearsal to check saved state. Confirm that a trivial whitespace edit does not trigger a new question.
- Remaining limitations: local model judgment needs human validation, local-only deployment, synthetic test cases, no universal assistant lock, no voice or PR publication in this edition.

## Beginner usability rehearsal — next step

Technical review remains incomplete. You do not need to judge whether the model's coding advice is correct to try the interface.

1. In the generated folder, connect BeProgram and choose scope `src`. The existing saved capacity change is ready to review; no extra edit is needed for this first checkpoint.
2. Review and approve the preview, read the generated question and answer in your own words. Note anything confusing, including where to click or whether processing appears stuck.
3. If there is a follow-up, try answering it. If you cannot understand it, record that and stop; a pass is not required for useful usability feedback.
4. After a pass, try Managed Ask AI and open history. Check whether you can find your question and submitted explanation. Generated advice can be incorrect.
5. Report what you tried, what appeared, and what was confusing. Do not share the token or `.env` contents. This rehearsal is only complete once a person actually performs it.

For a later exercise, reject negative guest counts in `src/canJoin.js` while keeping its capacity check. Complete the first checkpoint before starting that edit.

### Practice after giving up (0.4.2)

On an unresolved checkpoint, choose **Give up and explain**, then read the saved walkthrough. Choose **Try a practice question** when ready. Explain the new scenario in your own words. A wrong or incomplete answer keeps the same practice question open with feedback; a successful answer shows **Demonstrated with help** and enables Managed Ask AI. History keeps the original question and attempts alongside the explanation and practice question. Reload once to check that the practice state remains available. Reading the explanation alone never passes a checkpoint.

The user reported that the 0.4.1 flow worked well. The new practice flow still needs their usability feedback. Neither report substitutes for independent technical review.

## Independent technical review — still incomplete

This is separate from beginner usability testing. A reviewer comfortable judging the code and explanations should complete it; the current user should not guess or certify answers they cannot assess.

Open `docs/release-review/HUMAN_REVIEW.html` in your browser. For each of 20 examples:

1. Read the code, question and explanation; choose your own verdict.
2. Reveal the model result and judge whether its feedback is accurate and relevant.
3. Choose **Unsure** whenever needed; do not guess. Add notes for disagreements.
4. Enter your initials and click **Save review file**. Save `human-review.json` in `docs/release-review`.

Progress is saved locally in the browser. Partial exports remain incomplete. Validate your export with:

```powershell
.venv/Scripts/python.exe -m scripts.validate_review docs/release-review/human-review.json
```

Agent labels are not an answer key. A completed worksheet can still contain unresolved disagreements. The worksheet is bound to the exact report fingerprint; do not overwrite its source report during the review.

## Automated rehearsal evidence

`python -m scripts.verify_local_ai --demo` runs the same small capacity helper through actual capture/question/follow-up/pass/managed request/history/restart behavior using the local model and a disposable database. The frozen release report is `docs/release-review/final-beginner.json`. Inspect question and feedback content as well as flow assertions: a successful flow alone does not establish grading accuracy.

The older `docs/demo-rehearsal-result.json` is retained as historical evidence for the superseded Set example; its false order claim is documented in the assessment review. Earlier capacity/prompt trials are retained because the model reversed comparisons or cited old source. The final fixture uses a straightforward added guard; experimental grading changes were reverted completely after a regression on another example. No canned question, automatic pass or synthetic history is used in the current demo.

A real person's sidebar rehearsal and the broader human review remain separate acceptance steps. The release assessor includes quote recovery and scope/difficulty guidance; prior results remain historical measurements, not a new quality pass. The final demo follow-up/pass flow succeeds, but model imperfections remain: it flags a vague answer as a contradiction and its Managed Ask AI response incorrectly claims canJoin(0, 0) is true. The actual code returns false. Review AI suggestions against running code; they are never applied automatically.
