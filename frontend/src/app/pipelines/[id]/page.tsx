"use client";

import { usePipeline, useRunPipelineMutation, usePipelines } from "@/hooks/use-pipelines";
import { useAppStore } from "@/store/app-store";
import { pipelineService as pService } from "@/services/pipelines";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  GitBranch,
  Play,
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  Plus,
  Trash2,
  ChevronUp,
  ChevronDown,
  Sparkles,
  RefreshCcw,
} from "lucide-react";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";

export default function PipelineBuilder() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const pipelineId = params.id as string;
  
  const { data: pipeline, isLoading } = usePipeline(pipelineId);
  const runMutation = useRunPipelineMutation();

  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasets = Object.values(datasetCache);
  const addNotification = useAppStore((state) => state.addNotification);

  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  
  // Validation / Preview state
  const [valResults, setValResults] = useState<{ is_valid: boolean; errors: any[]; warnings: any[] } | null>(null);
  const [previewResults, setPreviewResults] = useState<any | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  // Add Step state
  const [addOpen, setAddOpen] = useState(false);
  const [transKey, setTransKey] = useState("remove_duplicates");
  const [paramStr, setParamStr] = useState("{}");

  const templates = [
    "General Data Cleaning",
    "Machine Learning Prep",
    "Power BI Reporter",
    "Financial Auditing",
    "Healthcare Patient Records",
  ];

  const handleAddStep = async () => {
    try {
      const parsedParams = JSON.parse(paramStr);
      await pService.addStep(pipelineId, transKey, parsedParams);
      queryClient.invalidateQueries({ queryKey: ["pipeline", pipelineId] });
      setAddOpen(false);
      setParamStr("{}");
      setValResults(null);
      setPreviewResults(null);
      addNotification({
        type: "success",
        title: "Step Added",
        message: `Added transformation '${transKey}' to pipeline.`,
      });
    } catch (e: any) {
      alert("Invalid JSON parameters: " + e.message);
    }
  };

  const handleRemoveStep = async (stepId: string) => {
    await pService.removeStep(pipelineId, stepId);
    queryClient.invalidateQueries({ queryKey: ["pipeline", pipelineId] });
    setValResults(null);
    setPreviewResults(null);
  };

  const handleMove = async (index: number, direction: "up" | "down") => {
    if (!pipeline?.steps) return;
    const steps = [...pipeline.steps];
    const targetIndex = direction === "up" ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= steps.length) return;
    
    // Swap order property
    const temp = steps[index].order;
    steps[index].order = steps[targetIndex].order;
    steps[targetIndex].order = temp;

    const payload = steps.map((s) => ({
      step_id: s.step_id!,
      order: s.order,
    }));

    await pService.reorder(pipelineId, payload);
    queryClient.invalidateQueries({ queryKey: ["pipeline", pipelineId] });
    setValResults(null);
    setPreviewResults(null);
  };

  const handleValidate = async () => {
    if (!selectedDatasetId) {
      alert("Please select a dataset to validate against.");
      return;
    }
    setIsChecking(true);
    try {
      const res = await pService.validate(pipelineId, selectedDatasetId);
      setValResults(res);
    } catch (e: any) {
      addNotification({
        type: "error",
        title: "Validation Failed",
        message: e.response?.data?.detail || "Could not validate pipeline.",
      });
    } finally {
      setIsChecking(false);
    }
  };

  const handlePreview = async () => {
    if (!selectedDatasetId) {
      alert("Please select a dataset to preview against.");
      return;
    }
    setIsChecking(true);
    try {
      const res = await pService.preview(pipelineId, selectedDatasetId);
      setPreviewResults(res);
    } catch (e: any) {
      addNotification({
        type: "error",
        title: "Preview Failed",
        message: e.response?.data?.detail || "Could not generate execution preview.",
      });
    } finally {
      setIsChecking(false);
    }
  };

  const handleApplyTemplate = async (template: string) => {
    try {
      await pService.applyTemplate(pipelineId, template, selectedDatasetId || undefined);
      queryClient.invalidateQueries({ queryKey: ["pipeline", pipelineId] });
      setValResults(null);
      setPreviewResults(null);
      addNotification({
        type: "success",
        title: "Template Applied",
        message: `Successfully applied pipeline template '${template}'.`,
      });
    } catch (e: any) {
      alert("Failed to apply template: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleExecute = () => {
    if (!selectedDatasetId) return;
    runMutation.mutate({
      pipelineId,
      datasetId: selectedDatasetId,
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <RefreshCcw className="h-8 w-8 text-primary animate-spin" />
        <p className="text-xs text-muted-foreground">Loading pipeline editor...</p>
      </div>
    );
  }

  if (!pipeline) return <div>Pipeline not found.</div>;

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link href="/pipelines">
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full border border-border bg-background">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-lg font-bold tracking-tight">{pipeline.name}</h1>
            <p className="text-xs text-muted-foreground">{pipeline.description}</p>
          </div>
        </div>

        {/* Dataset picker for preview / validation context */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
            className="text-xs rounded-lg border border-border p-2 bg-background font-semibold"
          >
            <option value="">Select context dataset...</option>
            {datasets.map((d) => (
              <option key={d.dataset_id} value={d.dataset_id}>
                {d.filename}
              </option>
            ))}
          </select>

          <Button
            size="sm"
            variant="outline"
            disabled={!selectedDatasetId || isChecking}
            onClick={handleValidate}
            className="h-9 text-xs"
          >
            Validate
          </Button>

          <Button
            size="sm"
            variant="outline"
            disabled={!selectedDatasetId || isChecking}
            onClick={handlePreview}
            className="h-9 text-xs"
          >
            Preview Diff
          </Button>

          <Button
            size="sm"
            disabled={!selectedDatasetId || runMutation.isPending}
            onClick={handleExecute}
            className="h-9 text-xs rounded-full gap-1"
          >
            <Play className="h-3 w-3" />
            Run Pipeline
          </Button>
        </div>
      </div>

      {/* Main split grid */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Steps sequence */}
        <Card className="rounded-xl border border-border bg-card md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-bold">Steps Sequence</CardTitle>
              <CardDescription>Drag or shift operations sequentially.</CardDescription>
            </div>
            
            <div className="flex gap-2">
              {/* Template applier */}
              <select
                onChange={(e) => {
                  if (e.target.value) handleApplyTemplate(e.target.value);
                  e.target.value = "";
                }}
                className="text-xs rounded-lg border border-border p-1.5 bg-background font-semibold"
              >
                <option value="">Apply preset template...</option>
                {templates.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>

              <Dialog open={addOpen} onOpenChange={setAddOpen}>
                <DialogTrigger render={
                  <Button size="sm" className="rounded-full gap-1 text-xs">
                    <Plus className="h-3.5 w-3.5" />
                    Add Step
                  </Button>
                } />
                <DialogContent className="max-w-sm rounded-xl">
                  <DialogHeader>
                    <DialogTitle className="text-sm font-bold">Add Transformation Step</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4 text-xs">
                    <div className="space-y-1 flex flex-col">
                      <label className="font-semibold text-muted-foreground mb-1">Transformation Key</label>
                      <select
                        value={transKey}
                        onChange={(e) => setTransKey(e.target.value)}
                        className="rounded-lg border border-border p-2 bg-background font-semibold"
                      >
                        <option value="remove_duplicates">remove_duplicates</option>
                        <option value="fill_missing">fill_missing</option>
                        <option value="drop_column">drop_column</option>
                        <option value="rename_column">rename_column</option>
                        <option value="convert_type">convert_type</option>
                        <option value="remove_outliers">remove_outliers</option>
                        <option value="normalize">normalize</option>
                        <option value="encode_categories">encode_categories</option>
                        <option value="standardize_text">standardize_text</option>
                        <option value="trim_whitespace">trim_whitespace</option>
                        <option value="lowercase">lowercase</option>
                        <option value="uppercase">uppercase</option>
                        <option value="replace_values">replace_values</option>
                        <option value="split_column">split_column</option>
                        <option value="merge_columns">merge_columns</option>
                        <option value="feature_engineering">feature_engineering</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="font-semibold text-muted-foreground">Parameters (JSON string)</label>
                      <Textarea
                        placeholder='{"column": "score", "method": "cap"}'
                        value={paramStr}
                        onChange={(e) => setParamStr(e.target.value)}
                        className="font-mono text-xs h-24 rounded-lg"
                      />
                    </div>

                    <Button onClick={handleAddStep} className="w-full rounded-lg">
                      Add
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 relative">
            {(!pipeline.steps || pipeline.steps.length === 0) ? (
              <div className="text-center text-xs text-muted-foreground py-16">
                No transformation steps defined. Click 'Add Step' to add operations.
              </div>
            ) : (
              pipeline.steps.map((step, idx) => (
                <div key={step.step_id} className="flex items-center justify-between border border-border rounded-xl p-4 bg-background hover:border-primary/45 transition">
                  <div className="space-y-1 pr-4">
                    <div className="flex items-center gap-2">
                      <span className="h-5 w-5 bg-primary/10 text-primary font-bold text-[10px] rounded-full flex items-center justify-center">
                        {step.order}
                      </span>
                      <p className="text-xs font-bold font-mono">{step.transformation}</p>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono">
                      Params: {JSON.stringify(step.params)}
                    </p>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-lg"
                      disabled={idx === 0}
                      onClick={() => handleMove(idx, "up")}
                    >
                      <ChevronUp className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-lg"
                      disabled={idx === pipeline.steps!.length - 1}
                      onClick={() => handleMove(idx, "down")}
                    >
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10 hover:text-destructive"
                      onClick={() => handleRemoveStep(step.step_id!)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Validation / Preview reports */}
        <div className="space-y-6">
          {/* Validation card */}
          {valResults && (
            <Card className="rounded-xl border border-border bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                  {valResults.is_valid ? (
                    <CheckCircle className="h-4 w-4 text-emerald-500" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                  )}
                  Validation Results
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-2">
                <p className="font-semibold">
                  Status: {valResults.is_valid ? "Ready to run" : "Errors found"}
                </p>
                {valResults.errors.length > 0 && (
                  <div className="space-y-1 text-destructive font-mono text-[10px]">
                    {valResults.errors.map((e, idx) => (
                      <p key={idx}>• Step {e.step_index || "?"}: {e.message}</p>
                    ))}
                  </div>
                )}
                {valResults.warnings.length > 0 && (
                  <div className="space-y-1 text-orange-500 font-mono text-[10px]">
                    {valResults.warnings.map((w, idx) => (
                      <p key={idx}>• {w.message}</p>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Preview card */}
          {previewResults && (
            <Card className="rounded-xl border border-border bg-card">
              <CardHeader>
                <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Execution Preview
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-2">
                <div className="flex justify-between border-b border-border pb-1">
                  <span className="text-muted-foreground">Original Row Count:</span>
                  <span className="font-bold">{previewResults.original_rows}</span>
                </div>
                <div className="flex justify-between border-b border-border pb-1">
                  <span className="text-muted-foreground">Transformed Row Count:</span>
                  <span className="font-bold">{previewResults.transformed_rows}</span>
                </div>
                <div className="flex justify-between border-b border-border pb-1">
                  <span className="text-muted-foreground">Rows Changed:</span>
                  <span className="font-bold text-primary">{previewResults.changed_rows}</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
