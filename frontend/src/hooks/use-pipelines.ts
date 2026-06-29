import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { pipelineService } from "../services/pipelines";
import { useAppStore } from "../store/app-store";

export const usePipelines = () => {
  return useQuery({
    queryKey: ["pipelines"],
    queryFn: () => pipelineService.list(),
  });
};

export const usePipeline = (pipelineId: string) => {
  return useQuery({
    queryKey: ["pipeline", pipelineId],
    queryFn: () => pipelineService.get(pipelineId),
    enabled: !!pipelineId,
  });
};

export const usePipelineHistory = (pipelineId?: string, datasetId?: string) => {
  return useQuery({
    queryKey: ["pipeline-history", pipelineId, datasetId],
    queryFn: () => pipelineService.history(pipelineId, datasetId),
  });
};

export const useCreatePipelineMutation = () => {
  const queryClient = useQueryClient();
  const addNotification = useAppStore((state) => state.addNotification);

  return useMutation({
    mutationFn: (data: { name: string; description?: string; datasetId?: string }) =>
      pipelineService.create(data.name, data.description, data.datasetId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["pipelines"] });
      addNotification({
        type: "success",
        title: "Pipeline Created",
        message: `Pipeline "${data.name}" created successfully.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: "error",
        title: "Creation Failed",
        message: error.response?.data?.detail || "Could not create pipeline.",
      });
    },
  });
};

export const useRunPipelineMutation = () => {
  const queryClient = useQueryClient();
  const addNotification = useAppStore((state) => state.addNotification);

  return useMutation({
    mutationFn: (data: { pipelineId: string; datasetId: string }) =>
      pipelineService.run(data.pipelineId, data.datasetId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-history"] });
      addNotification({
        type: "success",
        title: "Pipeline Execution Succeeded",
        message: `Status: ${data.status}. Rows before: ${data.rows_before}, after: ${data.rows_after}`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: "error",
        title: "Execution Failed",
        message: error.response?.data?.detail || "An error occurred during pipeline execution.",
      });
    },
  });
};
