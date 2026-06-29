import { api } from "./api";
import { CopilotHistory } from "../types";

export const copilotService = {
  generate: async (datasetId: string, prompt: string, sessionId?: string): Promise<any> => {
    const response = await api.post("/copilot/generate", {
      dataset_id: datasetId,
      prompt,
      session_id: sessionId,
    });
    return response.data;
  },

  preview: async (datasetId: string, pipelineData: Record<string, any>): Promise<any> => {
    const response = await api.post("/copilot/preview", {
      dataset_id: datasetId,
      pipeline_data: pipelineData,
    });
    return response.data;
  },

  run: async (datasetId: string, pipelineData: Record<string, any>): Promise<any> => {
    const response = await api.post("/copilot/run", {
      dataset_id: datasetId,
      pipeline_data: pipelineData,
    });
    return response.data;
  },

  history: async (sessionId?: string): Promise<CopilotHistory> => {
    const params: Record<string, string> = {};
    if (sessionId) params.session_id = sessionId;
    const response = await api.get("/copilot/history", { params });
    return response.data;
  },
};
