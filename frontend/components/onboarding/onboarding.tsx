"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Palette, ScanFace, Shirt, Sparkles, type LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { Button } from "@/components/ui/button";
import { useMounted } from "@/hooks/use-mounted";
import { useOnboardingStore } from "@/lib/onboarding-store";
import { cn } from "@/lib/utils";

interface Screen {
  icon: LucideIcon;
  title: string;
  body: string;
  accent: string;
}

const SCREENS: Screen[] = [
  {
    icon: ScanFace,
    title: "Skin Analysis",
    body: "Snap a selfie and AuraAI scores concerns like acne, pores and redness — dermatologist-grade, in seconds.",
    accent: "from-violet-500/30",
  },
  {
    icon: Shirt,
    title: "Virtual Try-On",
    body: "Attach any garment and see it rendered on you, with realistic fit and fabric, before you buy.",
    accent: "from-fuchsia-500/30",
  },
  {
    icon: Palette,
    title: "AI Stylist",
    body: "One agent decides what to analyse, then plans skincare and complete outfits tuned to your palette.",
    accent: "from-indigo-500/30",
  },
];

export function Onboarding() {
  const mounted = useMounted();
  const { open, hydrated, hydrate, complete } = useOnboardingStore();
  const [step, setStep] = useState(0);

  useEffect(() => hydrate(), [hydrate]);

  if (!mounted || !hydrated) return null;

  const last = step === SCREENS.length - 1;
  const screen = SCREENS[step];
  const Icon = screen.icon;

  return createPortal(
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[60] flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-background/80 backdrop-blur-md" aria-hidden />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label="Welcome to AuraAI"
            initial={{ opacity: 0, scale: 0.95, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 8 }}
            transition={{ type: "spring", stiffness: 300, damping: 28 }}
            className="relative z-10 w-full max-w-md overflow-hidden rounded-lg glass-strong shadow-soft"
          >
            <div className={cn("relative h-40 bg-gradient-to-b to-transparent", screen.accent)}>
              <div className="absolute inset-0 flex items-center justify-center">
                <AnimatePresence mode="wait">
                  <motion.span
                    key={step}
                    initial={{ scale: 0.6, opacity: 0, rotate: -12 }}
                    animate={{ scale: 1, opacity: 1, rotate: 0 }}
                    exit={{ scale: 0.6, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 260, damping: 20 }}
                    className="grid size-20 place-items-center rounded-3xl bg-brand shadow-glow"
                  >
                    <Icon className="size-9 text-white" />
                  </motion.span>
                </AnimatePresence>
              </div>
              <span className="absolute left-5 top-5 inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <Sparkles className="size-3.5 text-primary" /> Welcome to AuraAI
              </span>
            </div>

            <div className="p-6 pt-4 text-center">
              <AnimatePresence mode="wait">
                <motion.div
                  key={step}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.25 }}
                >
                  <h2 className="text-xl font-semibold tracking-tight">{screen.title}</h2>
                  <p className="mx-auto mt-2 max-w-xs text-sm leading-relaxed text-muted-foreground">
                    {screen.body}
                  </p>
                </motion.div>
              </AnimatePresence>

              <div className="mt-6 flex items-center justify-center gap-2">
                {SCREENS.map((_, i) => (
                  <span
                    key={i}
                    className={cn(
                      "h-1.5 rounded-full transition-all duration-300",
                      i === step ? "w-6 bg-brand" : "w-1.5 bg-muted",
                    )}
                  />
                ))}
              </div>

              <div className="mt-6 flex items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={complete}
                  className="rounded-full px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:ring-focus"
                >
                  Skip
                </button>
                <Button onClick={() => (last ? complete() : setStep((s) => s + 1))} className="group">
                  {last ? "Get started" : "Next"}
                  <ArrowRight className="transition-transform group-hover:translate-x-0.5" />
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  );
}
