# AuraAgent — autonomous stylist agent

AuraAgent decides *which* capabilities to use for a request. The user never names
an API; the planner classifies intent and the tool registry routes it.

## Pipeline

```
        ┌──────────────┐
 START →│ detect_intent│  recall memory (Redis+Supabase) → Planner (Gemini structured) → Intent
        └──────┬───────┘
               │ route_after_intent (conditional)
        ┌──────┴───────────────┐
        ▼                      ▼
 ┌──────────────┐        (no tools: CHAT_ONLY / UNKNOWN)
 │ execute_tools│  run intent's tools in order, threading state
 └──────┬───────┘              │
        └──────────┬───────────┘
                   ▼
            ┌────────────┐
            │ summarize  │  Gemini composes the reply (streamable)
            └─────┬──────┘
                  ▼
          ┌────────────────┐
          │ persist_memory │  history + snapshot + learned profile
          └───────┬────────┘
                  ▼
                 END
```

## Intent → tools

| Intent | Tools executed |
| --- | --- |
| `SKIN_ONLY` | skin_analysis → recommendation |
| `TRYON_ONLY` | virtual_try_on |
| `STYLE_ONLY` | color_palette → recommendation |
| `SKIN_AND_STYLE` | skin_analysis → color_palette → recommendation → virtual_try_on |
| `CHAT_ONLY` / `UNKNOWN` | (none — converse only) |

Routing lives in `ToolRegistry`; a tool that lacks its inputs (e.g. no garment
image for try-on) skips cleanly instead of failing the turn.

## Components

- **Planner** (`agents/planner.py`) — Gemini structured output, keyword fallback.
- **Tools** (`tools/`) — all implement `AuraTool` (`base.py`): `SkinAnalysisTool`,
  `VirtualTryOnTool`, `ColorPaletteTool`, `RecommendationTool`,
  `ConversationMemoryTool`.
- **Memory** (`agents/memory.py`, `agents/stores.py`) — short-term Redis session
  cache + long-term Supabase profile; in-memory backends for tests.
- **LLM** (`agents/llm.py` interface, `services/gemini_client.py` Gemini impl) —
  `complete` / `structured` / `stream`; mocked in tests.
- **Graph** (`workflows/aura_graph.py`) — compiled LangGraph `StateGraph`.
- **Prompts** (`prompts/*.md`) — `system`, `planner`, `stylist`, `skin`, `fashion`.

## Extending

Add a capability without touching the graph:

```python
registry.register(MyTool(service), intents=[Intent.STYLE_ONLY])
```
