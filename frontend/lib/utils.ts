import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge conditional class names, resolving Tailwind conflicts. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Generate a short, URL-safe session id (no external dependency). */
export function createSessionId(): string {
  const rand = Math.random().toString(36).slice(2, 10);
  const time = Date.now().toString(36);
  return `sess_${time}${rand}`;
}

/** Title-case a snake_case or kebab-case token, e.g. "dark_circle" → "Dark Circle". */
export function humanize(token: string): string {
  return token
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

/** Clamp a number into an inclusive range. */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/** Map a common color name to a CSS color for swatches; falls back to the name. */
export function colorToCss(name: string): string {
  const key = name.trim().toLowerCase();
  return NAMED_COLORS[key] ?? key;
}

const NAMED_COLORS: Record<string, string> = {
  olive: "#808000",
  terracotta: "#e2725b",
  mustard: "#e1ad01",
  cream: "#fffdd0",
  "forest green": "#228b22",
  emerald: "#50c878",
  cobalt: "#0047ab",
  ruby: "#e0115f",
  gold: "#d4af37",
  "rich plum": "#8e4585",
  "soft rose": "#e8b4b8",
  "powder blue": "#b0e0e6",
  lavender: "#b57edc",
  "cool grey": "#8c92ac",
  navy: "#1b1f3b",
  "dusty pink": "#d5a6bd",
  periwinkle: "#8f99fb",
  sage: "#9caf88",
  "slate blue": "#6a5acd",
  burgundy: "#800020",
  teal: "#008080",
  coral: "#ff7f50",
  "warm green": "#6b8e23",
  ivory: "#fffff0",
  "denim blue": "#1560bd",
  fuchsia: "#ff00ff",
  "true red": "#c1121f",
  white: "#f8f8ff",
};
