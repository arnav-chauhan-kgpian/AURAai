/**
 * Auth middleware.
 *
 * Protects app routes with Clerk when configured. When no Clerk key is present
 * (demo mode), it's a pass-through so the anonymous experience keeps working.
 */
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

const isProtected = createRouteMatcher(["/chat(.*)", "/dashboard(.*)", "/settings(.*)"]);

const guarded = clerkMiddleware(async (auth, req) => {
  if (isProtected(req)) await auth.protect();
});

export default clerkEnabled ? guarded : () => NextResponse.next();

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)", "/__clerk/:path*"],
};
