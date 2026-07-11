"use client";

import { motion } from "framer-motion";
import { Check, Copy, Palette } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCopy } from "@/hooks/use-copy";
import { colorToCss, humanize } from "@/lib/utils";
import type { ColorPalette } from "@/types/api";

export function ColorPaletteCard({ data }: { data: ColorPalette }) {
  const { copied, copy } = useCopy();
  const undertoneWarm = data.undertone.toLowerCase().includes("warm");

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <span className="grid size-8 place-items-center rounded-lg bg-accent/15 text-accent">
            <Palette className="size-4" />
          </span>
          <CardTitle>Color palette</CardTitle>
        </div>
        <button
          type="button"
          onClick={() => copy(data.recommended_colors.join(", "))}
          className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-xs transition-colors hover:bg-secondary focus-visible:ring-focus"
          aria-label="Copy palette"
        >
          {copied ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="brand">{data.season}</Badge>
          <Badge variant={undertoneWarm ? "warning" : "default"}>
            {humanize(data.undertone)} undertone
          </Badge>
          <Badge variant="outline">Fitzpatrick {data.fitzpatrick_type}</Badge>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-muted-foreground">Recommended</p>
          <div className="grid grid-cols-5 gap-2">
            {data.recommended_colors.map((color, i) => (
              <Swatch key={color} color={color} index={i} />
            ))}
          </div>
        </div>

        {data.avoid_colors.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium text-muted-foreground">Best avoided</p>
            <div className="flex flex-wrap gap-2">
              {data.avoid_colors.map((color) => (
                <span
                  key={color}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground"
                >
                  <span
                    className="size-3 rounded-full ring-1 ring-inset ring-black/10"
                    style={{ background: colorToCss(color) }}
                  />
                  {humanize(color)}
                </span>
              ))}
            </div>
          </div>
        )}

        <p className="text-xs leading-relaxed text-muted-foreground">{data.rationale}</p>
      </CardContent>
    </Card>
  );
}

function Swatch({ color, index }: { color: string; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05, type: "spring", stiffness: 300, damping: 20 }}
      className="group flex flex-col items-center gap-1.5"
      title={color}
    >
      <span
        className="aspect-square w-full rounded-xl ring-1 ring-inset ring-black/10 transition-transform group-hover:scale-105"
        style={{ background: colorToCss(color) }}
      />
      <span className="max-w-full truncate text-2xs text-muted-foreground">{color}</span>
    </motion.div>
  );
}
