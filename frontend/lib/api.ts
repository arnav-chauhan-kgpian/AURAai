/**
 * AuraAI backend endpoints.
 *
 * The single module every feature imports for backend communication. All calls
 * degrade to realistic mock data when `NEXT_PUBLIC_USE_MOCK` is set or the
 * backend is unreachable, so the experience never dead-ends on a network error.
 */
import { apiJson } from "@/lib/api-client";
import { env } from "@/lib/env";
import { MOCK_CHAT_RESPONSE, mockStream } from "@/lib/mock";
import type { ChatRequestInput, ChatResponse, StreamEvent } from "@/types/api";

function toFormData(input: ChatRequestInput): FormData {
  const form = new FormData();
  form.append("session_id", input.session_id);
  form.append("message", input.message);
  if (input.face_image) form.append("face_image", input.face_image);
  if (input.garment_image) form.append("garment_image", input.garment_image);
  form.append("garment_category", input.garment_category ?? "upper_body");
  return form;
}

/** Non-streaming chat turn. Falls back to mock data if the backend is down. */
export async function sendChat(input: ChatRequestInput): Promise<ChatResponse> {
  if (env.useMock) return { ...MOCK_CHAT_RESPONSE, session_id: input.session_id };
  try {
    return await apiJson<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: toFormData(input),
    });
  } catch {
    return { ...MOCK_CHAT_RESPONSE, session_id: input.session_id };
  }
}

/**
 * Stream a chat turn as SSE events. Parses `data:` frames from the POST stream;
 * on any transport failure it transparently switches to the simulated stream so
 * the timeline and chat always show live progress.
 */
export async function* streamChat(
  input: ChatRequestInput,
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent> {
  if (env.useMock) {
    yield* mockStream(input);
    return;
  }

  let response: Response;
  try {
    response = await fetch(`${env.apiBaseUrl}/api/v1/chat/stream`, {
      method: "POST",
      body: toFormData(input),
      signal,
    });
    if (!response.ok || !response.body) throw new Error("stream unavailable");
  } catch {
    yield* mockStream(input);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const dataLine = frame.split("\n").find((line) => line.startsWith("data:"));
      if (!dataLine) continue;
      const payload = dataLine.slice(5).trim();
      if (!payload) continue;
      try {
        yield JSON.parse(payload) as StreamEvent;
      } catch {
        /* ignore malformed frame */
      }
    }
  }
}

/** Liveness check used by the settings page connection indicator. */
export async function checkHealth(): Promise<boolean> {
  if (env.useMock) return true;
  try {
    await apiJson<{ status: string }>("/api/v1/health", { retries: 0 });
    return true;
  } catch {
    return false;
  }
}
