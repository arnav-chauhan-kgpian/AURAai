/**
 * Public runtime environment.
 *
 * Centralises access to `NEXT_PUBLIC_*` variables so components never read
 * `process.env` directly and required configuration is documented in one place.
 */
export const env = {
  /** Base URL of the AuraAI backend. */
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  /** When true, the app serves realistic mock data instead of calling the API. */
  useMock: process.env.NEXT_PUBLIC_USE_MOCK === "true",
} as const;
