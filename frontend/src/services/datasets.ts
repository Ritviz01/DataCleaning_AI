import { api } from "./api";
import { DatasetDetailsResponse } from "../types";

export const datasetService = {
  analyze: async (file: File): Promise<DatasetDetailsResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/datasets/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  clean: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/datasets/clean", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  aiInsights: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/datasets/ai-insights", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
};
