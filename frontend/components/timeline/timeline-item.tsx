"use client";

import { motion } from "framer-motion";
import { Check, type LucideIcon } from "lucide-react";

import type { PhaseStatus } from "@/lib/store";
import { cn } from "@/lib/utils";

export function TimelineItem({
  icon: Icon,
  label,
  status,
  isLast,
}: {
  icon: LucideIcon;
  label: string;
  status: PhaseStatus;
  isLast: boolean;
}) {
  return (
    <motion.li
      layout
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: "spring", stiffness: 400, damping: 32 }}
      className="relative flex gap-4 pb-6"
    >
      {!isLast && (
        <span
          className={cn(
            "absolute left-[19px] top-10 h-[calc(100%-1.5rem)] w-px",
            status === "complete" ? "bg-primary/50" : "bg-border",
          )}
          aria-hidden
        />
      )}

      <div className="relative">
        <span
          className={cn(
            "grid size-10 place-items-center rounded-full border transition-colors",
            status === "complete" && "border-primary/50 bg-primary/15 text-primary",
            status === "active" && "border-primary bg-primary/10 text-primary",
            status === "pending" && "border-border bg-card text-muted-foreground",
          )}
        >
          {status === "complete" ? (
            <Check className="size-5" />
          ) : (
            <Icon className="size-[18px]" />
          )}
        </span>
        {status === "active" && (
          <span className="absolute inset-0 rounded-full border border-primary animate-pulse-ring" aria-hidden />
        )}
      </div>

      <div className="flex min-h-10 flex-col justify-center">
        <span
          className={cn(
            "text-sm font-medium transition-colors",
            status === "pending" ? "text-muted-foreground" : "text-foreground",
          )}
        >
          {label}
        </span>
        <span className="text-xs text-muted-foreground">
          {status === "active" ? "In progress…" : status === "complete" ? "Complete" : "Waiting"}
        </span>
      </div>
    </motion.li>
  );
}
