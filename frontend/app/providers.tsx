"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

import { ThemeProvider } from "@/components/theme-provider";
import { clerkEnabled, clerkPublishableKey } from "@/lib/clerk";
import { makeQueryClient } from "@/lib/query-client";

/** Client-side context providers shared across the app. */
export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(makeQueryClient);

  const tree = (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>{children}</ThemeProvider>
    </QueryClientProvider>
  );

  // Only mount Clerk when configured, so demo mode runs without any keys.
  return clerkEnabled ? (
    <ClerkProvider publishableKey={clerkPublishableKey}>{tree}</ClerkProvider>
  ) : (
    tree
  );
}
