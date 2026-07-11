"use client";

import { Shirt, User } from "lucide-react";
import { useCallback, useRef, useState } from "react";

import { clamp, cn } from "@/lib/utils";

/** Draggable before/after comparison. Falls back to styled placeholders. */
export function BeforeAfterSlider({
  beforeSrc,
  afterSrc,
  className,
}: {
  beforeSrc?: string;
  afterSrc?: string;
  className?: string;
}) {
  const [position, setPosition] = useState(55);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const updateFromClientX = useCallback((clientX: number) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    setPosition(clamp(((clientX - rect.left) / rect.width) * 100, 0, 100));
  }, []);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative aspect-[4/5] w-full select-none overflow-hidden rounded-2xl border border-border",
        className,
      )}
      onPointerDown={(e) => {
        dragging.current = true;
        (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
        updateFromClientX(e.clientX);
      }}
      onPointerMove={(e) => dragging.current && updateFromClientX(e.clientX)}
      onPointerUp={() => (dragging.current = false)}
    >
      <Layer src={afterSrc} variant="after" />
      <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}>
        <Layer src={beforeSrc} variant="before" />
      </div>

      <div
        className="absolute inset-y-0 z-10 flex w-0 items-center justify-center"
        style={{ left: `${position}%` }}
      >
        <div className="h-full w-0.5 bg-white/80 shadow-[0_0_12px_rgba(0,0,0,0.4)]" />
        <button
          type="button"
          role="slider"
          aria-label="Compare before and after"
          aria-valuenow={Math.round(position)}
          aria-valuemin={0}
          aria-valuemax={100}
          onKeyDown={(e) => {
            if (e.key === "ArrowLeft") setPosition((p) => clamp(p - 4, 0, 100));
            if (e.key === "ArrowRight") setPosition((p) => clamp(p + 4, 0, 100));
          }}
          className="absolute grid size-9 -translate-x-1/2 place-items-center rounded-full border border-white/60 bg-white/90 text-black shadow-lg focus-visible:ring-focus"
          style={{ left: "50%" }}
        >
          <span className="text-xs">⇄</span>
        </button>
      </div>

      <span className="absolute left-3 top-3 rounded-full bg-background/70 px-2 py-0.5 text-2xs backdrop-blur">
        Before
      </span>
      <span className="absolute right-3 top-3 rounded-full bg-primary/80 px-2 py-0.5 text-2xs text-white backdrop-blur">
        After
      </span>
    </div>
  );
}

function Layer({ src, variant }: { src?: string; variant: "before" | "after" }) {
  if (src) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={variant} className="absolute inset-0 size-full object-cover" />;
  }
  return (
    <div
      className={cn(
        "absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground",
        variant === "before"
          ? "bg-gradient-to-br from-secondary to-muted"
          : "bg-gradient-to-br from-primary/25 via-accent/15 to-muted",
      )}
    >
      {variant === "before" ? <User className="size-10" /> : <Shirt className="size-10" />}
      <span className="text-xs">{variant === "before" ? "Your photo" : "Styled"}</span>
    </div>
  );
}
