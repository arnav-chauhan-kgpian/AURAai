"use client";

import { Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { INTENT_LABELS } from "@/lib/constants";
import { useSessionStore } from "@/lib/store";

/** Shows the agent's currently detected intent, once known. */
export function IntentPill() {
  const intent = useSessionStore((s) => s.results.intent);
  if (!intent) return null;
  return (
    <Badge variant="brand" className="gap-1.5">
      <Sparkles className="size-3" />
      {INTENT_LABELS[intent] ?? intent}
    </Badge>
  );
}
