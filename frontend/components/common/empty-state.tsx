"use client";

import { motion } from "framer-motion";
import {
  CloudOff,
  ImageOff,
  ServerCrash,
  Shirt,
  Sparkles,
  UserRoundSearch,
  type LucideIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";

export type EmptyStateVariant =
  | "no-selfie"
  | "no-garment"
  | "no-recommendations"
  | "no-history"
  | "no-internet"
  | "api-unavailable";

interface Preset {
  icon: LucideIcon;
  title: string;
  description: string;
}

const PRESETS: Record<EmptyStateVariant, Preset> = {
  "no-selfie": {
    icon: UserRoundSearch,
    title: "Add a selfie to begin",
    description: "Attach a well-lit, front-facing photo and AuraAI will analyse your skin.",
  },
  "no-garment": {
    icon: Shirt,
    title: "No garment yet",
    description: "Attach a clothing image to see it rendered on you with a virtual try-on.",
  },
  "no-recommendations": {
    icon: Sparkles,
    title: "No recommendations yet",
    description: "Ask about your skin or style and tailored advice will appear here.",
  },
  "no-history": {
    icon: ImageOff,
    title: "Nothing here yet",
    description: "Your past looks and analyses will collect here as you use AuraAI.",
  },
  "no-internet": {
    icon: CloudOff,
    title: "You're offline",
    description: "Check your connection. Demo Mode keeps the experience running without a network.",
  },
  "api-unavailable": {
    icon: ServerCrash,
    title: "Service is warming up",
    description: "The analysis service is briefly unavailable — Demo Mode has you covered meanwhile.",
  },
};

export function EmptyState({
  variant,
  action,
  className,
}: {
  variant: EmptyStateVariant;
  action?: React.ReactNode;
  className?: string;
}) {
  const preset = PRESETS[variant];
  const Icon = preset.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed border-border px-6 py-12 text-center",
        className,
      )}
    >
      <div className="relative">
        <span className="absolute inset-0 rounded-2xl bg-brand opacity-20 blur-xl" aria-hidden />
        <span className="relative grid size-14 place-items-center rounded-2xl border border-border bg-card text-primary">
          <Icon className="size-6" />
        </span>
      </div>
      <p className="mt-5 text-sm font-semibold">{preset.title}</p>
      <p className="mt-1.5 max-w-[16rem] text-xs leading-relaxed text-muted-foreground">
        {preset.description}
      </p>
      {action && <div className="mt-5">{action}</div>}
    </motion.div>
  );
}
