/**
 * Demo Mode state (Zustand) with localStorage persistence.
 *
 * A runtime toggle (independent of the build-time `NEXT_PUBLIC_USE_MOCK` env
 * var) that serves curated demo users instead of calling the backend — ideal
 * for a reliable, offline-safe live demo. Initialised from the env var so
 * `NEXT_PUBLIC_USE_MOCK=true` turns it on by default.
 */
import { create } from "zustand";

import { env } from "@/lib/env";
import type { DemoUser } from "@/lib/demo-users";

const STORAGE_KEY = "aura-demo";

interface Persisted {
  enabled: boolean;
  userId: DemoUser["id"];
}

function read(): Persisted {
  const fallback: Persisted = { enabled: env.useMock, userId: "A" };
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? { ...fallback, ...(JSON.parse(raw) as Persisted) } : fallback;
  } catch {
    return fallback;
  }
}

interface DemoState extends Persisted {
  hydrated: boolean;
  hydrate: () => void;
  setEnabled: (enabled: boolean) => void;
  setUser: (userId: DemoUser["id"]) => void;
}

function persist(state: Persisted): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export const useDemoStore = create<DemoState>((set, get) => ({
  enabled: env.useMock,
  userId: "A",
  hydrated: false,
  hydrate: () => set({ ...read(), hydrated: true }),
  setEnabled: (enabled) => {
    persist({ enabled, userId: get().userId });
    set({ enabled });
  },
  setUser: (userId) => {
    persist({ enabled: get().enabled, userId });
    set({ userId });
  },
}));
