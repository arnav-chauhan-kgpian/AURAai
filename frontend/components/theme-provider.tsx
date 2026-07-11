"use client";

import { useEffect } from "react";

import { useThemeStore } from "@/lib/theme-store";

/** Applies the persisted theme on mount (dark by default). */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const hydrate = useThemeStore((s) => s.hydrate);
  useEffect(() => hydrate(), [hydrate]);
  return <>{children}</>;
}
