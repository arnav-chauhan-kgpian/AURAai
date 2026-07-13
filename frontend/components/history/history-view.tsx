"use client";

/**
 * History view — the user's saved journey.
 *
 * Reads the per-user records the backend persists after each turn: a skin-health
 * progress line over time (#17), a gallery of past virtual try-ons, and recent
 * recommendation snapshots. Everything is scoped to the signed-in user by the
 * backend; in demo/anonymous mode the API returns empty and we show a friendly
 * empty state.
 */
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Clock, ImageIcon, LineChart, Shirt, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchHistory } from "@/lib/api";
import { skinHealthFromScores } from "@/lib/aura-score";
import type { HistoryScan } from "@/types/api";

export function HistoryView() {
  const { data, isLoading } = useQuery({
    queryKey: ["history"],
    queryFn: fetchHistory,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="mx-auto grid max-w-4xl gap-4 p-4 sm:p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-56 w-full rounded-2xl" />
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
    );
  }

  const scans = data?.scans ?? [];
  const tryOns = data?.try_ons ?? [];
  const recommendations = data?.recommendations ?? [];
  const isEmpty = scans.length === 0 && tryOns.length === 0 && recommendations.length === 0;

  if (isEmpty) {
    return (
      <div className="mx-auto max-w-4xl p-4 sm:p-6">
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-6 p-4 sm:p-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Your history</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Skin progress, saved try-ons, and past recommendations — all in one place.
        </p>
      </header>

      {scans.length > 0 && <SkinProgress scans={scans} />}

      {tryOns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Shirt className="size-4 text-primary" /> Virtual try-ons
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {tryOns.flatMap((job) =>
                job.output_images.map((src, i) => (
                  <figure
                    key={`${job.id}-${i}`}
                    className="group relative aspect-[3/4] overflow-hidden rounded-xl border border-border bg-secondary"
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={src}
                      alt="Virtual try-on result"
                      className="size-full object-cover transition-transform group-hover:scale-105"
                      loading="lazy"
                    />
                    <figcaption className="absolute inset-x-0 bottom-0 flex items-center gap-1 bg-gradient-to-t from-black/70 to-transparent p-2 text-2xs text-white">
                      <Clock className="size-3" /> {formatDate(job.created_at)}
                    </figcaption>
                  </figure>
                )),
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="size-4 text-primary" /> Recent recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {recommendations.slice(0, 6).map((rec) => (
              <div key={rec.id} className="rounded-xl border border-border p-3">
                <p className="text-sm">{rec.payload.summary || "Personalised recommendation set"}</p>
                <p className="mt-1 flex items-center gap-1 text-2xs text-muted-foreground">
                  <Clock className="size-3" /> {formatDate(rec.created_at)}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/** A minimal SVG line chart of skin-health over time (oldest → newest). */
function SkinProgress({ scans }: { scans: HistoryScan[] }) {
  // Backend returns newest-first; reverse for a left-to-right timeline.
  const points = [...scans]
    .reverse()
    .map((s) => ({ value: skinHealthFromScores(s.scores), at: s.created_at }))
    .filter((p) => p.value > 0);

  if (points.length === 0) return null;

  const latest = points[points.length - 1].value;
  const first = points[0].value;
  const delta = latest - first;
  const w = 640;
  const h = 160;
  const pad = 16;
  const max = Math.max(...points.map((p) => p.value), 100);
  const min = Math.min(...points.map((p) => p.value), 0);
  const range = Math.max(max - min, 1);
  const x = (i: number) =>
    points.length === 1 ? w / 2 : pad + (i * (w - pad * 2)) / (points.length - 1);
  const y = (v: number) => pad + (1 - (v - min) / range) * (h - pad * 2);
  const path = points.map((p, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(p.value)}`).join(" ");
  const area = `${path} L ${x(points.length - 1)} ${h - pad} L ${x(0)} ${h - pad} Z`;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          <span className="flex items-center gap-2">
            <LineChart className="size-4 text-primary" /> Skin health over time
          </span>
          <span className="text-sm font-normal text-muted-foreground">
            {latest}
            <span className="ml-2">
              {delta === 0 ? (
                "steady"
              ) : (
                <span className={delta > 0 ? "text-emerald-500" : "text-amber-500"}>
                  {delta > 0 ? "▲" : "▼"} {Math.abs(delta)}
                </span>
              )}
            </span>
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label="Skin health trend">
          <defs>
            <linearGradient id="auraFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="currentColor" stopOpacity="0.25" />
              <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
            </linearGradient>
          </defs>
          <motion.path
            d={area}
            fill="url(#auraFill)"
            className="text-primary"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          />
          <motion.path
            d={path}
            fill="none"
            stroke="currentColor"
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-primary"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.9, ease: "easeInOut" }}
          />
          {points.map((p, i) => (
            <circle key={i} cx={x(i)} cy={y(p.value)} r={3.5} className="fill-primary" />
          ))}
        </svg>
        <p className="mt-1 text-2xs text-muted-foreground">
          {points.length} scan{points.length === 1 ? "" : "s"} · higher is healthier
        </p>
      </CardContent>
    </Card>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
      <div className="mb-4 grid size-14 place-items-center rounded-full bg-primary/10 text-primary">
        <ImageIcon className="size-6" />
      </div>
      <h2 className="text-lg font-semibold">No history yet</h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        Run a skin analysis or a virtual try-on in chat and it will be saved here — including a
        progress chart as you track your skin over time.
      </p>
    </div>
  );
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
