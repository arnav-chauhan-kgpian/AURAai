# AuraAI — Feature List

## Autonomous agent (backend)
- LangGraph state graph: `detect_intent → route → execute_tools → summarize → persist_memory`.
- Intent classification via Gemini structured output (+ deterministic keyword fallback).
- 6 intents: `SKIN_ONLY`, `TRYON_ONLY`, `STYLE_ONLY`, `SKIN_AND_STYLE`, `CHAT_ONLY`, `UNKNOWN`.
- Data-driven tool routing (`ToolRegistry`) — extensible without touching the graph.
- 5 tools on one interface: Skin Analysis, Virtual Try-On, Color Palette, Recommendation, Conversation Memory.
- Two-tier memory: Redis (session history + snapshot) + Supabase (durable profile).
- Token streaming to the client over SSE.

## YouCam integration (backend)
- Full async workflow: auth → File API upload → task create → poll → parse.
- Skin Analysis + Apparel Virtual Try-On.
- Connection pooling, exponential backoff with jitter, retry on 429/5xx, rate limiting.
- Typed error mapping: no-face, multiple-faces, invalid-image, rate-limit, expired-task, server-error.
- Robust polling with configurable interval + timeout; structured logs (request id, task id, latency, retries).

## Frontend experience
- **Routes:** Landing `/`, Chat `/chat`, Dashboard `/dashboard`, Settings `/settings` (+ error, not-found, loading, route transitions).
- **Landing:** animated mesh gradient hero, headline, CTA, feature cards, closing CTA.
- **Dashboard:** three-pane (Conversation · Timeline · Results), responsive to a segmented control on mobile.
- **Chat:** streaming markdown replies, code blocks, images, typing indicator, auto-scroll, selfie + garment upload.
- **Timeline:** live phases (upload → planning → skin → tone → recommendations → try-on → done) animating in.
- **Skin results:** animated radial gauges, concern badges, overlay heatmap toggle, animated numbers.
- **Color palette:** season, warm/cool undertone, swatches, copy palette.
- **Virtual try-on:** before/after slider, fullscreen modal, zoom, download.
- **Recommendations:** tabbed skincare / fashion / colors / shopping.

## Signature feature
- **Aura Score** — a 0–100 confidence metric blending skin health, color harmony, and style match, shown as a gradient radial with a per-dimension breakdown. Computed client-side → instant and always available.

## Demo readiness
- **Demo Mode** — runtime toggle (Settings) + `NEXT_PUBLIC_USE_MOCK` env var.
- **Automatic fallback** — any YouCam/stream failure switches to demo assets transparently.
- **3 personas** — Maya (acne · oily · warm · casual), Daniel (dry · neutral · business), Priya (sensitive · cool · evening), all matching the real schema.
- Header **Demo** pill when active.

## Polish
- Page transitions, button ripple, scroll-reveal sections, skeleton loaders (no spinners), image fade-in.
- `prefers-reduced-motion` honored globally.
- Premium empty states (no selfie / garment / recommendations / history / internet / API).
- Beautiful error states with recovery actions (no face / multiple faces / upload / rate-limited / server).
- First-launch onboarding walkthrough (3 screens, skip, persisted).
- Dark mode by default, theme-aware, persisted.

## Accessibility
- ARIA roles (switch, slider, dialog, tablist/tab/tabpanel, alert), labels on all icon buttons.
- Full keyboard operation: Enter-to-send, arrow-key sliders, Escape-to-close, visible focus rings.
- Theme-aware contrast in both light and dark.

## Engineering
- 30 backend unit tests (mocked Gemini + YouCam) green.
- Frontend production build green, 5 static routes.
- Dockerfiles + docker-compose for the full stack.
- Clean architecture, typed end-to-end, no business logic in endpoints.
