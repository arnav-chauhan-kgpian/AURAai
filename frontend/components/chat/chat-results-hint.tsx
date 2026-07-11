"use client";

import { AnimatePresence, motion } from "framer-motion";
import { LayoutGrid } from "lucide-react";
import Link from "next/link";

import { useSessionStore } from "@/lib/store";

/** Floating prompt to view structured results on the dashboard. */
export function ChatResultsHint() {
  const results = useSessionStore((s) => s.results);
  const hasResults = Boolean(
    results.skin || results.palette || results.tryOn || results.recommendations,
  );

  return (
    <AnimatePresence>
      {hasResults && (
        <motion.div
          initial={{ opacity: 0, y: 16, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 16, scale: 0.95 }}
          className="fixed bottom-24 right-4 z-30 sm:bottom-6 sm:right-6"
        >
          <Link
            href="/dashboard"
            className="glass-strong flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-medium shadow-soft transition-transform hover:-translate-y-0.5 focus-visible:ring-focus"
          >
            <LayoutGrid className="size-4 text-primary" />
            View full results
          </Link>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
