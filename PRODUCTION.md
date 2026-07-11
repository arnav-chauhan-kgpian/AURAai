# Production Readiness

This document tracks what was hardened for production and the operator steps
required to go live. Hardening is code-complete and verified (backend imports +
30 tests green; frontend build green). What remains is **provisioning** external
services and flipping the switches.

## What was implemented

| Phase | Area | Status |
| --- | --- | --- |
| 1 | **Authentication** (Clerk): sign-up/in/out, JWT verification (JWKS/RS256), protected endpoints, session middleware, user profile, refresh + secure cookies (Clerk-managed), RBAC groundwork | ✅ code-complete |
| 2 | **Authorization**: every request carries `user_id` + `org_id` + server-owned `session_id`; ownership validated; no client-generated ids | ✅ |
| 3 | **Database**: Supabase migrations for `users, profiles, sessions, conversations, skin_scans, try_on_jobs, recommendations, audit_logs` — RLS, FKs, indexes, soft delete, timestamps | ✅ |
| 4 | **Storage**: Supabase Storage object store, signed URLs, expiry, retention purge | ✅ |
| 5 | **Privacy**: consent, image deletion, GDPR account erasure, retention policy | ✅ |
| 6 | **Security**: rate limiting, upload validation (size/type/magic bytes), virus-scan hook, security headers, CSRF stance, input sanitization, secrets validation | ✅ |
| 7 | **Observability**: Sentry, OpenTelemetry tracing, Prometheus metrics, structured logs, correlation ids | ✅ (guarded, opt-in) |
| 8 | **Deployment**: Railway config, Docker health/readiness checks, graceful shutdown | ✅ |
| 9 | **CI/CD**: GitHub Actions — lint, typecheck, backend + frontend tests, Docker build | ✅ |
| 10 | **Docs**: this file + SECURITY / DEPLOYMENT / DATA_MODEL / MIGRATIONS | ✅ |

Backward compatibility is preserved: with `AUTH_REQUIRED=false` and no Clerk keys,
the app runs anonymously / in Demo Mode exactly as before. Production switches
harden it without code changes.

## Go-live checklist

1. **Provision services**
   - Clerk application → copy `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `CLERK_ISSUER`; set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`.
   - Supabase project → `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`; create the `aura-uploads` bucket (or run `0002_storage.sql`).
   - Redis instance → `REDIS_URL`.
   - Gemini + YouCam keys.
2. **Apply migrations** — see [`MIGRATIONS.md`](MIGRATIONS.md).
3. **Set production env** (see [`.env.example`](.env.example)):
   - `ENVIRONMENT=production`, `AUTH_REQUIRED=true`, `HSTS_ENABLED=true`, `CONSENT_REQUIRED=true`.
   - `CORS_ORIGINS` = your real origins (no wildcards — startup will reject them).
   - `CLERK_AUTHORIZED_PARTIES` = your frontend origins.
   - Optionally `SENTRY_DSN`, `OTEL_EXPORTER_OTLP_ENDPOINT`.
4. **Deploy** — see [`DEPLOYMENT.md`](DEPLOYMENT.md). `validate_secrets()` fails fast if anything critical is missing.
5. **Verify** — `GET /api/v1/health` (liveness) and `GET /api/v1/ready` (readiness) return 200; sign in; run a chat turn; test `DELETE /api/v1/privacy/account`.

## Known follow-ups (not blockers)

- **Verify live YouCam I/O**: skin/VTO result parsers are tolerant and validated against docs, not a live account — confirm against real responses.
- **Wire the retention purge to a scheduler** (cron / Railway job calling `ObjectStore.purge_expired`).
- **ClamAV**: `VIRUS_SCAN_ENABLED=true` requires a reachable `clamd` and the `clamd` Python package.
- **Frontend tests / E2E** are not yet present (CI runs lint + typecheck + build).
- **Optionally wire Clerk as a Supabase third-party JWT** to move RLS from default-deny to per-row policies (examples are in the migration).
