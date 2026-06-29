"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { useDatasetMutation, useCleanDatasetMutation } from "@/hooks/use-datasets";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { UploadCloud, File, AlertCircle, Sparkles, Settings, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<"analyze" | "clean">("analyze");
  
  const datasetMutation = useDatasetMutation();
  const cleanMutation = useCleanDatasetMutation();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
      "application/json": [".json"],
      "application/x-parquet": [".parquet"],
      "application/octet-stream": [".parquet"],
    },
  });

  const handleUpload = async () => {
    if (!file) return;

    if (uploadMode === "analyze") {
      datasetMutation.mutate(file, {
        onSuccess: (data) => {
          router.push(`/datasets/${data.dataset_id}`);
        },
      });
    } else {
      cleanMutation.mutate(file, {
        onSuccess: (data) => {
          router.push(`/datasets/${data.dataset_id}`);
        },
      });
    }
  };

  const isPending = datasetMutation.isPending || cleanMutation.isPending;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Ingest Dataset</h1>
        <p className="text-sm text-muted-foreground">
          Upload tabular datasets for quality inspections, cleansing operations, and dashboard insights.
        </p>
      </div>

      <Card className="rounded-xl border border-border shadow-sm">
        <CardHeader>
          <CardTitle className="text-sm font-bold flex items-center gap-1.5">
            <Settings className="h-4 w-4 text-primary" />
            Upload Settings
          </CardTitle>
          <CardDescription>Choose how the engine should process the upload.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Button
            variant={uploadMode === "analyze" ? "default" : "outline"}
            className="flex-1 rounded-lg py-6"
            onClick={() => setUploadMode("analyze")}
          >
            <div className="text-left">
              <p className="text-xs font-bold">Interactive Analysis</p>
              <p className="text-[10px] opacity-80 font-normal">Generate quality reports & open Copilot</p>
            </div>
          </Button>
          <Button
            variant={uploadMode === "clean" ? "default" : "outline"}
            className="flex-1 rounded-lg py-6"
            onClick={() => setUploadMode("clean")}
          >
            <div className="text-left">
              <p className="text-xs font-bold">Auto-Clean Copy</p>
              <p className="text-[10px] opacity-80 font-normal">Directly clean recommendations and download</p>
            </div>
          </Button>
        </CardContent>
      </Card>

      {/* Dropzone */}
      <Card className="rounded-xl border border-border bg-card">
        <CardContent className="p-6 space-y-6">
          <div
            {...getRootProps()}
            className={cn(
              "flex flex-col items-center justify-center border-2 border-dashed border-border rounded-xl p-12 transition text-center cursor-pointer hover:border-primary/50",
              isDragActive && "border-primary bg-primary/5",
              isPending && "pointer-events-none opacity-50"
            )}
          >
            <input {...getInputProps()} />
            <UploadCloud className="h-12 w-12 text-muted-foreground/50 mb-4 animate-bounce" />
            <p className="text-xs font-semibold">Drag & drop your dataset file here, or click to browse</p>
            <p className="text-[10px] text-muted-foreground mt-2">
              Supports CSV, Excel (XLSX, XLS), JSON, and Parquet up to 100MB
            </p>
          </div>

          {/* Selected File Details */}
          {file && (
            <div className="flex items-center justify-between rounded-lg border border-border p-3 bg-accent/20">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                  <File className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold">{file.name}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 rounded-lg"
                onClick={() => setFile(null)}
                disabled={isPending}
              >
                Clear
              </Button>
            </div>
          )}

          {/* Status Message / Progress */}
          {isPending && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1">
                  <Sparkles className="h-4 w-4 text-primary animate-spin" />
                  Running quality checks & structural profiling...
                </span>
              </div>
              <div className="h-1.5 w-full bg-accent rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full animate-progress-loading" />
              </div>
            </div>
          )}

          {/* Submit */}
          <Button
            size="lg"
            className="w-full rounded-full"
            disabled={!file || isPending}
            onClick={handleUpload}
          >
            {isPending ? "Processing..." : "Process Dataset"}
            <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
