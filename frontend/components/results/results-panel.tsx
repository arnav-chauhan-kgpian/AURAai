"use client";

import { AnimatePresence, motion } from "framer-motion";
import { LayoutGrid } from "lucide-react";

import { EmptyState } from "@/components/common/empty-state";
import { AuraScoreCard } from "@/components/results/aura-score-card";
import { ColorPaletteCard } from "@/components/results/color-palette-card";
import { Recommendations } from "@/components/results/recommendations";
import { SkinResultsCard } from "@/components/skin/skin-results-card";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { VtoCard } from "@/components/vto/vto-card";
import { useSessionStore } from "@/lib/store";

const fade = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { ease: [0.16, 1, 0.3, 1], duration: 0.4 },
};

export function ResultsPanel({ className }: { className?: string }) {
  const status = useSessionStore((s) => s.status);
  const results = useSessionStore((s) => s.results);
  const streaming = status === "streaming";
  const hasAny = results.skin || results.palette || results.tryOn || results.recommendations;

  return (
    <section className={className} aria-label="Results">
      <header className="flex h-14 items-center gap-2 border-b border-border px-5 text-sm font-medium">
        <LayoutGrid className="size-4 text-primary" />
        Results
      </header>

      <div className="space-y-4 p-4 sm:p-5">
        {!hasAny && !streaming && <EmptyState variant="no-recommendations" />}

        {streaming && !hasAny && <ResultsSkeleton />}

        <AnimatePresence mode="popLayout">
          {hasAny && (
            <motion.div key="aura" layout {...fade}>
              <AuraScoreCard />
            </motion.div>
          )}
          {results.skin && (
            <motion.div key="skin" layout {...fade}>
              <SkinResultsCard data={results.skin} selfieUrl={results.selfieUrl} />
            </motion.div>
          )}
          {results.palette && (
            <motion.div key="palette" layout {...fade}>
              <ColorPaletteCard data={results.palette} />
            </motion.div>
          )}
          {results.tryOn && (
            <motion.div key="vto" layout {...fade}>
              <VtoCard data={results.tryOn} />
            </motion.div>
          )}
          {results.recommendations && (
            <motion.div key="recs" layout {...fade}>
              <Recommendations data={results.recommendations} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}

function ResultsSkeleton() {
  return (
    <Card>
      <CardHeader className="gap-3">
        <div className="flex items-center gap-2">
          <Skeleton className="size-8 rounded-lg" />
          <Skeleton className="h-4 w-32" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <Skeleton className="size-[108px] rounded-full" />
              <Skeleton className="h-3 w-14" />
            </div>
          ))}
        </div>
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="aspect-[4/5] w-full rounded-2xl" />
      </CardContent>
    </Card>
  );
}
