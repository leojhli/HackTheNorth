# Deployment preparation

One API process serves the built React UI and all private routes. Use one PostgreSQL database (Supabase Postgres works) and Supabase Auth. SQLite/local token mode is for loopback development; startup rejects either in production.

1. Provision PostgreSQL and a Supabase Auth project; enable asymmetric JWT signing and create/invite pilot users. Set your app URL and auth redirect URLs. No registration flow is supplied in this prototype.
2. Create a server `.env` from `.env.example`. Set `ENVIRONMENT=production`, `AUTH_MODE=supabase`, `DATABASE_URL` using the psycopg dialect, `SUPABASE_URL`, publishable key, exact HTTPS `APP_ORIGIN` and comma-separated `ALLOWED_ORIGINS`. Put private keys in the host secret manager. Never use frontend `VITE_` variables for private keys.
3. Build and initialize:

```sh
docker build -t beprogram .
docker run --rm --env-file .env beprogram python -m backend.migrate
docker compose -f compose.production.yml up -d
```

4. Put an HTTPS reverse proxy in front of 127.0.0.1:8000. Enforce a 12 MB request limit, upstream timeout greater than 40 seconds, and request rate limits (especially public `/v1/verify`). Keep API port private; only the proxy exposes the application. Allow microphone on the app's HTTPS origin. Proxy request/access logs must not include auth headers, bodies, or query credentials. The supplied container disables access logs and forwarded-header trust.
5. Verify `/health`, authenticated owner isolation, actual OpenAI checkpoint/follow-up/pass, restart recovery, and one end-to-end managed request. Test the exact configured PostgreSQL deployment under concurrent requests; local SQLite tests are not PostgreSQL concurrency certification.
6. Schedule `python -m backend.retention` daily using a job with the same database settings. It removes source context after 30 days and removes expired private receipt packages as a whole, preserving commitments rather than silently changing them. Evidence metadata/answers remain until project deletion. Deleting a project cascades its private records. Exported/on-chain/remote artifacts remain separate.

Database migration v1 creates a private `beprogram` schema and revokes public/anon/authenticated schema access when those roles exist. Keep this schema out of Supabase exposed schemas. Run migrations with a schema owner; run the API with a dedicated role granted only usage and required table CRUD. Do not use a browser service-role key. Future schema changes require explicit migrations; `create_all` does not upgrade existing columns.

Back up PostgreSQL with encrypted backups and rehearse restoration. Define a retention policy for backups and exported evidence. Rotate OpenAI/ElevenLabs/Composio keys and Devnet issuer keys through the secret manager; old receipt verification needs the historical trusted public issuer list. Issuer rotation does not rewrite an existing preview. Monitor health, typed error rates, provider latency, database disk and retention failures.

Optional activation gates:

- Sentry: inspect actual emitted envelopes, then verify correlated errors/traces/logs in your organization. A local memory-transport redaction test is not a delivered Sentry event.
- Solana: fund a dedicated Devnet issuer with test SOL; never use a mainnet wallet. Set an independently chosen trusted issuer list for the verifier. Verify genesis hash/network, real issuance, tamper/issuer/replay failures and timeout reconciliation before enabling for users. No automatic replacement of expired transactions and no revocation system.
- ElevenLabs: verify voice ID/model access, microphone permission denial, actual playback/transcription and edited text submission. Server bounds audio bytes; the 90-second recording limit is enforced by the browser.
- Composio: create GitHub auth configuration with only the permissions your selected repositories require. Connect from BeProgram so the Composio user ID matches the verified app identity. The runtime uses the documented v3.1 auth-link/account/proxy API and validates the connection before every operation. Validate these exact schemas against your connection before enablement. Test approved comments only on an authorized demo PR. No connection or external write was performed by building this repository.

No host, domain, TLS certificate, provider account, wallet funding, CI secret, or public release has been created. The Docker/compose assets are prepared but require a Docker-capable deployment environment to execute and verify.
