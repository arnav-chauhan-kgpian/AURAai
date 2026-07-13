/** App-wide constants: navigation, timeline phase model, tool labels. */

import type { LucideIcon } from "lucide-react";
import {
  CheckCircle2,
  Palette,
  ScanFace,
  Shirt,
  Sparkles,
  Upload,
} from "lucide-react";

export const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/chat", label: "Chat" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/history", label: "History" },
  { href: "/settings", label: "Settings" },
] as const;

export type TimelinePhaseId =
  | "upload"
  | "skin_analysis"
  | "color_palette"
  | "planning"
  | "recommendation"
  | "virtual_try_on"
  | "done";

export interface TimelinePhaseMeta {
  id: TimelinePhaseId;
  label: string;
  icon: LucideIcon;
}

/** Canonical ordered timeline phases and their display labels. */
export const TIMELINE_PHASES: TimelinePhaseMeta[] = [
  { id: "upload", label: "Uploading selfie", icon: Upload },
  { id: "planning", label: "Planning", icon: Sparkles },
  { id: "skin_analysis", label: "Running skin analysis", icon: ScanFace },
  { id: "color_palette", label: "Analyzing skin tone", icon: Palette },
  { id: "recommendation", label: "Generating recommendations", icon: Sparkles },
  { id: "virtual_try_on", label: "Running virtual try-on", icon: Shirt },
  { id: "done", label: "Done", icon: CheckCircle2 },
];

/** Map a backend tool name to its timeline phase id. */
export const TOOL_TO_PHASE: Record<string, TimelinePhaseId> = {
  skin_analysis: "skin_analysis",
  color_palette: "color_palette",
  recommendation: "recommendation",
  virtual_try_on: "virtual_try_on",
};

export const TOOL_LABELS: Record<string, string> = {
  skin_analysis: "Skin Analysis",
  color_palette: "Color Palette",
  recommendation: "Recommendations",
  virtual_try_on: "Virtual Try-On",
};

export const INTENT_LABELS: Record<string, string> = {
  SKIN_ONLY: "Skin",
  TRYON_ONLY: "Try-On",
  STYLE_ONLY: "Style",
  SKIN_AND_STYLE: "Skin & Style",
  CHAT_ONLY: "Chat",
  UNKNOWN: "Exploring",
};
