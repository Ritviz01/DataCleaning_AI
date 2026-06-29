import { api } from "./api";
import { Pipeline, PipelineRun, PipelineStep } from "../types";

export const pipelineService = {
  create: async (name: string, description?: string, datasetId?: string, stopOnError: boolean = true): Promise<{ pipeline_id: string; name: string }> => {
    const response = await api.post("/pipeline/create", {
      name,
      description,
      dataset_id: datasetId,
      stop_on_error: stopOnError,
    });
    return response.data;
  },

  addStep: async (pipelineId: string, transformation: string, params: Record<string, any>, order?: number): Promise<{ step_id: string; order: number }> => {
    const response = await api.post("/pipeline/add-step", {
      pipeline_id: pipelineId,
      transformation,
      params,
      order,
    });
    return response.data;
  },

  removeStep: async (pipelineId: string, stepId: string): Promise<any> => {
    const response = await api.post("/pipeline/remove-step", {
      pipeline_id: pipelineId,
      step_id: stepId,
    });
    return response.data;
  },

  reorder: async (pipelineId: string, steps: { step_id: string; order: number }[]): Promise<any> => {
    const response = await api.post("/pipeline/reorder", {
      pipeline_id: pipelineId,
      steps,
    });
    return response.data;
  },

  list: async (): Promise<Pipeline[]> => {
    const response = await api.get("/pipeline/list");
    return response.data;
  },

  get: async (id: string): Promise<Pipeline> => {
    const response = await api.get(`/pipeline/${id}`);
    return response.data;
  },

  validate: async (pipelineId: string, datasetId: string): Promise<{ is_valid: boolean; errors: any[]; warnings: any[] }> => {
    const response = await api.post("/pipeline/validate", {
      pipeline_id: pipelineId,
      dataset_id: datasetId,
    });
    return response.data;
  },

  preview: async (pipelineId: string, datasetId: string): Promise<any> => {
    const response = await api.post("/pipeline/preview", {
      pipeline_id: pipelineId,
      dataset_id: datasetId,
    });
    return response.data;
  },

  run: async (pipelineId: string, datasetId: string): Promise<PipelineRun> => {
    const response = await api.post("/pipeline/run", {
      pipeline_id: pipelineId,
      dataset_id: datasetId,
    });
    return response.data;
  },

  history: async (pipelineId?: string, datasetId?: string): Promise<PipelineRun[]> => {
    const params: Record<string, string> = {};
    if (pipelineId) params.pipeline_id = pipelineId;
    if (datasetId) params.dataset_id = datasetId;
    const response = await api.get("/pipeline/history", { params });
    return response.data;
  },

  applyTemplate: async (pipelineId: string, templateName: string, datasetId?: string): Promise<any> => {
    const response = await api.post("/pipeline/template/apply", {
      pipeline_id: pipelineId,
      template_name: templateName,
      dataset_id: datasetId,
    });
    return response.data;
  },

  export: async (format: string, pipelineId?: string, runId?: string): Promise<any> => {
    const response = await api.post("/pipeline/export", {
      format,
      pipeline_id: pipelineId,
      run_id: runId,
    });
    return response.data;
  },
};
