"use client";

import { useEffect } from "react";

import { useMounted } from "@/hooks/use-mounted";
import { useDemoStore } from "@/lib/demo-store";

/** Small pill shown in the header while Demo Mode is active. */
export function DemoBadge() {
  const mounted = useMounted();
  const enabled = useDemoStore((s) => s.enabled);
  const hydrate = useDemoStore((s) => s.hydrate);

  useEffect(() => hydrate(), [hydrate]);

  if (!mounted || !enabled) return null;

  return (
    <span className="hidden items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-2.5 py-1 text-2xs font-medium text-primary sm:inline-flex">
      <span className="size-1.5 animate-pulse rounded-full bg-primary" />
      Demo
    </span>
  );
}
