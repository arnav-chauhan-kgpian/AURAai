# AuraAI — 3-Minute Demo Script

A tight, judge-ready narration. Total runtime **3:00**. Tip: run in **Demo Mode**
(Settings → Demo Mode, persona **Maya**) so nothing depends on the network. Have a
selfie and a garment image ready to attach.

---

### 0:00 – 0:20 · The problem

> "Getting skincare and style advice today means juggling five apps — one scans your
> skin, another tries on clothes, a third recommends products, and none of them talk to
> each other. **AuraAI is one autonomous agent that does all of it** — and *it* decides
> what to run. You just talk to it."

*(On screen: landing page, animated hero — "Your Personal AI Skin & Style Agent".)*

---

### 0:20 – 1:00 · Skin Analysis

> "Let's ask a real question: *'I have acne — what should I wear? And can I try this
> jacket?'* I attach a selfie and a jacket, and hit send."

*(Attach selfie + garment, send. Point at the center Timeline.)*

> "Watch the agent think. It classified the intent as **Skin &amp; Style** — I never told it
> to run skin analysis. Now it's streaming its plan live: uploading, analysing skin,
> reading skin tone…"

*(Results panel fills.)*

> "Here are the skin scores — **acne 70, oiliness 58** — on animated gauges, with an
> overlay heatmap I can toggle. This is real YouCam skin analysis, mapped to a clean UI."

---

### 1:00 – 1:45 · Virtual Try-On

> "Because I attached a garment, the agent *also* chose to run a virtual try-on — again,
> its decision. Here's the jacket rendered on me."

*(Scrub the before/after slider; open fullscreen; zoom.)*

> "Drag to compare before and after, open fullscreen to zoom, and download the look. And
> notice the **Aura Score** up top — a single confidence number blending skin health,
> color harmony and style match. That's the number people screenshot and share."

---

### 1:45 – 2:20 · AI Stylist

> "Now the reasoning. Gemini takes the skin scores, my **warm undertone**, and an
> **Autumn** palette, and writes one grounded reply — plus structured recommendations."

*(Open the Recommendations tabs.)*

> "Skincare: a BHA cleanser and oil-free moisturiser — because oiliness is elevated.
> Fashion: an olive overshirt that echoes my palette. Colors and shopping too. Every
> suggestion is justified by the actual data, not generic filler."

---

### 2:20 – 2:45 · Architecture

> "Under the hood: a **LangGraph** agent. It detects intent, conditionally routes to the
> right tools, executes them in order, then summarises and persists memory. Adding a new
> capability is a one-line registry change — the graph never moves."

*(Show `docs/AGENT.md` graph or `submission/workflow.svg`.)*

> "FastAPI orchestrates YouCam and Gemini asynchronously with retries and polling; Redis
> and Supabase hold short- and long-term memory."

---

### 2:45 – 3:00 · Closing

> "And if any API ever hiccups mid-demo, AuraAI **automatically** falls back to demo
> assets — so it never breaks in front of an audience. One agent, your whole routine.
> That's **AuraAI**."

*(End on the Aura Score card / landing.)*

---

**Fallback if live services are down:** everything above runs identically in Demo Mode.
Switch personas (Maya / Daniel / Priya) to show acne+casual, dry+business, and
sensitive+evening in seconds.
