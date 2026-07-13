# Railway Deploy Runbook (turnkey)

Everything below is ready. The only step that requires **you** is `railway login`
(interactive browser auth). After that, the rest can run start-to-finish.

## 0. One-time auth (you)

```bash
railway login              # opens a browser; authenticates this machine
railway whoami             # confirm
```

## 1. Create the project + two services

```bash
railway init                       # create/select a project
railway add --service backend      # backend service
railway add --service frontend     # frontend service
```

In the **frontend** service Settings → *Config-as-code*, set the file path to
`railway.frontend.json` (the backend uses the default `railway.json`).

## 2. Backend env vars (service: backend)

Values live in `backend/.env` (git-ignored). Set them on Railway:

```bash
railway variables --service backend \
  --set ENVIRONMENT=production \
  --set DEBUG=false \
  --set AUTH_REQUIRED=true \
  --set HSTS_ENABLED=true \
  --set LLM_PROVIDER=groq \
  --set GROQ_API_KEY=... \
  --set YOUCAM_API_KEY=... \
  --set YOUCAM_SECRET_KEY=... \
  --set SUPABASE_URL=... \
  --set SUPABASE_SERVICE_ROLE_KEY=... \
  --set SUPABASE_STORAGE_BUCKET=aura-uploads \
  --set REDIS_URL=rediss://... \
  --set CLERK_ISSUER=https://<slug>.clerk.accounts.dev \
  --set 'CLERK_AUTHORIZED_PARTIES=["https://<frontend-domain>"]' \
  --set 'CORS_ORIGINS=["https://<frontend-domain>"]'
```

> `CORS_ORIGINS` and `CLERK_AUTHORIZED_PARTIES` need the **frontend** public URL,
> which you only get after the frontend deploys — set placeholders, then update
> (step 5).

## 3. Frontend env vars (service: frontend)

`NEXT_PUBLIC_*` are consumed at **build** time (Next inlines them); the Dockerfile
declares matching `ARG`s so Railway passes them through automatically.

```bash
railway variables --service frontend \
  --set NEXT_PUBLIC_API_BASE_URL=https://<backend-domain> \
  --set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_... \
  --set CLERK_SECRET_KEY=sk_... \
  --set NEXT_PUBLIC_USE_MOCK=false
```

## 4. Deploy

```bash
railway up --service backend
railway up --service frontend -c railway.frontend.json
railway domain --service backend      # generate/print public URL
railway domain --service frontend
```

## 5. Wire the two together, then redeploy the frontend

- Set backend `CORS_ORIGINS` / `CLERK_AUTHORIZED_PARTIES` to the frontend URL.
- Set frontend `NEXT_PUBLIC_API_BASE_URL` to the backend URL.
- `railway up --service frontend -c railway.frontend.json` (rebuild bakes the URL).

## 6. Verify

```bash
curl -s https://<backend-domain>/health   # {"status":"ok"}
curl -s https://<backend-domain>/ready     # {"status":"ready","checks":{...}}
open  https://<frontend-domain>/           # landing page
```

## Data stores (already external, free tier)

- **Redis** → Upstash (`REDIS_URL=rediss://…`). No Railway service needed.
- **Postgres + Storage** → Supabase. Migrations already applied (see MIGRATIONS.md).
