import { create } from "zustand";
import { persist } from "zustand/middleware";
import { CopilotTurn } from "../types";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  pipeline?: any;
  validation?: any;
  preview?: any;
}

interface CopilotState {
  sessionId: string;
  messages: ChatMessage[];
  pendingPrompt: string | null;
  historyTurns: CopilotTurn[];
  
  initializeSession: () => void;
  addMessage: (message: Omit<ChatMessage, "id" | "timestamp">) => void;
  setPendingPrompt: (prompt: string | null) => void;
  clearChat: () => void;
  setHistoryTurns: (turns: CopilotTurn[]) => void;
}

export const useCopilotStore = create<CopilotState>()(
  persist(
    (set) => ({
      sessionId: "",
      messages: [],
      pendingPrompt: null,
      historyTurns: [],

      initializeSession: () => {
        set((state) => {
          if (state.sessionId) return {};
          return {
            sessionId: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15),
            messages: [
              {
                id: "welcome",
                sender: "assistant",
                text: "Hello! I am your AI Data Copilot. Type any command like 'Deduplicate and normalize scores' or 'Prepare my data for ML' to begin building your clean data pipeline.",
                timestamp: new Date().toISOString(),
              },
            ],
          };
        });
      },
      addMessage: (msg) =>
        set((state) => {
          const newMsg: ChatMessage = {
            ...msg,
            id: Math.random().toString(36).substring(7),
            timestamp: new Date().toISOString(),
          };
          return {
            messages: [...state.messages, newMsg],
          };
        }),
      setPendingPrompt: (pendingPrompt) => set({ pendingPrompt }),
      clearChat: () =>
        set((state) => ({
          messages: [
            {
              id: "welcome",
              sender: "assistant",
              text: "Chat cleared. What can I do for you next?",
              timestamp: new Date().toISOString(),
            },
          ],
        })),
      setHistoryTurns: (historyTurns) => set({ historyTurns }),
    }),
    {
      name: "dataclean-copilot-store",
    }
  )
);
