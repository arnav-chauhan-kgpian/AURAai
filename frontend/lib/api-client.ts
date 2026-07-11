/**
 * Typed HTTP client for the AuraAI backend.
 *
 * A single fetch wrapper all data access builds on: base-URL resolution, JSON
 * handling, a normalised {@link ApiError}, and exponential-backoff retry on
 * transient failures (network errors and 429/5xx).
 */
import { env } from "@/lib/env";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const RETRY_STATUSES = new Set([429, 500, 502, 503, 504]);
const DEFAULT_RETRIES = 2;

interface RequestOptions extends RequestInit {
  /** Number of retry attempts on transient failure (default 2). */
  retries?: number;
}

function backoff(attempt: number): number {
  return Math.min(4000, 300 * 2 ** attempt) * (0.5 + Math.random() * 0.5);
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function toApiError(response: Response): Promise<ApiError> {
  let message = `Request failed (${response.status})`;
  let code: string | undefined;
  try {
    const body = await response.json();
    const err = body?.error ?? body;
    message = err?.message ?? message;
    code = err?.code;
  } catch {
    /* non-JSON error body */
  }
  return new ApiError(message, response.status, code);
}

/** Perform a fetch against the API with retry, returning the raw Response. */
export async function apiFetch(path: string, options: RequestOptions = {}): Promise<Response> {
  const { retries = DEFAULT_RETRIES, ...init } = options;
  const url = path.startsWith("http") ? path : `${env.apiBaseUrl}${path}`;

  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, init);
      if (RETRY_STATUSES.has(response.status) && attempt < retries) {
        await sleep(backoff(attempt));
        continue;
      }
      if (!response.ok) throw await toApiError(response);
      return response;
    } catch (error) {
      lastError = error;
      const isAbort = error instanceof DOMException && error.name === "AbortError";
      if (isAbort || error instanceof ApiError || attempt === retries) throw error;
      await sleep(backoff(attempt));
    }
  }
  throw lastError instanceof Error ? lastError : new ApiError("Network error", 0);
}

/** Perform a JSON request and parse the response body. */
export async function apiJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await apiFetch(path, {
    ...options,
    headers: { Accept: "application/json", ...options.headers },
  });
  return (await response.json()) as T;
}
