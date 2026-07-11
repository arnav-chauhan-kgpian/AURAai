/**
 * Onboarding state (Zustand) with localStorage persistence.
 *
 * Tracks whether the first-launch walkthrough has been completed so it shows
 * exactly once. `open` is resolved on hydrate to avoid a flash before we know.
 */
import { create } from "zustand";

const STORAGE_KEY = "aura-onboarded";

interface OnboardingState {
  open: boolean;
  hydrated: boolean;
  hydrate: () => void;
  complete: () => void;
  reopen: () => void;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  open: false,
  hydrated: false,
  hydrate: () => {
    if (typeof window === "undefined") return;
    const done = window.localStorage.getItem(STORAGE_KEY) === "1";
    set({ open: !done, hydrated: true });
  },
  complete: () => {
    if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, "1");
    set({ open: false });
  },
  reopen: () => set({ open: true }),
}));
