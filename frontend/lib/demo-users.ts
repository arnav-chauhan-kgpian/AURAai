/**
 * Demo users — realistic, backend-schema-accurate outputs for a reliable demo.
 *
 * Used by Demo Mode (a runtime toggle) and as the automatic fallback when the
 * YouCam pipeline is unreachable, so a live demo never dead-ends. Each dataset
 * matches {@link ChatResponse} exactly.
 */
import { MOCK_CHAT_RESPONSE } from "@/lib/mock";
import type { ChatRequestInput, ChatResponse, StreamEvent } from "@/types/api";

export interface DemoUser {
  id: "A" | "B" | "C";
  name: string;
  tagline: string;
  traits: string[];
  response: ChatResponse;
}

/** User A — Acne · oily · warm undertone · casual (the canonical mock). */
const USER_A: ChatResponse = { ...MOCK_CHAT_RESPONSE, session_id: "demo_A" };

/** User B — Dry skin · neutral tone · business attire. */
const USER_B: ChatResponse = {
  session_id: "demo_B",
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
    "Your skin reads **dry**, with a low moisture score (dehydration **66**) and some early fine lines around the eyes — the priority is rebuilding the barrier.\n\nYour undertone is **neutral**, which opens up a versatile **Spring** palette. For business attire, teal, denim-blue and ivory read sharp and approachable.\n\n**Try this**\n- A hydrating hyaluronic-acid serum under a richer moisturiser\n- A gentle, non-foaming cleanser\n- The navy blazer below anchors a clean, professional look\n\nHere's the blazer on you 👇",
  skin_analysis: {
    task_id: "demo_skin_B",
    scores: [
      { concern: "moisture", raw_score: 68, ui_score: 66 },
      { concern: "wrinkle", raw_score: 34, ui_score: 32 },
      { concern: "radiance", raw_score: 44, ui_score: 42 },
      { concern: "redness", raw_score: 28, ui_score: 26 },
      { concern: "pore", raw_score: 24, ui_score: 22 },
      { concern: "oiliness", raw_score: 16, ui_score: 15 },
    ],
    overlays: [{ concern: "moisture", url: "" }],
  },
  color_palette: {
    fitzpatrick_type: "III",
    undertone: "neutral",
    season: "Spring",
    recommended_colors: ["teal", "denim blue", "ivory", "coral", "warm green"],
    avoid_colors: ["washed-out pastels", "muddy brown"],
    rationale: "Neutral medium skin carries clean, clear colors especially well.",
  },
  try_on: { task_id: "demo_vto_B", output_images: [""] },
  recommendations: {
    summary: "A barrier-rebuilding routine paired with sharp business-neutral styling.",
    skincare: [
      { title: "Hyaluronic-acid hydrating serum", category: "serum", rationale: "Draws water into dehydrated skin." },
      { title: "Ceramide-rich moisturiser", category: "moisturiser", rationale: "Rebuilds and seals the barrier." },
      { title: "Non-foaming cream cleanser", category: "cleanser", rationale: "Cleanses without stripping natural oils." },
    ],
    outfit: [
      { title: "Navy wool blazer", category: "layer", rationale: "A neutral anchor that reads professional." },
      { title: "Ivory poplin shirt", category: "top", rationale: "Clean contrast that flatters neutral undertones." },
      { title: "Charcoal tailored trousers", category: "bottom", rationale: "Balanced, sharp, versatile." },
    ],
    colors: ["teal", "denim blue", "ivory", "charcoal"],
    shopping: [{ title: "Denim-blue knit tie", category: "accessory", rationale: "A subtle nod to your spring palette." }],
  },
};

/** User C — Sensitive skin · cool undertone · evening wear. */
const USER_C: ChatResponse = {
  session_id: "demo_C",
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
    "Your skin reads **sensitive**, with elevated **redness (62)** and some under-eye shadowing — so we'll keep everything gentle and barrier-supporting.\n\nYour undertone is **cool**, placing you in a soft **Summer** palette. For evening wear, slate blue, dusty rose and burgundy look elegant against your skin.\n\n**Try this**\n- Fragrance-free, ceramide + niacinamide products only\n- Skip harsh exfoliants; add a calming moisturiser\n- The slate-blue evening look below neutralises redness beautifully\n\nHere's the look on you 👇",
  skin_analysis: {
    task_id: "demo_skin_C",
    scores: [
      { concern: "redness", raw_score: 64, ui_score: 62 },
      { concern: "dark_circle", raw_score: 48, ui_score: 46 },
      { concern: "moisture", raw_score: 42, ui_score: 40 },
      { concern: "radiance", raw_score: 40, ui_score: 38 },
      { concern: "pore", raw_score: 30, ui_score: 28 },
      { concern: "wrinkle", raw_score: 24, ui_score: 22 },
    ],
    overlays: [{ concern: "redness", url: "" }],
  },
  color_palette: {
    fitzpatrick_type: "II",
    undertone: "cool",
    season: "Summer",
    recommended_colors: ["dusty pink", "periwinkle", "slate blue", "burgundy", "sage"],
    avoid_colors: ["neon", "bright orange", "gold"],
    rationale: "Fair, cool skin is flattered by soft, cool-based hues over high-contrast brights.",
  },
  try_on: { task_id: "demo_vto_C", output_images: [""] },
  recommendations: {
    summary: "A calm-the-redness routine paired with cool-toned evening styling.",
    skincare: [
      { title: "Niacinamide + ceramide moisturiser", category: "moisturiser", rationale: "Calms redness and supports the barrier." },
      { title: "Fragrance-free gentle cleanser", category: "cleanser", rationale: "Avoids irritating sensitive skin." },
      { title: "Mineral SPF 30", category: "sunscreen", rationale: "Gentle, non-stinging daily protection." },
    ],
    outfit: [
      { title: "Slate-blue satin slip dress", category: "dress", rationale: "Cool tone that quiets facial redness." },
      { title: "Dusty-rose wrap", category: "layer", rationale: "Soft summer hue that complements your palette." },
    ],
    colors: ["slate blue", "dusty pink", "burgundy", "periwinkle"],
    shopping: [{ title: "Silver drop earrings", category: "accessory", rationale: "Cool metals suit cool undertones." }],
  },
};

export const DEMO_USERS: DemoUser[] = [
  {
    id: "A",
    name: "Maya",
    tagline: "Acne · oily · warm undertone",
    traits: ["Acne", "Oily skin", "Warm undertone", "Casual"],
    response: USER_A,
  },
  {
    id: "B",
    name: "Daniel",
    tagline: "Dry · neutral tone · business",
    traits: ["Dry skin", "Neutral tone", "Business attire"],
    response: USER_B,
  },
  {
    id: "C",
    name: "Priya",
    tagline: "Sensitive · cool undertone · evening",
    traits: ["Sensitive skin", "Cool undertone", "Evening wear"],
    response: USER_C,
  },
];

export function getDemoUser(id: DemoUser["id"]): DemoUser {
  return DEMO_USERS.find((user) => user.id === id) ?? DEMO_USERS[0];
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** Stream a demo user's response as lifelike SSE events. */
export async function* buildDemoStream(
  response: ChatResponse,
  input: ChatRequestInput,
  options: { includeTryOn?: boolean } = {},
): AsyncGenerator<StreamEvent> {
  const hasGarment = options.includeTryOn ?? Boolean(input.garment_image);
  const tools = hasGarment
    ? response.tools_used
    : response.tools_used.filter((t) => t !== "virtual_try_on");

  await wait(450);
  yield { type: "intent", data: { intent: response.intent, rationale: "Skin concern + styling ask." } };

  await wait(650);
  yield { type: "step", data: { tools } };

  for (const token of response.reply.split(/(\s+)/)) {
    await wait(16);
    yield { type: "token", data: { token } };
  }

  await wait(180);
  yield {
    type: "final",
    data: {
      ...response,
      session_id: input.session_id,
      tools_used: tools,
      try_on: hasGarment ? response.try_on : null,
    },
  };
}
