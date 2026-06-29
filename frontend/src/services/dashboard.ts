import { api } from "./api";

export const dashboardService = {
  generate: async (datasetId: string): Promise<any> => {
    const response = await api.post("/datasets/dashboard", {
      dataset_id: datasetId,
    });
    return response.data;
  },

  get: async (datasetId: string): Promise<any> => {
    const response = await api.get(`/datasets/dashboard/${datasetId}`);
    return response.data;
  },

  regenerate: async (datasetId: string): Promise<any> => {
    const response = await api.post(`/datasets/dashboard/${datasetId}/generate`);
    return response.data;
  },
};
