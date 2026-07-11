"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ScanFace } from "lucide-react";
import { useState } from "react";

import { Switch } from "@/components/ui/switch";
import type { OverlayImage } from "@/types/api";

/** Selfie preview with a toggleable concern heatmap overlay. */
export function OverlayPreview({
  overlays,
  imageUrl,
}: {
  overlays: OverlayImage[];
  imageUrl?: string;
}) {
  const [heatmap, setHeatmap] = useState(true);
  const realOverlay = overlays.find((o) => o.url)?.url;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Overlay preview</span>
        <label className="flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
          Heatmap
          <Switch checked={heatmap} onCheckedChange={setHeatmap} aria-label="Toggle heatmap" />
        </label>
      </div>

      <div className="relative aspect-[4/5] w-full overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-secondary/60 to-muted">
        {imageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={imageUrl} alt="Analyzed selfie" className="size-full object-cover" />
        ) : (
          <div className="flex size-full flex-col items-center justify-center gap-2 text-muted-foreground">
            <ScanFace className="size-10" />
            <span className="text-xs">Selfie preview</span>
          </div>
        )}

        <AnimatePresence>
          {heatmap && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 mix-blend-screen"
              style={{
                backgroundImage: realOverlay
                  ? `url(${realOverlay})`
                  : [
                      "radial-gradient(circle at 38% 40%, hsl(0 80% 55% / 0.55), transparent 22%)",
                      "radial-gradient(circle at 60% 44%, hsl(20 90% 55% / 0.5), transparent 20%)",
                      "radial-gradient(circle at 50% 62%, hsl(38 90% 55% / 0.45), transparent 26%)",
                      "radial-gradient(circle at 30% 66%, hsl(0 80% 55% / 0.4), transparent 18%)",
                    ].join(","),
                backgroundSize: realOverlay ? "cover" : undefined,
              }}
              aria-hidden
            />
          )}
        </AnimatePresence>

        {heatmap && (
          <div className="absolute bottom-3 left-3 flex items-center gap-2 rounded-full bg-background/70 px-2.5 py-1 text-2xs backdrop-blur">
            <span className="flex items-center gap-1">
              <span className="size-2 rounded-full bg-[hsl(0_80%_55%)]" /> High
            </span>
            <span className="flex items-center gap-1">
              <span className="size-2 rounded-full bg-[hsl(38_90%_55%)]" /> Moderate
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
