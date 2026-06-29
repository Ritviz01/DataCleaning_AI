"use client";

import { usePipelines, useCreatePipelineMutation } from "@/hooks/use-pipelines";
import { useAppStore } from "@/store/app-store";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { GitBranch, Plus, Calendar, ArrowRight, Activity, Settings } from "lucide-react";
import Link from "next/link";

export default function PipelinesList() {
  const { data: pipelines, isLoading } = usePipelines();
  const createMutation = useCreatePipelineMutation();
  
  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasets = Object.values(datasetCache);

  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [targetDataset, setTargetDataset] = useState("");
  const [open, setOpen] = useState(false);

  const handleCreate = () => {
    if (!name.trim()) return;
    createMutation.mutate(
      {
        name,
        description: desc || undefined,
        datasetId: targetDataset || undefined,
      },
      {
        onSuccess: () => {
          setName("");
          setDesc("");
          setTargetDataset("");
          setOpen(false);
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Data Pipelines</h1>
          <p className="text-sm text-muted-foreground">
            Configure reusable transformation steps, reorder, and execute clean pipelines on datasets.
          </p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger render={
            <Button className="rounded-full gap-1">
              <Plus className="h-4 w-4" />
              New Pipeline
            </Button>
          } />
          <DialogContent className="max-w-sm rounded-xl">
            <DialogHeader>
              <DialogTitle className="text-sm font-bold">Create Transformation Pipeline</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-muted-foreground">Pipeline Name</label>
                <Input
                  placeholder="E.g., Customer ML Prep"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="rounded-lg h-9"
                />
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-muted-foreground">Description (Optional)</label>
                <Input
                  placeholder="E.g., Removes null values and formats headers"
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                  className="rounded-lg h-9"
                />
              </div>
              <div className="space-y-1 flex flex-col">
                <label className="font-semibold text-muted-foreground mb-1">Target Dataset (Optional)</label>
                <select
                  value={targetDataset}
                  onChange={(e) => setTargetDataset(e.target.value)}
                  className="rounded-lg border border-border p-2 bg-background font-semibold"
                >
                  <option value="">None — General Pipeline</option>
                  {datasets.map((d) => (
                    <option key={d.dataset_id} value={d.dataset_id}>
                      {d.filename}
                    </option>
                  ))}
                </select>
              </div>
              <Button
                onClick={handleCreate}
                disabled={!name.trim() || createMutation.isPending}
                className="w-full rounded-lg"
              >
                Create
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Pipelines grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="h-40 rounded-xl animate-pulse bg-accent/20" />
          <Card className="h-40 rounded-xl animate-pulse bg-accent/20" />
        </div>
      ) : !pipelines || pipelines.length === 0 ? (
        <Card className="rounded-xl border border-border p-12 text-center text-xs text-muted-foreground">
          <GitBranch className="h-12 w-12 mx-auto text-muted-foreground/30 mb-2" />
          No pipelines configured yet. Click 'New Pipeline' to build a workflow.
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {pipelines.map((p) => (
            <Card
              key={p.pipeline_id}
              className="rounded-xl border border-border bg-card hover:border-primary/50 transition flex flex-col justify-between"
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <GitBranch className="h-5 w-5 text-primary" />
                  <Badge variant="secondary" className="rounded-full text-[9px] uppercase font-bold">
                    Active
                  </Badge>
                </div>
                <CardTitle className="text-sm font-bold pt-2">{p.name}</CardTitle>
                <CardDescription className="text-xs truncate">{p.description || "No description provided."}</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 border-t border-border mt-4 flex items-center justify-between text-[10px] text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  {p.created_at ? new Date(p.created_at).toLocaleDateString() : "N/A"}
                </span>
                <Link href={`/pipelines/${p.pipeline_id}`}>
                  <Button size="sm" variant="ghost" className="h-8 gap-1 pr-1 font-bold text-xs text-primary hover:text-primary/90">
                    Open Builder
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
