"use client";

import { LayoutGrid, MessageSquare, Activity } from "lucide-react";
import { useState } from "react";

import { ChatPanel } from "@/components/chat/chat-panel";
import { IntentPill } from "@/components/dashboard/intent-pill";
import { ResultsPanel } from "@/components/results/results-panel";
import { Timeline } from "@/components/timeline/timeline";
import { cn } from "@/lib/utils";

type MobileView = "chat" | "timeline" | "results";

const MOBILE_TABS: { id: MobileView; label: string; icon: typeof MessageSquare }[] = [
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "timeline", label: "Timeline", icon: Activity },
  { id: "results", label: "Results", icon: LayoutGrid },
];

export function DashboardShell() {
  const [view, setView] = useState<MobileView>("chat");

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      {/* Mobile / tablet segmented control */}
      <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-2 xl:hidden">
        <div className="inline-flex rounded-full bg-muted/70 p-1">
          {MOBILE_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setView(tab.id)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all focus-visible:ring-focus",
                view === tab.id ? "bg-card text-foreground shadow-sm" : "text-muted-foreground",
              )}
            >
              <tab.icon className="size-3.5" />
              {tab.label}
            </button>
          ))}
        </div>
        <IntentPill />
      </div>

      {/* Desktop three-pane layout */}
      <div className="min-h-0 flex-1 xl:grid xl:grid-cols-[minmax(340px,1fr)_320px_minmax(380px,1.3fr)]">
        <div className={cn("h-full min-h-0", view === "chat" ? "block" : "hidden", "xl:block xl:border-r xl:border-border")}>
          <ChatPanel className="h-full" />
        </div>
        <div className={cn("h-full min-h-0 overflow-y-auto", view === "timeline" ? "block" : "hidden", "xl:block xl:border-r xl:border-border")}>
          <Timeline />
        </div>
        <div className={cn("h-full min-h-0 overflow-y-auto", view === "results" ? "block" : "hidden", "xl:block")}>
          <ResultsPanel />
        </div>
      </div>
    </div>
  );
}
