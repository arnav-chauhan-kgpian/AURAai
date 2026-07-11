"use client";

import { motion } from "framer-motion";

/** Three-dot "thinking" indicator shown before the first streamed token. */
export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 py-1" aria-label="Assistant is typing" role="status">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="size-2 rounded-full bg-muted-foreground/70"
          animate={{ y: [0, -4, 0], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1, repeat: Infinity, delay: i * 0.15 }}
        />
      ))}
    </div>
  );
}
