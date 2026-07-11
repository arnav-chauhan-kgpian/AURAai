"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

import { AnimatedNumber } from "@/components/skin/animated-number";
import { Card } from "@/components/ui/card";
import { computeAuraScore } from "@/lib/aura-score";
import { useSessionStore } from "@/lib/store";

export function AuraScoreCard() {
  const results = useSessionStore((s) => s.results);
  const score = computeAuraScore(results);
  if (!score.available) return null;

  const size = 132;
  const stroke = 11;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score.overall / 100);

  return (
    <Card className="relative overflow-hidden border-primary/25">
      <div className="absolute inset-0 -z-10 bg-brand opacity-[0.08]" aria-hidden />
      <div className="absolute -right-10 -top-10 -z-10 size-40 rounded-full bg-brand opacity-20 blur-3xl" aria-hidden />
      <div className="flex items-center gap-6 p-6">
        <div className="relative shrink-0" style={{ width: size, height: size }}>
          <svg width={size} height={size} className="-rotate-90">
            <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="hsl(var(--muted))" strokeWidth={stroke} />
            <defs>
              <linearGradient id="aura-grad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="hsl(var(--brand-1))" />
                <stop offset="55%" stopColor="hsl(var(--brand-2))" />
                <stop offset="100%" stopColor="hsl(var(--brand-3))" />
              </linearGradient>
            </defs>
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="url(#aura-grad)"
              strokeWidth={stroke}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-semibold tabular-nums">
              <AnimatedNumber value={score.overall} duration={1.4} />
            </span>
            <span className="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
              Aura Score
            </span>
          </div>
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 text-sm font-semibold">
            <Sparkles className="size-4 text-primary" />
            Your Aura Score
          </div>
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{score.insight}</p>
          <div className="mt-4 space-y-2.5">
            <Meter label="Skin health" value={score.skin} />
            <Meter label="Color harmony" value={score.color} />
            <Meter label="Style match" value={score.style} />
          </div>
        </div>
      </div>
    </Card>
  );
}

function Meter({ label, value }: { label: string; value: number }) {
  if (value === 0) return null;
  return (
    <div className="flex items-center gap-3">
      <span className="w-24 shrink-0 text-xs text-muted-foreground">{label}</span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
        <motion.div
          className="h-full rounded-full bg-brand"
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <span className="w-8 shrink-0 text-right text-xs font-medium tabular-nums">{value}</span>
    </div>
  );
}
