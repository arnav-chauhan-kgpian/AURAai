/**
 * Realistic mock data and a simulated event stream.
 *
 * Used when `NEXT_PUBLIC_USE_MOCK=true` or when the backend is unreachable, so
 * the full experience — streaming timeline, results cards — can be demonstrated
 * offline. The shapes match the real API exactly.
 */
import type { ChatRequestInput, ChatResponse, StreamEvent } from "@/types/api";

export const MOCK_CHAT_RESPONSE: ChatResponse = {
  session_id: "sess_demo",
  intent: "SKIN_AND_STYLE",
  tools_used: ["skin_analysis", "color_palette", "recommendation", "virtual_try_on"],
  steps: [
    "intent:SKIN_AND_STYLE",
    "skin_analysis:ok",
    "color_palette:ok",
    "recommendation:ok",
    "virtual_try_on:ok",
    "summarized",
  ],
  reply:
    "Your skin reads **combination**, with elevated **acne (70)** and **oiliness (58)** around the T-zone — so the goal is to calm breakouts without stripping moisture.\n\nFor color, your warm undertone lands you in an **Autumn** palette. Lean into olive, terracotta and mustard; skip icy pastels.\n\n**Try this**\n- A gentle BHA cleanser morning and night\n- Oil-free, non-comedogenic moisturiser + daily SPF\n- The olive overshirt below pairs beautifully with your palette\n\nHere's how that jacket looks on you 👇",
  skin_analysis: {
    task_id: "skin_demo",
    scores: [
      { concern: "acne", raw_score: 72, ui_score: 70 },
      { concern: "oiliness", raw_score: 61, ui_score: 58 },
      { concern: "pore", raw_score: 55, ui_score: 52 },
      { concern: "redness", raw_score: 41, ui_score: 39 },
      { concern: "wrinkle", raw_score: 22, ui_score: 20 },
      { concern: "moisture", raw_score: 48, ui_score: 46 },
    ],
    overlays: [
      { concern: "acne", url: "" },
      { concern: "pore", url: "" },
    ],
  },
  color_palette: {
    fitzpatrick_type: "IV",
    undertone: "warm",
    season: "Autumn",
    recommended_colors: ["olive", "terracotta", "mustard", "cream", "forest green"],
    avoid_colors: ["icy pastel", "cool grey"],
    rationale: "Warm olive skin glows in earthy, warm autumnal tones.",
  },
  try_on: {
    task_id: "vto_demo",
    output_images: [""],
  },
  recommendations: {
    summary: "A calm-the-breakouts routine paired with warm autumn styling.",
    skincare: [
      {
        title: "Salicylic acid (BHA) cleanser",
        category: "cleanser",
        rationale: "Clears pores and reduces oil without over-drying.",
      },
      {
        title: "Oil-free gel moisturiser",
        category: "moisturiser",
        rationale: "Hydrates the barrier while staying non-comedogenic.",
      },
      {
        title: "Broad-spectrum SPF 50",
        category: "sunscreen",
        rationale: "Protects post-BHA skin and prevents dark marks.",
      },
    ],
    outfit: [
      {
        title: "Olive merino overshirt",
        category: "top",
        rationale: "Warm olive echoes your autumn palette.",
      },
      {
        title: "Cream straight-leg trousers",
        category: "bottom",
        rationale: "Soft neutral balances the saturated top.",
      },
    ],
    colors: ["olive", "terracotta", "mustard", "cream"],
    shopping: [
      {
        title: "Charcoal merino crewneck",
        category: "knitwear",
        rationale: "A versatile layer that flatters warm undertones.",
      },
    ],
  },
};

const REPLY_TOKENS = MOCK_CHAT_RESPONSE.reply.split(/(\s+)/);

/** Yield a lifelike sequence of stream events for a turn. */
export async function* mockStream(input: ChatRequestInput): AsyncGenerator<StreamEvent> {
  const hasGarment = Boolean(input.garment_image);
  const tools = hasGarment
    ? MOCK_CHAT_RESPONSE.tools_used
    : MOCK_CHAT_RESPONSE.tools_used.filter((t) => t !== "virtual_try_on");

  await wait(500);
  yield { type: "intent", data: { intent: MOCK_CHAT_RESPONSE.intent, rationale: "Skin concern + styling ask." } };

  await wait(700);
  yield { type: "step", data: { tools } };

  for (const token of REPLY_TOKENS) {
    await wait(18);
    yield { type: "token", data: { token } };
  }

  await wait(200);
  yield {
    type: "final",
    data: {
      ...MOCK_CHAT_RESPONSE,
      session_id: input.session_id,
      tools_used: tools,
      try_on: hasGarment ? MOCK_CHAT_RESPONSE.try_on : null,
    },
  };
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
