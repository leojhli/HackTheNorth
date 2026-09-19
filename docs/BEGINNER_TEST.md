# Beginner usability check

This checks whether BeProgram is understandable and usable. You do not need to certify its coding advice or grading accuracy. If an explanation seems confusing or wrong, record that and stop rather than guessing your way to a pass.

## Start with a fresh example

In the BeProgram workspace terminal:

```powershell
./scripts/run-local.ps1
```

In another terminal:

```powershell
.venv/Scripts/python.exe -m scripts.prepare_demo
```

Open the printed folder in VS Code. Open BeProgram, connect, and choose scope `src`. Your saved token should be reused. If a password prompt appears, use the private local token as described in the README; never include it in screenshots or feedback. Keep `.env` closed while sharing your screen.

## Try the learning flow

1. Choose **Review saved changes**, inspect the preview, and approve the demo's `src/canJoin.js` change. Is it clear which code you approved?
2. Read the question and answer in your own words. Is the wording understandable? If the feedback is confusing, note its exact wording. A follow-up is allowed; repeated or unrelated demands are a finding.
3. If stuck, choose **Give up and explain**. Does the explanation help? Managed Ask AI should remain locked after reading it.
4. Choose **Try a practice question**. Is it a different example? Answer the example it actually asks. If accepted, the result should say **Demonstrated with help**. Do not copy an answer just to make the status change.
5. Open **Managed Ask AI**, request a test for the full-capacity case, and check that a response opens with its approved-file context. This is an unverified suggestion; it should not edit your files.
6. Open **History**. Can you find the question, your answer, the feedback, and the assisted result? Reload VS Code with **Developer: Reload Window** and confirm the saved history remains.

If you pass without help, that is a valid ordinary result. To test the assisted path, generate another fresh demo folder/project rather than resetting history. If you cannot finish, record where you stopped; an incomplete run is useful feedback.

## Record what happened

Copy this into your reply, leaving any untested item blank:

```text
Could connect and approve the intended file:
Question understandable:
Feedback understandable:
Give up / practice understandable:
Managed Ask AI button and saved-file context visible:
History survived reload:
Where I got stuck (exact message, if possible):
Waiting time felt reasonable / too long:
```

Do not include the token, private project code, or other people's information. This feedback is usability evidence only. Independent technical assessment review remains a separate unfinished requirement.
