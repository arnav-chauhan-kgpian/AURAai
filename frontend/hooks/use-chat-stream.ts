"use client";

/**
 * The streaming brain of the UI.
 *
 * Consumes the SSE event generator from the API layer and projects it onto the
 * session store: it grows the assistant message token-by-token, advances the
 * live timeline phases, and lands the final structured results. The dashboard
 * and chat surfaces are pure views over that store.
 */
import { useCallback, useRef } from "react";

import { streamChat } from "@/lib/api";
import { TOOL_TO_PHASE, type TimelinePhaseId } from "@/lib/constants";
import { buildDemoStream, getDemoUser } from "@/lib/demo-users";
import { useDemoStore } from "@/lib/demo-store";
import { useSessionStore, type TimelinePhase } from "@/lib/store";
import type { ChatRequestInput, ChatResponse, StreamEvent } from "@/types/api";

const TOOL_ORDER: TimelinePhaseId[] = [
  "skin_analysis",
  "color_palette",
  "recommendation",
  "virtual_try_on",
];

export interface SendOptions {
  message: string;
  faceImage?: File | null;
  garmentImage?: File | null;
  garmentCategory?: string;
}

export function useChatStream() {
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(async ({ message, faceImage, garmentImage, garmentCategory }: SendOptions) => {
    const store = useSessionStore.getState();
    if (store.status === "streaming") return;

    const controller = new AbortController();
    abortRef.current = controller;

    store.setStatus("streaming");
    store.addUserMessage(message, Boolean(faceImage || garmentImage));
    store.setResults({ intent: null, skin: null, palette: null, tryOn: null, recommendations: null });

    const initial: TimelinePhase[] = [];
    if (faceImage) initial.push({ id: "upload", status: "active" });
    initial.push({ id: "planning", status: "pending" });
    store.setPhases(initial);

    const assistantId = store.startAssistantMessage();

    const input: ChatRequestInput = {
      session_id: store.sessionId,
      message,
      face_image: faceImage ?? null,
      garment_image: garmentImage ?? null,
      garment_category: garmentCategory ?? "upper_body",
    };

    const demo = useDemoStore.getState();
    const source = demo.enabled
      ? buildDemoStream(getDemoUser(demo.userId).response, input, { includeTryOn: true })
      : streamChat(input, controller.signal);

    try {
      for await (const event of source) {
        handleEvent(event, assistantId);
      }
    } catch {
      useSessionStore.getState().appendToken(
        assistantId,
        "\n\n_Something interrupted the connection. Please try again._",
      );
    } finally {
      completeTimeline();
      useSessionStore.getState().finishAssistantMessage(assistantId);
      useSessionStore.getState().setStatus("idle");
      abortRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { send, stop };
}

function handleEvent(event: StreamEvent, assistantId: string): void {
  const store = useSessionStore.getState();

  switch (event.type) {
    case "intent": {
      store.patchPhase("upload", "complete");
      store.patchPhase("planning", "active");
      store.setResults({ intent: (event.data.intent as ChatResponse["intent"]) ?? null });
      break;
    }
    case "step": {
      store.patchPhase("planning", "complete");
      const tools = (event.data.tools as string[]) ?? [];
      const toolPhases = TOOL_ORDER.filter((phase) =>
        tools.some((tool) => TOOL_TO_PHASE[tool] === phase),
      );
      // Lay out the planned pipeline; the real per-tool `tool` events below
      // light each phase as the backend actually starts/finishes it.
      const next: TimelinePhase[] = [
        ...store.phases.map((p) => ({ ...p, status: "complete" as const })),
        ...toolPhases.map((id) => ({ id, status: "pending" as const })),
        { id: "done" as TimelinePhaseId, status: "pending" as const },
      ];
      store.setPhases(next);
      break;
    }
    case "tool": {
      const tool = String(event.data.tool ?? "");
      const phase = TOOL_TO_PHASE[tool];
      if (phase) {
        const status = String(event.data.status ?? "");
        store.patchPhase(phase, status === "running" ? "active" : "complete");
      }
      break;
    }
    case "token": {
      store.appendToken(assistantId, String(event.data.token ?? ""));
      break;
    }
    case "final": {
      const data = event.data as unknown as ChatResponse;
      if (data.session_id && data.session_id !== store.sessionId) {
        store.setSessionId(data.session_id);
      }
      store.setResults({
        intent: data.intent ?? null,
        skin: data.skin_analysis ?? null,
        palette: data.color_palette ?? null,
        tryOn: data.try_on ?? null,
        recommendations: data.recommendations ?? null,
      });
      if (data.reply) store.finishAssistantMessage(assistantId, data.reply);
      break;
    }
    case "error": {
      const message = String(event.data.message ?? "Something went wrong. Please try again.");
      store.appendToken(assistantId, `\n\n_${message}_`);
      break;
    }
  }
}

function completeTimeline(): void {
  const store = useSessionStore.getState();
  const completed = store.phases.map((p) => ({ ...p, status: "complete" as const }));
  if (!completed.some((p) => p.id === "done")) {
    completed.push({ id: "done", status: "complete" });
  } else {
    for (const phase of completed) if (phase.id === "done") phase.status = "complete";
  }
  store.setPhases(completed);
}
