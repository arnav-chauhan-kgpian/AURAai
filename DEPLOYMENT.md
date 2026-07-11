# Deployment

Two services: **backend** (FastAPI) and **frontend** (Next.js). Both ship as
optimized, non-root Docker images with health checks.

## Prerequisites

- Provisioned: Clerk, Supabase (DB + Storage), Redis, Gemini, YouCam.
- Migrations applied — see [`MIGRATIONS.md`](MIGRATIONS.md).
- Environment configured from [`.env.example`](.env.example).

## Railway (recommended)

The repo includes [`railway.json`](railway.json) for the backend service
(Dockerfile build, health check at `/api/v1/health`, restart-on-failure).

1. **Backend service** → deploy from `docker/Dockerfile.backend`. Set all backend
   env vars. Railway injects `$PORT`; the start command honors it.
2. **Frontend service** → deploy from `docker/Dockerfile.frontend`. Set
   `NEXT_PUBLIC_*` vars (API base URL, Clerk publishable key).
3. **Redis** → add the Railway Redis plugin; set `REDIS_URL`.
4. Point the frontend's `NEXT_PUBLIC_API_BASE_URL` at the backend service URL and
   add that origin to `CORS_ORIGINS` and `CLERK_AUTHORIZED_PARTIES`.

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
