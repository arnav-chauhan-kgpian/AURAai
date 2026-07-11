# Architecture

AuraAI follows a clean, layered architecture with a single, inward dependency
direction. Nothing in an inner layer imports from an outer one.

```
transport (api)  →  application (services, agents)  →  infrastructure (db, storage, providers)
```

## Backend layers

| Layer | Package | Responsibility | May depend on |
| --- | --- | --- | --- |
| Transport | `app/api` | HTTP routing, request/response mapping | core, schemas, services (via DI) |
| Core | `app/core` | config access, logging, exceptions, DI wiring | config, db, services, agents |
| Application | `app/services` | capability logic; the only caller of providers | schemas, db, storage, config |
| Agent | `app/agents`, `app/workflows`, `app/tools` | planning, memory, tool orchestration | services, schemas, config |
| Domain | `app/schemas`, `app/models` | transport contracts vs. persistence models | — |
| Infrastructure | `app/db`, `app/storage` | Supabase / Redis clients, object store | config |

## The agent

The differentiator is the **agent**, not the endpoints. A LangGraph state graph
(`app/workflows/stylist_graph.py`) threads an explicit `AgentState`
(`app/agents/state.py`) through planning, tool-execution and synthesis nodes:

1. **Plan** — `Planner` decomposes the user goal into ordered tool steps.
2. **Act** — the graph invokes tools from the `ToolRegistry` (skin, VTO, recommendation).
3. **Observe & replan** — results update state; the planner may revise remaining steps.
4. **Synthesise** — Gemini turns accumulated signals into a `RecommendationSet`.

Per-session conversation state lives in Redis via `ConversationMemory`.

## Request lifecycle

```
Client → FastAPI router → dependency provider → service/agent → provider(s) → response
                      ↑ RequestContextMiddleware binds a correlation id
                      ↑ error_handler maps AuraError → JSON error contract
```

## Design rules

- Services are the only layer permitted to call external providers.
- Transport schemas (`app/schemas`) are decoupled from persistence models (`app/models`).
- Configuration is accessed exclusively through `get_settings()`.
- Exceptions derive from `AuraError` so the API produces a stable error contract.
