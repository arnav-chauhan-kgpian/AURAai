# Deployment

Two services: **backend** (FastAPI) and **frontend** (Next.js). Both ship as
optimized, non-root Docker images with health checks.

## Prerequisites

- Provisioned: Clerk, Supabase (DB + Storage), Redis, Gemini, YouCam.
- Migrations applied — see [`MIGRATIONS.md`](MIGRATIONS.md).
- Environment configured from [`.env.example`](.env.example).

## Railway (recommended)

**Two services from one repo**, plus external managed data stores (Supabase,
Upstash Redis). Config-as-code lives in two files:

- [`railway.json`](railway.json) — **backend** (default config file). Dockerfile
  build, health check at `/health`, restart-on-failure, honors `$PORT`.
- [`railway.frontend.json`](railway.frontend.json) — **frontend**. Set this as
  the *Config-as-code file path* in the frontend service's Settings.

### Steps

1. `railway login` (one-time, opens a browser).
2. `railway init` → create/select a project.
3. **Backend service** (uses `railway.json`) → set all backend env vars
   (see below). Railway injects `$PORT`.
4. **Frontend service** → in Settings, set *Config file* to
   `railway.frontend.json`. The `NEXT_PUBLIC_*` vars must be present as
   **service variables** so Railway passes them as Docker **build args** (Next.js
   inlines them at build time — runtime-only values would be ignored).
5. **Redis** → use Upstash (set `REDIS_URL=rediss://…`) or add the Railway Redis
   plugin.
6. After the backend gets a public URL, set the frontend's
   `NEXT_PUBLIC_API_BASE_URL` to it, and add the frontend origin to the backend's
   `CORS_ORIGINS` and `CLERK_AUTHORIZED_PARTIES`. Redeploy the frontend so the
   new API URL is baked in.

### Deploy from the CLI (monorepo, per service)

```bash
railway up --service backend            # builds docker/Dockerfile.backend
railway up --service frontend -c railway.frontend.json
```

## Docker Compose (self-hosted)

```bash
cp .env.example .env      # fill in production values
docker compose up --build # backend :8000, frontend :3000, redis :6379
```

## Health & readiness

- `GET /api/v1/health` — **liveness**, never touches dependencies. Used by the
  container `HEALTHCHECK` and the platform.
- `GET /api/v1/ready` — **readiness**, pings Redis and checks the agent is built.
  Returns `503` until dependencies are reachable (in production).

## Graceful shutdown

Uvicorn runs with `--timeout-graceful-shutdown 30`. On `SIGTERM`, in-flight
requests drain and the lifespan handler closes the YouCam and Redis clients
before exit. `--proxy-headers` trusts the platform's `X-Forwarded-*`.

## Image optimization

- Multi-stage builds; only runtime artifacts in the final layer.
- Non-root users (`app` / `nextjs`).
- Backend installs `--only main` (no dev deps); frontend uses `npm ci` from a
  committed lockfile.

## Observability (optional)

- `SENTRY_DSN` → error tracking.
- `OTEL_EXPORTER_OTLP_ENDPOINT` → traces to your OTLP collector.
- `/metrics` → Prometheus scrape endpoint (when `METRICS_ENABLED=true`).

All three are guarded: absent config or libraries simply disables them.

## Retention job

Schedule a periodic call to purge expired images (Railway cron / external
scheduler) hitting an internal task that runs `ObjectStore.purge_expired()`, or
run it from a management shell. Retention window: `IMAGE_RETENTION_DAYS`.
