# Operating the free local edition

The supported zero-subscription delivery runs on your own computer: one FastAPI process serves the built website, SQLite persists history, and a separate local Ollama process performs inference. No hosting account, domain, Supabase account or model credits are required. VS Code connects over loopback.

## Daily use

1. Run `./scripts/run-local.ps1` from the repository. This starts the dedicated Ollama server on 127.0.0.1:11435 with `OLLAMA_NO_CLOUD=1`, then the app on 127.0.0.1:8000.
2. Use the local VSIX/sidebar or dashboard. Keep `LOCAL_DEV_TOKEN` in `.env` private; the token authenticates local requests and is not a provider API key.
3. Stop the backend with Ctrl+C. Use `./scripts/stop-local-ai.ps1` to stop the isolated model server and release GPU memory.
4. Back up `beprogram.db` while the app is stopped, or use SQLite's online backup API. Do not copy only the DB while ignoring an active WAL. Protect backups because they contain approved source and explanations.
5. Schedule `python -m backend.retention` locally if using the documented 30-day source-context expiry. It is not automatically scheduled. Project deletion removes its local records; it cannot remove exported files or optional public receipts.

Model weights/runtime are in `%LOCALAPPDATA%/CodeProof/ollama`. The model download needs internet; core inference and persistence work locally afterward. Optional Devnet verification and package installation still require internet. Ollama startup logs are in that runtime directory; do not enable source-payload debug logging.

Local auth checks that the caller is loopback. Keep both service ports private: do not expose this token-based development setup through a tunnel or public reverse proxy. The existing production checks still require proper JWT authentication and PostgreSQL. This change does not weaken those checks to pretend local auth is a multiuser deployment.

## Optional hosted deployment

Existing Docker/compose/Supabase/PostgreSQL assets are historical preparation, not a turnkey free deployment. A hosted server would also need actual local-model compute in the same network namespace as the backend's loopback-only Ollama endpoint. No free GPU host or subscription-free public availability is promised. Use the local demo for this budget.

Before any future hosted release, explicitly design authentication, persistent storage/backups, local model placement, TLS, request limits, resource capacity and costs; validate Docker and PostgreSQL concurrency. Do not turn on paid hosted providers as an automatic fallback. Nothing has been published or deployed externally.

## References

- Ollama local-only configuration: https://docs.ollama.com/faq
- Native JSON-schema outputs: https://docs.ollama.com/capabilities/structured-outputs
- Model/download size and license information: https://ollama.com/library/qwen2.5-coder:7b

These confirm runtime capabilities, not the accuracy of CodeProof's assessments. Independent review of model correctness remains incomplete.
