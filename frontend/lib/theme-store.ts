/**
 * Theme state (Zustand) with localStorage persistence.
 *
 * A dependency-free dark/light theme controller. Dark is the default so the
 * product looks intentional on first paint; the choice persists across visits
 * and is applied by toggling the `dark` class on <html>.
 */
import { create } from "zustand";

export type Theme = "light" | "dark";

const STORAGE_KEY = "aura-theme";

function applyTheme(theme: Theme): void {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("dark", theme === "dark");
  document.documentElement.style.colorScheme = theme;
}

function readStoredTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "light" || stored === "dark" ? stored : "dark";
}

interface ThemeState {
  theme: Theme;
  hydrate: () => void;
  setTheme: (theme: Theme) => void;
  toggle: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: "dark",
  hydrate: () => {
    const theme = readStoredTheme();
    applyTheme(theme);
    set({ theme });
  },
  setTheme: (theme) => {
    applyTheme(theme);
    if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, theme);
    set({ theme });
  },
  toggle: () => get().setTheme(get().theme === "dark" ? "light" : "dark"),
}));
