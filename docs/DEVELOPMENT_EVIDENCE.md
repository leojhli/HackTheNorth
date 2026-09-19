> Current free local edition: OpenAI inference has been replaced with local Ollama/Qwen2.5-Coder. See VERIFICATION.md and the actual-model JSON reports for new runtime evidence. Historical sponsor and hosted-provider notes below are not current track claims. Codex's development assistance is separate from the models used by the product.

# Development evidence (not sponsor submission proof)

| Task | Coding-assistant contribution | Artifact/check | Human verification |
| --- | --- | --- | --- |
| Inspect actual sources and plan | Retrieved Figma Make source inventory, diagnosed unreadable resource links, imported user ZIP; identified timers/keyword evaluation/seeded history | IMPLEMENTATION_PLAN.md, imported React source | Pending owner review |
| Durable learning loop | Implemented typed provider adapter, immutable snapshots, versioned attempts, owner checks, managed AI gate and recovery tests | backend/service.py, tests/test_core.py | Pending live model review |
| Fix observed telemetry failure | Initial tests exposed an AttributeError in Sentry logging that masked persisted successful requests; explicit logger import and fail-open emission corrected it | backend/observability.py; API tests changed from failures to passes | Pending live Sentry organization check |
| Fix oversized-diff suppression | Review found oversized single hunks were entirely skipped; bounded prefix and full-change hash now retain partial coverage | backend/context.py, regression test | Pending repository pilot |
| Replace prototype actions | Retained Figma panel/tokens/icons, wired real backend state, removed production simulation entry point | LiveApp.tsx, LiveWebsite.tsx, Voice.tsx, Optional.tsx | Pending user review |
| Harden external writes | Implemented wallet challenge replay protection, durable signed transaction reconciliation, exact PR preview consent and uncertain-write reconciliation | receipt and GitHub tests with explicit doubles | No live external write performed |
| Protect frozen assessment | Review found re-upload after an evaluation outage could replace its question; return existing checkpoint and use explicit retries | Regression asserts unchanged question/version and one question-provider call | Automated check passed; human review pending |
| Verify exported design in browser | Fixed explanation accessible name and mobile metadata wrapping, inspected desktop/mobile/light renders, exercised reload and managed gate | 2 Playwright scenarios and docs/screenshots | Agent visual review complete; owner review pending |
| Correct primary extension experience | Reused Figma checkpoint UI in a VS Code sidebar; host-only API/token bridge; captured, answered and passed without opening a browser | Packaged VSIX, 7 extension unit tests, 6 actual host check groups, sidebar browser scenario | Automated host and visual checks complete; live user/OpenAI pilot pending |
| Fix Windows capture boundary | Actual extension host rejected a valid source path because drive-letter case differed; canonical/relative containment fixes it | capture.cjs, Windows boundary regression and successful host rerun | Automated actual-host confirmation |

The OpenAI API adapter is separate from Codex's development assistance. No live provider call, human assessment agreement score, end-to-end latency benchmark, prize eligibility, or submission has been claimed without evidence.
