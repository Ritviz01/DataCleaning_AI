import { create } from "zustand";
import { persist } from "zustand/middleware";
import { DatasetDetailsResponse } from "../types";

interface Notification {
  id: string;
  type: "success" | "error" | "info" | "warning";
  title: string;
  message: string;
  timestamp: string;
}

interface Settings {
  openaiKeyStatus: "configured" | "not_configured";
  geminiKeyStatus: "configured" | "not_configured";
  llmProvider: "openai" | "gemini";
}

interface AppState {
  theme: "light" | "dark";
  selectedDatasetId: string | null;
  datasetCache: Record<string, DatasetDetailsResponse>;
  notifications: Notification[];
  settings: Settings;
  
  setTheme: (theme: "light" | "dark") => void;
  setSelectedDatasetId: (id: string | null) => void;
  cacheDataset: (id: string, data: DatasetDetailsResponse) => void;
  addNotification: (notification: Omit<Notification, "id" | "timestamp">) => void;
  clearNotifications: () => void;
  updateSettings: (settings: Partial<Settings>) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: "dark",
      selectedDatasetId: null,
      datasetCache: {},
      notifications: [],
      settings: {
        openaiKeyStatus: "not_configured",
        geminiKeyStatus: "not_configured",
        llmProvider: "openai",
      },

      setTheme: (theme) => set({ theme }),
      setSelectedDatasetId: (selectedDatasetId) => set({ selectedDatasetId }),
      cacheDataset: (id, data) =>
        set((state) => ({
          datasetCache: { ...state.datasetCache, [id]: data },
        })),
      addNotification: (notif) =>
        set((state) => {
          const newNotif: Notification = {
            ...notif,
            id: Math.random().toString(36).substring(7),
            timestamp: new Date().toISOString(),
          };
          return {
            notifications: [newNotif, ...state.notifications].slice(0, 50), // keep last 50
          };
        }),
      clearNotifications: () => set({ notifications: [] }),
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
    }),
    {
      name: "dataclean-app-store",
      partialize: (state) => ({
        theme: state.theme,
        selectedDatasetId: state.selectedDatasetId,
        settings: state.settings,
      }),
    }
  )
);
