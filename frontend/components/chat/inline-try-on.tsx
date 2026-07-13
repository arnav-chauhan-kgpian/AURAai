"use client";

import { motion } from "framer-motion";
import { Download, Expand, Shirt } from "lucide-react";
import { useState } from "react";

import { Dialog } from "@/components/ui/dialog";
import { useSessionStore } from "@/lib/store";

/**
 * Renders the latest virtual try-on image inline in the chat, so the result is
 * visible immediately (not only in the dashboard Results panel).
 */
export function InlineTryOn() {
  const tryOn = useSessionStore((s) => s.results.tryOn);
  const status = useSessionStore((s) => s.status);
  const [fullscreen, setFullscreen] = useState(false);

  const src = tryOn?.output_images.find(Boolean);
  if (!src || status === "streaming") return null;

  const download = () => {
    const a = document.createElement("a");
    a.href = src;
    a.download = "aura-tryon.jpg";
    a.click();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="flex gap-3"
    >
      <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-xl bg-brand shadow-glow">
        <Shirt className="size-4 text-white" />
      </span>
      <div className="min-w-0 max-w-[85%]">
        <div className="mb-1.5 text-xs font-medium text-muted-foreground">Your virtual try-on</div>
        <div className="group relative overflow-hidden rounded-2xl border border-border">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={src} alt="Virtual try-on result" className="max-h-80 w-auto object-contain" />
          <div className="absolute right-2 top-2 flex gap-1.5 opacity-0 transition-opacity group-hover:opacity-100">
            <button
              type="button"
              onClick={() => setFullscreen(true)}
              aria-label="Fullscreen"
              className="grid size-8 place-items-center rounded-full bg-background/80 backdrop-blur transition-colors hover:bg-background focus-visible:ring-focus"
            >
              <Expand className="size-4" />
            </button>
            <button
              type="button"
              onClick={download}
              aria-label="Download image"
              className="grid size-8 place-items-center rounded-full bg-background/80 backdrop-blur transition-colors hover:bg-background focus-visible:ring-focus"
            >
              <Download className="size-4" />
            </button>
          </div>
        </div>
      </div>

      <Dialog open={fullscreen} onClose={() => setFullscreen(false)} label="Try-on" className="max-w-lg">
        <div className="p-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={src} alt="Virtual try-on result" className="w-full rounded-xl" />
        </div>
      </Dialog>
    </motion.div>
  );
}
