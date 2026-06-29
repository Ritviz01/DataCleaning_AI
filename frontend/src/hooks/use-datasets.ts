import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { datasetService } from "../services/datasets";
import { useAppStore } from "../store/app-store";

export const useDatasetMutation = () => {
  const queryClient = useQueryClient();
  const cacheDataset = useAppStore((state) => state.cacheDataset);
  const addNotification = useAppStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (file: File) => {
      return await datasetService.analyze(file);
    },
    onSuccess: (data) => {
      cacheDataset(data.dataset_id, data);
      queryClient.setQueryData(["dataset", data.dataset_id], data);
      addNotification({
        type: "success",
        title: "Upload Successful",
        message: `Dataset "${data.filename}" has been uploaded and analyzed.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: "error",
        title: "Upload Failed",
        message: error.response?.data?.detail || "An error occurred during dataset analysis.",
      });
    },
  });
};

export const useCleanDatasetMutation = () => {
  const addNotification = useAppStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (file: File) => {
      return await datasetService.clean(file);
    },
    onSuccess: (data) => {
      addNotification({
        type: "success",
        title: "Cleaning Complete",
        message: `Processed dataset. Cleaned file exported as ${data.export.filename}.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: "error",
        title: "Cleaning Failed",
        message: error.response?.data?.detail || "An error occurred during cleaning.",
      });
    },
  });
};
