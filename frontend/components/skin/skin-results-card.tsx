"use client";

import { ScanFace } from "lucide-react";

import { ConcernBadge } from "@/components/skin/concern-badge";
import { OverlayPreview } from "@/components/skin/overlay-preview";
import { ScoreGauge } from "@/components/skin/score-gauge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SkinAnalysisResponse } from "@/types/api";

export function SkinResultsCard({
  data,
  selfieUrl,
}: {
  data: SkinAnalysisResponse;
  selfieUrl?: string | null;
}) {
  const sorted = [...data.scores].sort((a, b) => b.ui_score - a.ui_score);
  const top = sorted.slice(0, 3);
  const rest = sorted.slice(3);

  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <span className="grid size-8 place-items-center rounded-lg bg-primary/15 text-primary">
          <ScanFace className="size-4" />
        </span>
        <CardTitle>Skin analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-3 gap-2">
          {top.map((score) => (
            <ScoreGauge key={score.concern} concern={score.concern} score={score.ui_score} />
          ))}
        </div>

        {rest.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {rest.map((score) => (
              <ConcernBadge key={score.concern} score={score} />
            ))}
          </div>
        )}

        <OverlayPreview overlays={data.overlays} imageUrl={selfieUrl ?? undefined} />
      </CardContent>
    </Card>
  );
}
