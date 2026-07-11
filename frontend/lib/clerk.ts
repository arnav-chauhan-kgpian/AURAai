/**
 * Clerk configuration gate.
 *
 * Auth is enabled only when a publishable key is present. This keeps the app
 * fully runnable in demo mode (no keys) while enabling real authentication in
 * production — backward compatibility with the anonymous/demo experience.
 */
export const clerkPublishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ?? "";
export const clerkEnabled = clerkPublishableKey.length > 0;
