/**
 * Global session state (Zustand).
 *
 * Holds the conversation, the live timeline phases, and the latest structured
 * results for a session. The streaming hook drives these; the dashboard's three
 * panels (conversation, timeline, results) all read from here so they stay in
 * sync without prop drilling.
 */
import { create } from "zustand";

import type { TimelinePhaseId } from "@/lib/constants";
import { createSessionId } from "@/lib/utils";
import type {
  ColorPalette,
  Intent,
  RecommendationSet,
  SkinAnalysisResponse,
  TryOnResponse,
} from "@/types/api";

export type PhaseStatus = "pending" | "active" | "complete";

export interface TimelinePhase {
  id: TimelinePhaseId;
  status: PhaseStatus;
}

export interface UiMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
  hasImage?: boolean;
}

export interface SessionResults {
  intent: Intent | null;
  skin: SkinAnalysisResponse | null;
  palette: ColorPalette | null;
  tryOn: TryOnResponse | null;
  recommendations: RecommendationSet | null;
}

const EMPTY_RESULTS: SessionResults = {
  intent: null,
  skin: null,
  palette: null,
  tryOn: null,
  recommendations: null,
};

interface SessionState {
  sessionId: string;
  status: "idle" | "streaming";
  messages: UiMessage[];
  phases: TimelinePhase[];
  results: SessionResults;

  newSession: () => void;
  clearConversation: () => void;
  setStatus: (status: SessionState["status"]) => void;
  setSessionId: (id: string) => void;

  addUserMessage: (content: string, hasImage?: boolean) => void;
  startAssistantMessage: () => string;
  appendToken: (id: string, token: string) => void;
  finishAssistantMessage: (id: string, content?: string) => void;

  setPhases: (phases: TimelinePhase[]) => void;
  patchPhase: (id: TimelinePhaseId, status: PhaseStatus) => void;

  setResults: (results: Partial<SessionResults>) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: createSessionId(),
  status: "idle",
  messages: [],
  phases: [],
  results: { ...EMPTY_RESULTS },

  newSession: () =>
    set({
      sessionId: createSessionId(),
      status: "idle",
      messages: [],
      phases: [],
      results: { ...EMPTY_RESULTS },
    }),

  clearConversation: () =>
    set({ messages: [], phases: [], results: { ...EMPTY_RESULTS }, status: "idle" }),

  setStatus: (status) => set({ status }),

  // Adopt the server-issued session id so subsequent turns reuse the same
  // conversation (fixes cross-turn memory).
  setSessionId: (id) => set({ sessionId: id }),

  addUserMessage: (content, hasImage) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: `u_${state.messages.length}_${Date.now()}`, role: "user", content, hasImage },
      ],
    })),

  startAssistantMessage: () => {
    const id = `a_${Date.now()}`;
    set((state) => ({
      messages: [...state.messages, { id, role: "assistant", content: "", streaming: true }],
    }));
    return id;
  },

  appendToken: (id, token) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + token } : m,
      ),
    })),

  finishAssistantMessage: (id, content) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, streaming: false, content: content ?? m.content } : m,
      ),
    })),

  setPhases: (phases) => set({ phases }),

  patchPhase: (id, status) =>
    set((state) => ({
      phases: state.phases.map((p) => (p.id === id ? { ...p, status } : p)),
    })),

  setResults: (results) => set((state) => ({ results: { ...state.results, ...results } })),
}));
