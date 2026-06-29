import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { copilotService } from "../services/copilot";
import { useCopilotStore } from "../store/copilot-store";
import { useAppStore } from "../store/app-store";

export const useCopilotHistory = (sessionId?: string) => {
  return useQuery({
    queryKey: ["copilot-history", sessionId],
    queryFn: () => copilotService.history(sessionId),
    enabled: !!sessionId,
  });
};

export const useCopilotGenerateMutation = () => {
  const addMessage = useCopilotStore((state) => state.addMessage);
  const addNotification = useAppStore((state) => state.addNotification);

  return useMutation({
    mutationFn: (data: { datasetId: string; prompt: string; sessionId?: string }) =>
      copilotService.generate(data.datasetId, data.prompt, data.sessionId),
    onSuccess: (data, variables) => {
      // Add response message to copilot chat store
      addMessage({
        sender: "assistant",
        text: data.pipeline?.description || `Generated a pipeline with ${data.pipeline?.steps?.length || 0} steps.`,
        pipeline: data.pipeline,
        validation: data.validation,
        preview: data.preview,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: "error",
        title: "Copilot Generation Failed",
        message: error.response?.data?.detail || "AI failed to generate a pipeline. Please check your credentials.",
      });
      addMessage({
        sender: "assistant",
        text: `Error: ${error.response?.data?.detail || "I encountered an issue generating your pipeline. Please verify the backend settings or OpenAI key config."}`,
      });
    },
  });
};
