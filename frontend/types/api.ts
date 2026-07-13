/**
 * API contract types — a faithful mirror of the backend's wire format.
 *
 * The FastAPI backend serialises Pydantic models with snake_case field names, so
 * these interfaces use snake_case to match the JSON exactly (no runtime mapping).
 */

// --- Skin analysis ---------------------------------------------------------

export interface SkinScore {
  concern: string;
  raw_score: number;
  ui_score: number;
}

export interface OverlayImage {
  concern: string;
  url: string;
}

export interface SkinAnalysisResponse {
  task_id: string;
  scores: SkinScore[];
  overlays: OverlayImage[];
  raw?: Record<string, unknown>;
}

// --- Virtual try-on --------------------------------------------------------

export interface TryOnResponse {
  task_id: string;
  output_images: string[];
  raw?: Record<string, unknown>;
}

// --- Color -----------------------------------------------------------------

export interface ColorPalette {
  fitzpatrick_type: string;
  undertone: string;
  season: string;
  recommended_colors: string[];
  avoid_colors: string[];
  rationale: string;
}

// --- Recommendations -------------------------------------------------------

export interface ProductRecommendation {
  title: string;
  category: string;
  rationale: string;
  url?: string | null;
}

export interface RecommendationSet {
  summary: string;
  skincare: ProductRecommendation[];
  outfit: ProductRecommendation[];
  colors: string[];
  shopping: ProductRecommendation[];
}

// --- Chat ------------------------------------------------------------------

export type Intent =
  | "SKIN_ONLY"
  | "TRYON_ONLY"
  | "STYLE_ONLY"
  | "SKIN_AND_STYLE"
  | "CHAT_ONLY"
  | "UNKNOWN";

export interface ChatResponse {
  session_id: string;
  reply: string;
  intent: Intent;
  tools_used: string[];
  steps: string[];
  recommendations: RecommendationSet | null;
  skin_analysis: SkinAnalysisResponse | null;
  try_on: TryOnResponse | null;
  color_palette: ColorPalette | null;
}

// --- Streaming events (SSE from POST /chat/stream) -------------------------

export type StreamEventType = "intent" | "step" | "tool" | "token" | "final" | "error";

export interface StreamEvent {
  type: StreamEventType;
  data: Record<string, unknown>;
}

export interface ChatRequestInput {
  session_id: string;
  message: string;
  face_image?: File | null;
  garment_image?: File | null;
  garment_category?: string;
}
