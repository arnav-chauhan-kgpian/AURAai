# AuraAI — Judging Highlights

A one-page cheat sheet mapping AuraAI to common hackathon judging criteria.

## The 30-second pitch

AuraAI is an **autonomous AI stylist**. Ask it anything about your skin or style and a
LangGraph agent decides which tools to run — skin analysis, color, recommendations,
virtual try-on — streams its plan live, and returns one grounded, personalised reply
plus a signature **Aura Score**. It never dead-ends: if an API fails, it falls back to
demo assets automatically.

## Why it wins

| Criterion | How AuraAI delivers |
| --- | --- |
| **Innovation** | Not an API wrapper — a true agent that *plans multi-step tool use*. The user never picks an API. |
| **Technical depth** | LangGraph state graph, Gemini structured output + streaming, async YouCam orchestration with retry/backoff/polling, two-tier memory (Redis + Supabase), 30 backend tests. |
| **Design / UX** | Apple-grade frontend: streaming timeline, animated gauges, before/after try-on, dark mode, page transitions, ripple, reduced-motion, premium empty &amp; error states. |
| **Completeness** | Landing, chat, dashboard, settings, onboarding, error &amp; empty states, Docker, README, docs — all shipped and building. |
| **Demo readiness** | Demo Mode + 3 personas + automatic fallback = a demo that *cannot* break on stage. |
| **"Wow"** | The **Aura Score** — one memorable, shareable confidence number synthesised from every signal. |

## Signature moments to show

1. **Agent autonomy** — one prompt triggers Skin → Color → Recommendation → Try-On, with the intent shown as a pill. The user chose nothing.
2. **Live timeline** — the agent's plan streams step-by-step in the center panel.
3. **Aura Score** — a gradient radial hero number with a skin/color/style breakdown.
4. **Before/after try-on** — draggable slider + fullscreen zoom + download.
5. **Never breaks** — kill the backend mid-demo; it keeps going on demo assets.

## By the numbers

- **4** agent tools, **6** intents, **1** data-driven routing table (extensible without graph edits).
- **30** backend unit tests passing (planner routing, tool execution, memory, full graph, YouCam client).
- **5** frontend routes, **~45** components, **0** build errors.
- **3** demo personas covering acne/oily/warm, dry/neutral, sensitive/cool.

## Architecture in one line

`Next.js 15 ⇄ FastAPI + LangGraph ⇄ {YouCam, Gemini 2.5 Flash, Supabase, Redis}` — Dockerised.
