"use client";

import { Download, Expand, Shirt } from "lucide-react";
import { useState } from "react";

import { BeforeAfterSlider } from "@/components/vto/before-after-slider";
import { Dialog } from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TryOnResponse } from "@/types/api";

export function VtoCard({
  data,
  beforeSrc,
}: {
  data: TryOnResponse;
  beforeSrc?: string | null;
}) {
  const [fullscreen, setFullscreen] = useState(false);
  const afterSrc = data.output_images.find(Boolean);

  const download = () => {
    if (!afterSrc) return;
    const link = document.createElement("a");
    link.href = afterSrc;
    link.download = `aura-tryon-${data.task_id}.jpg`;
    link.click();
  };

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <span className="grid size-8 place-items-center rounded-lg bg-primary/15 text-primary">
            <Shirt className="size-4" />
          </span>
          <CardTitle>Virtual try-on</CardTitle>
        </div>
        <div className="flex items-center gap-1.5">
          <IconAction label="Fullscreen" onClick={() => setFullscreen(true)}>
            <Expand className="size-4" />
          </IconAction>
          <IconAction label="Download image" onClick={download} disabled={!afterSrc}>
            <Download className="size-4" />
          </IconAction>
        </div>
      </CardHeader>
      <CardContent>
        <BeforeAfterSlider beforeSrc={beforeSrc ?? undefined} afterSrc={afterSrc} />
        <p className="mt-3 text-xs text-muted-foreground">
          Drag the handle to compare. Open fullscreen to zoom.
        </p>
      </CardContent>

      <Dialog open={fullscreen} onClose={() => setFullscreen(false)} label="Try-on fullscreen" className="max-w-xl">
        <ZoomView src={afterSrc} beforeSrc={beforeSrc ?? undefined} />
      </Dialog>
    </Card>
  );
}

function IconAction({
  label,
  onClick,
  disabled,
  children,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      disabled={disabled}
      className="grid size-9 place-items-center rounded-full border border-border text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:opacity-40 focus-visible:ring-focus"
    >
      {children}
    </button>
  );
}

function ZoomView({ src, beforeSrc }: { src?: string; beforeSrc?: string }) {
  const [zoom, setZoom] = useState(1);
  return (
    <div className="p-4">
      <div className="relative aspect-[4/5] w-full overflow-hidden rounded-2xl border border-border bg-muted">
        <div
          className="size-full transition-transform duration-200"
          style={{ transform: `scale(${zoom})` }}
        >
          <BeforeAfterSlider beforeSrc={beforeSrc} afterSrc={src} className="rounded-none border-0" />
        </div>
      </div>
      <div className="mt-4 flex items-center justify-center gap-3">
        <span className="text-xs text-muted-foreground">Zoom</span>
        <input
          type="range"
          min={1}
          max={2.5}
          step={0.1}
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
          className="h-1 w-48 cursor-pointer appearance-none rounded-full bg-muted accent-primary"
          aria-label="Zoom level"
        />
        <span className="w-10 text-right text-xs tabular-nums text-muted-foreground">
          {zoom.toFixed(1)}×
        </span>
      </div>
    </div>
  );
}
