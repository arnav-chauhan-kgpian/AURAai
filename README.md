<div align="center">

# ✦ AuraAI

### Your Personal AI Skin &amp; Style Agent

**An autonomous AI stylist that analyses your skin, renders virtual try-ons, and plans personalised skincare &amp; outfits — the agent decides which tools to run, you never pick an API.**

`Next.js 15` · `FastAPI` · `LangGraph` · `Groq (Llama 3.3 70B)` · `YouCam` · `Supabase` · `Redis` · `Docker`

</div>

---

## 🚀 Live Demo

> **[✦ Open AuraAI →](https://frontend-production-cae3a.up.railway.app/)**

| | URL |
| --- | --- |
| **App (frontend)** | https://frontend-production-cae3a.up.railway.app/ |
| **API (backend)** | https://auraai-production-1419.up.railway.app/ |
| **API health** | https://auraai-production-1419.up.railway.app/health |
| **API readiness** | https://auraai-production-1419.up.railway.app/ready |

Deployed on **Railway** as two services (FastAPI backend + Next.js frontend) with
Supabase (Postgres + Storage) and Upstash Redis as managed data stores. Sign in to
run the full agent (skin analysis, recommendations, virtual try-on), or explore the
landing experience anonymously.

---

## Overview

AuraAI is **not an API wrapper**. It is an autonomous agent that plans and executes a
multi-step workflow for every request:

```
"I have acne, what should I wear? Can I try this jacket?"
        │
        ▼  the agent classifies intent → SKIN_AND_STYLE
Skin Analysis ─▶ Color Palette ─▶ Recommendations ─▶ Virtual Try-On ─▶ Reply
```

The user never names a tool. A **LangGraph** agent detects intent, routes to the
right capabilities, streams its plan live, and synthesises one warm, grounded reply.

| | |
| --- | --- |
| 🔬 **Skin AI** | Dermatologist-grade concern scoring from one selfie (YouCam Skin Analysis) |
| 👕 **Virtual Try-On** | Realistic garment rendering (YouCam Apparel Try-On) |
| 🎨 **AI Stylist** | Palette + skincare + outfit + shopping, reasoned by Groq (Llama 3.3 70B) |
| ✦ **Aura Score** | A signature 0–100 confidence score blending skin, color &amp; style |
| ⚡ **Demo Mode** | Full experience offline — three curated personas, zero API keys |

---

## Architecture

```
                         ┌──────────────────────── Next.js 15 frontend ─────────────────────────┐
                         │  Landing · Chat · Dashboard (Conversation │ Timeline │ Results) · …   │
                         │  Zustand · React Query · Framer Motion · streaming SSE hook           │
                         └───────────────────────────────┬──────────────────────────────────────┘
                                                         │  POST /chat/stream (SSE) · REST
                                                         ▼
┌──────────────────────────────────────── FastAPI backend ─────────────────────────────────────────┐
│  api ─▶ AuraAgent.run() ── compiled LangGraph ───────────────────────────────────────────────     │
│            detect_intent → (route) → execute_tools → summarize → persist_memory                    │
│            Planner (Groq structured) · ToolRegistry · Summarizer · ConversationMemory              │
│  tools: SkinAnalysisTool · VirtualTryOnTool · ColorPaletteTool · RecommendationTool · Memory       │
└───────┬──────────────────────────┬───────────────────────────┬────────────────────┬───────────────┘
        ▼                          ▼                           ▼                    ▼
  YouCam Skin/VTO            Groq Llama 3.3/3.1           Supabase              Redis
  (async task API)          (reason + stream)          (profile store)     (session memory)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/AGENT.md`](docs/AGENT.md) for detail.

---

## Tech stack

**Frontend** — Next.js 15 (App Router) · TypeScript · TailwindCSS · shadcn-style UI ·
Framer Motion · React Query · Zustand · Lucide · react-markdown

**Backend** — FastAPI · Python 3.12 · Poetry · LangGraph · LangChain · Groq (Llama 3.3 70B
+ 3.1 8B; Gemini also supported) · httpx (async, pooled) · Pydantic · structlog

**Infra** — Supabase (Postgres + Storage) · Redis · Docker + Docker Compose

---

## Features

- **Autonomous agent** — intent routing (`SKIN_ONLY`, `TRYON_ONLY`, `STYLE_ONLY`, `SKIN_AND_STYLE`, `CHAT_ONLY`) with data-driven tool selection.
- **Live streaming** — the agent's plan streams to a timeline; the reply streams token-by-token.
- **Skin results** — animated radial gauges, concern badges, overlay heatmap toggle.
- **Color palette** — seasonal analysis, warm/cool undertone, copyable swatches.
- **Virtual try-on** — before/after slider, fullscreen zoom, download.
- **Recommendations** — tabbed skincare / fashion / colors / shopping.
- **Aura Score** — a memorable confidence hero metric, computed client-side.
- **Demo Mode** — runtime toggle + env var + automatic fallback on API failure, with 3 personas.
- **Onboarding** — first-launch 3-screen walkthrough (skip + persisted).
- **Premium polish** — page transitions, button ripple, scroll reveals, skeletons (never spinners), reduced-motion support, beautiful empty &amp; error states, dark mode by default.

---

## Installation

**Prerequisites:** Node 20+, Python 3.12 + Poetry, Docker, and (optional) YouCam / Gemini / Supabase keys.

```bash
git clone <repo-url> aura-ai
cd aura-ai
cp .env.example .env        # fill in keys — or skip and use Demo Mode

make install                # backend (poetry) + frontend (npm)
make up                     # full stack via docker compose
```

Individual services:

```bash
make backend     # uvicorn app.main:app --reload   → http://localhost:8000
make frontend    # next dev                          → http://localhost:3000
```

> **No keys? No problem.** Launch the frontend and flip **Settings → Demo Mode** (or set
> `NEXT_PUBLIC_USE_MOCK=true`). If the YouCam pipeline ever fails or times out, AuraAI
> **automatically** serves demo assets so a live demo never dead-ends.

---

## Deployment

Live on **Railway** as two Dockerized services (see the [Live Demo](#-live-demo) above).
Config-as-code ships in the repo:

- [`railway.json`](railway.json) — backend service (`docker/Dockerfile.backend`, health at `/health`).
- [`railway.frontend.json`](railway.frontend.json) — frontend service (`docker/Dockerfile.frontend`).
- Step-by-step: [`RAILWAY_DEPLOY.md`](RAILWAY_DEPLOY.md) (dashboard + CLI) and [`DEPLOYMENT.md`](DEPLOYMENT.md).

Production hardening is verified live: HTTPS + HSTS, security headers, CORS locked to the
frontend origin, per-user rate limiting, auth enforcement (Clerk JWT via JWKS), interactive
docs disabled, gated `/metrics`, and `/health` + `/ready` probes.

---

## Environment variables

| Variable | Description |
| --- | --- |
| `ENVIRONMENT` / `DEBUG` | Runtime mode and verbose logging |
| `YOUCAM_API_KEY` / `YOUCAM_SECRET_KEY` | YouCam (Perfect Corp) credentials (secret = RSA public key) |
| `YOUCAM_BASE_URL` | YouCam API host |
| `GROQ_API_KEY` / `GROQ_MODEL` | Groq LLM (default `llama-3.3-70b-versatile`) — primary provider |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | Google Gemini (alternative provider; `LLM_PROVIDER=auto` prefers Groq) |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | Supabase project |
| `REDIS_URL` | Redis connection |
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL exposed to the frontend |
| `NEXT_PUBLIC_USE_MOCK` | `true` to start the frontend in Demo Mode |

Full list in [`.env.example`](.env.example).

---

## Project structure

```
aura-ai/
├── frontend/                 # Next.js 15 · TS · Tailwind · Framer Motion
│   ├── app/                  # routes: / · /chat · /dashboard · /settings (+ template, error, not-found)
│   ├── components/           # ui · layout · landing · chat · timeline · skin · vto · results · common · onboarding
│   ├── hooks/                # use-chat-stream (SSE) · use-copy · …
│   ├── lib/                  # api · api-client · store · demo-users · demo-store · aura-score · theme
│   └── types/                # api contract (snake_case, matches backend)
├── backend/                  # FastAPI · Python 3.12 · Poetry
│   └── app/                  # api · agents · tools · services · workflows · schemas · db · prompts · …
├── docker/                   # backend & frontend Dockerfiles
├── docs/                     # ARCHITECTURE.md · AGENT.md · API.md
├── submission/               # architecture · workflow · demo-script · judging-highlights · screenshots
├── docker-compose.yml · .env.example · Makefile · README.md
```

---

## Agent workflow

```
START → detect_intent → (conditional route) → execute_tools → summarize → persist_memory → END
             │                                      │
     Planner (Groq,                 tools run in intent order, threading state:
     structured output)             skin_analysis → color_palette → recommendation → virtual_try_on
```

- **Intent → tools** is a data table in `ToolRegistry` — add a capability without touching the graph.
- Tools that lack inputs (e.g. no garment image) **skip cleanly** rather than failing the turn.
- Per-session history + profile persist to Redis (short-term) and Supabase (long-term).

---

## Screenshots

Rendered from the shipped build (landing + dashboard):
**[▶ View interactive screens](https://claude.ai/code/artifact/ed784541-7dda-4ba5-965c-0fde2f5b7456)**

See [`submission/screenshots/`](submission/screenshots/) for capture instructions.

## Demo GIF

A 15-second capture of a full turn (selfie → streaming timeline → Aura Score → try-on) lives at
`submission/screenshots/demo.gif`. Record with the [3-minute demo script](submission/demo-script.md).

---

## Future roadmap

**Shipped since v1:** per-user history + skin-progress-over-time journal · real
per-tool SSE progress · biometric-consent flow · real skin heatmaps · Clerk auth ·
per-user quotas + retention sweeper.

**Next:**
- Long-term preference memory beyond a session (loved/disliked looks) and voice input.
- Real product catalogue for shoppable, in-stock recommendations.
- OpenTelemetry tracing of agent plans; automated recommendation-quality evals.
- Clerk **production** instance (currently a development instance) and custom domains.

---

## License

MIT © AuraAI. See [`LICENSE`](LICENSE).
