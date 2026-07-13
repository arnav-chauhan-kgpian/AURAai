/**
 * Aura Score — the product's signature moment.
 *
 * A single, reassuring 0–100 number synthesised from everything the agent found:
 * skin health, color harmony, and styling completeness. It is computed purely on
 * the client from results already returned, so it is instant, always available,
 * and needs no extra backend call — a memorable, demo-safe hero metric.
 */
import { clamp } from "@/lib/utils";
import type { SessionResults } from "@/lib/store";
import type { SkinScore } from "@/types/api";

/**
 * A 0–100 skin-health number for a single scan (higher = healthier), the same
 * inverse-severity basis the Aura Score uses. Shared by the progress-over-time
 * chart so a scan's dot matches the hero metric.
 */
export function skinHealthFromScores(scores: SkinScore[]): number {
  if (scores.length === 0) return 0;
  const avg = scores.reduce((sum, s) => sum + s.ui_score, 0) / scores.length;
  return Math.round(clamp(100 - avg * 0.9, 20, 99));
}

export interface AuraScore {
  overall: number;
  skin: number;
  color: number;
  style: number;
  insight: string;
  available: boolean;
}

export function computeAuraScore(results: SessionResults): AuraScore {
  const parts: { value: number; weight: number }[] = [];

  // Skin health: the inverse of average concern severity (higher = healthier).
  let skin = 0;
  if (results.skin && results.skin.scores.length > 0) {
    const avg =
      results.skin.scores.reduce((sum, s) => sum + s.ui_score, 0) / results.skin.scores.length;
    skin = Math.round(clamp(100 - avg * 0.9, 20, 99));
    parts.push({ value: skin, weight: 0.45 });
  }

  // Color harmony: a well-matched palette with clear recommendations scores high.
  let color = 0;
  if (results.palette) {
    color = Math.round(clamp(72 + results.palette.recommended_colors.length * 3, 0, 96));
    parts.push({ value: color, weight: 0.25 });
  }

  // Style completeness: depth of recommendations plus a rendered try-on.
  let style = 0;
  if (results.recommendations || results.tryOn) {
    const recs = results.recommendations;
    const depth = recs ? recs.skincare.length + recs.outfit.length + recs.shopping.length : 0;
    style = Math.round(clamp(52 + depth * 5 + (results.tryOn ? 16 : 0), 0, 98));
    parts.push({ value: style, weight: 0.3 });
  }

  const available = parts.length > 0;
  const totalWeight = parts.reduce((sum, p) => sum + p.weight, 0) || 1;
  const overall = available
    ? Math.round(parts.reduce((sum, p) => sum + p.value * p.weight, 0) / totalWeight)
    : 0;

  return { overall, skin, color, style, insight: insightFor(overall, skin, color), available };
}

function insightFor(overall: number, skin: number, color: number): string {
  if (overall >= 85) return "Radiant — your routine and palette are working in harmony.";
  if (overall >= 70) return "Strong foundation with a couple of easy wins ahead.";
  if (skin > 0 && skin < 60) return "A gentle, targeted routine will lift this quickly.";
  if (color > 0) return "Your colors are dialed in — a few tweaks and you're set.";
  return "A great starting point — let's build from here.";
}
