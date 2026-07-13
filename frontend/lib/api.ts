/**
 * AuraAI backend endpoints.
 *
 * The single module every feature imports for backend communication. All calls
 * degrade to realistic mock data when `NEXT_PUBLIC_USE_MOCK` is set or the
 * backend is unreachable, so the experience never dead-ends on a network error.
 */
import { apiJson } from "@/lib/api-client";
import { getAuthToken } from "@/lib/auth-token";
import { env } from "@/lib/env";
import { MOCK_CHAT_RESPONSE, mockStream } from "@/lib/mock";
import type { ChatRequestInput, ChatResponse, StreamEvent } from "@/types/api";

function toFormData(input: ChatRequestInput): FormData {
  const form = new FormData();
  form.append("message", input.message);
  if (input.face_image) form.append("face_image", input.face_image);
  if (input.garment_image) form.append("garment_image", input.garment_image);
  form.append("garment_category", input.garment_category ?? "upper_body");
  return form;
}

/** Auth + server-owned-session headers for a request. */
async function authHeaders(input: ChatRequestInput): Promise<Record<string, string>> {
  const headers: Record<string, string> = { "X-Session-Id": input.session_id };
  const token = await getAuthToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

/** Non-streaming chat turn. Falls back to mock data if the backend is down. */
export async function sendChat(input: ChatRequestInput): Promise<ChatResponse> {
  if (env.useMock) return { ...MOCK_CHAT_RESPONSE, session_id: input.session_id };
  try {
    return await apiJson<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: toFormData(input),
      headers: await authHeaders(input),
    });
  } catch {
    return { ...MOCK_CHAT_RESPONSE, session_id: input.session_id };
  }
}

/**
 * Stream a chat turn as SSE events. Parses `data:` frames from the POST stream.
 *
 * Mock data is served ONLY in explicit demo mode (`NEXT_PUBLIC_USE_MOCK`). A
 * real backend error surfaces the actual message (via an `error` event) rather
 * than silently returning fake results, which would hide the real problem.
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
      headers: await authHeaders(input),
      signal,
    });
  } catch {
    yield {
      type: "error",
      data: { message: "Can't reach the server. Make sure the backend is running." },
    };
    return;
  }

  if (!response.ok || !response.body) {
    let message = `The request failed (${response.status}).`;
    try {
      const body = await response.json();
      message = body?.error?.message ?? message;
    } catch {
      /* non-JSON error body */
    }
    yield { type: "error", data: { message } };
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

/** Bearer auth headers for non-chat authenticated calls. */
async function bearerHeaders(): Promise<Record<string, string>> {
  const token = await getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Whether the signed-in user has consented to face-image processing. */
export async function getConsent(): Promise<boolean> {
  if (env.useMock) return true;
  try {
    const res = await apiJson<{ granted?: boolean }>("/api/v1/privacy/consent", {
      headers: await bearerHeaders(),
      retries: 0,
    });
    return Boolean(res.granted);
  } catch {
    return false;
  }
}

/** Record (grant/withdraw) consent to process face images. */
export async function setConsent(granted: boolean): Promise<boolean> {
  if (env.useMock) return granted;
  try {
    const res = await apiJson<{ granted?: boolean }>("/api/v1/privacy/consent", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(await bearerHeaders()) },
      body: JSON.stringify({ granted }),
    });
    return Boolean(res.granted);
  } catch {
    return false;
  }
}

/** GDPR erasure of the signed-in user's data. */
export async function deleteAccountData(): Promise<boolean> {
  try {
    await apiJson("/api/v1/privacy/account", { method: "DELETE", headers: await bearerHeaders() });
    return true;
  } catch {
    return false;
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
