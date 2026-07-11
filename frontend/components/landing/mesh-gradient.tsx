"use client";

import { motion } from "framer-motion";

/** Animated mesh-gradient backdrop: soft, drifting color blobs behind the hero. */
export function MeshGradient() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden" aria-hidden>
      <div className="absolute inset-0 bg-background" />
      <Blob className="left-[8%] top-[6%] size-[38rem] bg-[hsl(263_90%_60%/0.35)]" delay={0} />
      <Blob className="right-[4%] top-[2%] size-[32rem] bg-[hsl(292_84%_60%/0.28)]" delay={2} />
      <Blob className="bottom-[-8%] left-[30%] size-[40rem] bg-[hsl(245_90%_62%/0.30)]" delay={4} />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/30 to-background" />
      <div
        className="absolute inset-0 opacity-[0.15] mix-blend-soft-light"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}

function Blob({ className, delay }: { className: string; delay: number }) {
  return (
    <motion.div
      className={`absolute rounded-full blur-[100px] ${className}`}
      animate={{
        x: [0, 40, -30, 0],
        y: [0, -30, 20, 0],
        scale: [1, 1.1, 0.95, 1],
      }}
      transition={{ duration: 18, delay, repeat: Infinity, ease: "easeInOut" }}
    />
  );
}
