/**
 * Bearer-token access for API calls.
 *
 * When Clerk is configured, it injects `window.Clerk`; we pull a short-lived
 * session token from the active session to authorize backend requests. Returns
 * null in demo/anonymous mode, where the backend falls back to an anonymous
 * context (dev only).
 */
interface ClerkWindow {
  Clerk?: { session?: { getToken?: () => Promise<string | null> } };
}

export async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const clerk = (window as unknown as ClerkWindow).Clerk;
  try {
    return (await clerk?.session?.getToken?.()) ?? null;
  } catch {
    return null;
  }
}
