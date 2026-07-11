import { Badge } from "@/components/ui/badge";
import { humanize } from "@/lib/utils";
import type { SkinScore } from "@/types/api";

function variantFor(score: number): "success" | "warning" | "danger" {
  if (score >= 60) return "danger";
  if (score >= 40) return "warning";
  return "success";
}

export function ConcernBadge({ score }: { score: SkinScore }) {
  return (
    <Badge variant={variantFor(score.ui_score)} className="gap-1.5">
      {humanize(score.concern)}
      <span className="tabular-nums opacity-70">{Math.round(score.ui_score)}</span>
    </Badge>
  );
}
