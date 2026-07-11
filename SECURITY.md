# Security

## Authentication

- **Provider:** Clerk. The frontend uses `@clerk/nextjs`; `middleware.ts` protects
  `/chat`, `/dashboard`, `/settings`. Clerk manages **refresh tokens and secure,
  rotating session cookies**.
- **Backend verification:** short-lived Clerk JWTs are verified with RS256 against
  Clerk's JWKS (`app/auth/clerk.py`) — signature, `iss`, `exp`, and authorized
  party (`azp`) are all checked. Signing keys are cached.
- **Token transport:** the frontend attaches `Authorization: Bearer <token>`; the
  backend also accepts Clerk's `__session` cookie for same-site requests.
- **Dev/demo:** when `AUTH_REQUIRED=false` and no Clerk keys are set, requests fall
  back to an anonymous context. **Production must set `AUTH_REQUIRED=true`** —
  `validate_secrets()` enforces this at startup.

## Authorization

- Every protected request resolves a `RequestContext` = `user_id` + `org_id` +
  **server-owned** `session_id` + `correlation_id` (`app/auth/dependencies.py`).
- **No client-generated ids**: a presented `X-Session-Id` is accepted only after
  `SessionService` confirms it belongs to the caller; otherwise a fresh id is
  minted server-side.
- **RBAC groundwork** (`app/auth/roles.py`): `USER < ADMIN < OWNER`, sourced from
  Clerk org claims; `require_role(...)` gates privileged routes.

## Data protection & privacy

- Face images are **biometric data**. Consent is required before processing
  (`CONSENT_REQUIRED=true`); the chat endpoint refuses to analyse a face image
  without recorded consent.
- **Deletion:** `DELETE /api/v1/privacy/images` (images) and
  `DELETE /api/v1/privacy/account` (full GDPR erasure across all tables + storage).
- **Retention:** stored images are swept after `IMAGE_RETENTION_DAYS`
  (`ObjectStore.purge_expired`).
- **RLS:** all tables have Row Level Security enabled with a default-deny posture;
  the backend uses the service-role key (which bypasses RLS), so a leaked anon key
  grants no data access.

## Request security

- **Rate limiting** (`app/security/rate_limit.py`): Redis fixed-window per user
  (IP fallback), `RATE_LIMIT_PER_MINUTE`. Fails open on a Redis outage; returns
  `429` + `Retry-After` when exceeded.
- **Upload validation** (`app/security/uploads.py`): max size, MIME allow-list, and
  **magic-byte verification** (defeats `Content-Type` spoofing). Optional ClamAV
  scan **fails closed** when required.
- **Input sanitization** (`app/security/sanitize.py`): control-char stripping,
  Unicode normalisation, length bounds on the chat message.
- **Security headers** (`app/security/headers.py`, Helmet-equivalent):
  `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  `Permissions-Policy`, a locked-down `Content-Security-Policy`, COOP/CORP, and
  HSTS (opt-in behind HTTPS).
- **CSRF:** the API authenticates via bearer tokens (not ambient cookies) and CORS
  is restricted to known origins with an explicit method/header allow-list, so
  cross-site form posts cannot be authenticated. Clerk cookies are `SameSite` and
  same-site only.
- **Secrets validation** (`app/security/secrets.py`): startup fails fast in
  production if auth is off, Clerk/YouCam/Gemini/Supabase creds are missing, or
  CORS contains wildcards.

## Reporting a vulnerability

Email `security@aura-ai.dev` with details and reproduction steps. Please do not
open public issues for security reports.
