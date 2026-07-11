"use client";

import { motion, useReducedMotion } from "framer-motion";

/**
 * Route transition wrapper. Next.js re-mounts `template.tsx` on every
 * navigation, so this gives each page a soft, consistent entrance without any
 * jarring layout shift. Reduced-motion users get a plain fade.
 */
export default function Template({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      initial={reduce ? { opacity: 0 } : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}
