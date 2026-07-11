"use client";

import { AnimatePresence } from "framer-motion";
import { Activity } from "lucide-react";

import { TimelineItem } from "@/components/timeline/timeline-item";
import { TIMELINE_PHASES } from "@/lib/constants";
import { useSessionStore } from "@/lib/store";

const PHASE_META = Object.fromEntries(TIMELINE_PHASES.map((p) => [p.id, p]));

export function Timeline({ className }: { className?: string }) {
  const phases = useSessionStore((s) => s.phases);

  return (
    <section className={className} aria-label="Analysis timeline">
      <header className="flex h-14 items-center gap-2 border-b border-border px-5 text-sm font-medium">
        <Activity className="size-4 text-primary" />
        Agent timeline
      </header>

      <div className="p-5">
        {phases.length === 0 ? (
          <EmptyTimeline />
        ) : (
          <ol className="relative">
            <AnimatePresence initial={false}>
              {phases.map((phase, index) => {
                const meta = PHASE_META[phase.id];
                if (!meta) return null;
                return (
                  <TimelineItem
                    key={phase.id}
                    icon={meta.icon}
                    label={meta.label}
                    status={phase.status}
                    isLast={index === phases.length - 1}
                  />
                );
              })}
            </AnimatePresence>
          </ol>
        )}
      </div>
    </section>
  );
}

function EmptyTimeline() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span className="grid size-12 place-items-center rounded-2xl border border-border bg-card">
        <Activity className="size-5 text-muted-foreground" />
      </span>
      <p className="mt-4 text-sm font-medium">No active run</p>
      <p className="mt-1 max-w-[14rem] text-xs text-muted-foreground">
        Send a message and the agent&apos;s plan will stream here step by step.
      </p>
    </div>
  );
}
