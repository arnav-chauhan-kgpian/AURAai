"use client";

import { animate, useMotionValue } from "framer-motion";
import { useEffect, useState } from "react";

/** Counts up to `value` on mount / when the value changes. */
export function AnimatedNumber({
  value,
  duration = 1.1,
  className,
}: {
  value: number;
  duration?: number;
  className?: string;
}) {
  const motionValue = useMotionValue(0);
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const controls = animate(motionValue, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [value, duration, motionValue]);

  return <span className={className}>{display}</span>;
}
