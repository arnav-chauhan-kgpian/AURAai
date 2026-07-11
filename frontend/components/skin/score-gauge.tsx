"use client";

import { motion } from "framer-motion";

import { AnimatedNumber } from "@/components/skin/animated-number";
import { humanize } from "@/lib/utils";

/** Higher scores mean a more pronounced concern → warmer color. */
function severityColor(score: number): string {
  if (score >= 65) return "hsl(0 72% 55%)";
  if (score >= 45) return "hsl(38 92% 55%)";
  if (score >= 25) return "hsl(48 90% 52%)";
  return "hsl(142 65% 47%)";
}

export function ScoreGauge({
  concern,
  score,
  size = 108,
}: {
  concern: string;
  score: number;
  size?: number;
}) {
  const stroke = 9;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = severityColor(score);
  const offset = circumference * (1 - Math.min(score, 100) / 100);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth={stroke}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold tabular-nums">
            <AnimatedNumber value={Math.round(score)} />
          </span>
          <span className="text-2xs text-muted-foreground">/ 100</span>
        </div>
      </div>
      <span className="text-center text-xs font-medium text-muted-foreground">
        {humanize(concern)}
      </span>
    </div>
  );
}
