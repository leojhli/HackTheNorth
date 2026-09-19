# Realistic hackathon tracks

Evidence register based on the supplied 2026 rules, not a guarantee of eligibility or prizes.

| Track | Position | Remaining work |
| --- | --- | --- |
| Overall / Warp | Working learning developer tool; no extra API required | Strong demo and honest limitations |
| Beginner | No integration required | Every teammate must have attended at most one prior hackathon |
| Sentry | Logs + Tracing enabled locally; live uploads accepted with HTTP 200 | Verify free account plan, dashboard receipt and a real improvement documented from Sentry data |
| Rox | Guided context agent for multi-file/partial Managed Ask AI requests | Broader real-project evidence; two synthetic examples do not establish general reliability or eligibility |

## Sentry setup

Current workspace update: the user supplied a DSN, configuration is enabled locally, and both verification uploads received HTTP 200 without rate limits. See [live evidence](release-review/sentry-live-ingestion.json). Dashboard visibility, account plan and the required real improvement remain unverified. The steps below are retained for reproduction; do not replace an already-configured DSN unnecessarily.

1. Create a Sentry Python/FastAPI project on the **free Developer plan**. Verify that the account is free, not a paid plan or credit-based trial. Stop if asked to pay.
2. Find its **DSN** in project settings. This is the SDK's destination, not your BeProgram token. No Sentry API access token is needed.
3. Add these lines to your local ignored `.env`. Do not replace `LOCAL_DEV_TOKEN`, paste credentials into chat, or include them in screenshots:

   ```dotenv
   SENTRY_ENABLED=true
   SENTRY_DSN=<paste your project DSN locally>
   ```

4. Run `./scripts/run-local.ps1 -Restart`, then:

   ```powershell
   .venv/Scripts/python.exe -m scripts.verify_sentry --send
   ```

5. In Sentry, find the printed `correlation_id` in **Logs** and **Traces**. Expand `managed_ask` to see its nested `local_inference` span. A successful SDK flush does not prove delivery; verify both products in the dashboard.
6. Use a real trace/error to diagnose an actual issue. Record what the data showed, the fix and the measured improvement. This remains unfinished; do not claim earlier fixes were discovered through a Sentry dashboard.

Disable with `SENTRY_ENABLED=false` and restart. A DSN alone never opts in. Core learning still works without Sentry; no paid fallback or billing automation exists.

**Data disclosure:** only manually instrumented operation names, durations, outcomes and opaque correlation/trace IDs are sent. Source, prompts, answers, filenames, hostname, user identity and tokens are excluded. Automatic HTTP/SQL/AI-prompt instrumentation, breadcrumbs, replay and profiling are disabled. AI runs locally; optional diagnostic metadata leaves the computer only when enabled.

Without an account, run `.venv/Scripts/python.exe -m scripts.verify_sentry` to capture actual SDK envelopes in memory. It uses real local inference on a synthetic helper, never sends to Sentry and is not hosted-service receipt evidence. The implementation fixes previously separate nested transactions so model inference appears inside its parent operation. SDK tests verify that structure; live product-improvement evidence remains open.

References: [Python Logs](https://docs.sentry.io/platforms/python/logs/), [custom tracing](https://docs.sentry.io/platforms/python/tracing/instrumentation/custom-instrumentation/), [free plan](https://www.sentry.help/en/articles/16738709-changes-to-legacy-developer-plans-september-2026).

## Rox demonstration

The local model chooses an `inspect_module` tool for an approved entry file. The tool follows simple relative imports inside that same saved snapshot, reading at most three excerpts. Missing or ambiguous dependencies produce a context request; otherwise the model answers from the selected excerpts. Replies identify the excerpts read. Unrelated source is omitted from the final answer context.

This is a **guided tool workflow**, not unrestricted repository exploration or a multi-agent system. The application controls dependency traversal and limits. It cannot read unapproved files, execute code, publish, modify files or grant a checkpoint pass. Existing scope, gate, retry binding and retention checks remain. Unchanged dependencies never included in a capture are unavailable. Complex syntax, external packages, dynamic imports and truncated snapshots remain limitations; the import heuristic is not a full language parser.

Run `.venv/Scripts/python.exe -m scripts.verify_context_agent`. Reports retain synthetic source, actual tool choices and responses. In the completed check, the tool followed `src/main.js` to `src/limit.js`, used the actual value 5 despite an old comment mentioning 100, and answered `full(5)` as true. Removing the approved dependency caused an explicit missing-context response; an unrelated colors file was unused.

Earlier looping designs repeated files or incorrectly requested context. Their reports are preserved as `docs/release-review/context-agent-*.json`. The bounded tool replaces that design. Two successful development examples are not independent validation. Demonstrate permitted real-project changes before claiming broad Rox readiness.
