"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";

import { useMounted } from "@/hooks/use-mounted";
import { useThemeStore } from "@/lib/theme-store";

export function ThemeToggle() {
  const mounted = useMounted();
  const theme = useThemeStore((s) => s.theme);
  const toggle = useThemeStore((s) => s.toggle);

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className="relative grid size-10 place-items-center overflow-hidden rounded-full border border-border bg-card/50 text-foreground transition-colors hover:bg-secondary/70 focus-visible:ring-focus"
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={mounted ? theme : "loading"}
          initial={{ y: -18, opacity: 0, rotate: -30 }}
          animate={{ y: 0, opacity: 1, rotate: 0 }}
          exit={{ y: 18, opacity: 0, rotate: 30 }}
          transition={{ duration: 0.2 }}
        >
          {theme === "dark" ? <Moon className="size-[18px]" /> : <Sun className="size-[18px]" />}
        </motion.span>
      </AnimatePresence>
    </button>
  );
}
