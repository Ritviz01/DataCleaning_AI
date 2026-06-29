"use client";

import { usePipelineHistory } from "@/hooks/use-pipelines";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { History, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";

export default function AuditLogsPage() {
  const { data: history, isLoading, refetch } = usePipelineHistory();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">System Audit Trail</h1>
          <p className="text-sm text-muted-foreground">
            Historical trace logs of all transformation pipelines run against uploaded datasets.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-xs text-muted-foreground hover:bg-accent transition"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh Audit
        </button>
      </div>

      <Card className="rounded-xl border border-border bg-card">
        <CardHeader>
          <CardTitle className="text-sm font-bold flex items-center gap-1.5">
            <History className="h-4 w-4 text-primary" />
            Activity Log Stream
          </CardTitle>
          <CardDescription>Immutable execution timeline.</CardDescription>
        </CardHeader>
        <CardContent className="relative pl-6 sm:pl-8 border-l border-border ml-4 space-y-6 py-4">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-16 w-full rounded-xl bg-accent/20" />
              <Skeleton className="h-16 w-full rounded-xl bg-accent/20" />
            </div>
          ) : !history || history.length === 0 ? (
            <div className="text-center text-xs text-muted-foreground py-8 pr-4">
              No audit records stored yet.
            </div>
          ) : (
            history.map((run) => (
              <div key={run.run_id} className="relative space-y-2">
                {/* Timeline dot */}
                <div className={`absolute -left-[30px] sm:-left-[38px] top-1 h-4 w-4 rounded-full border-4 border-card flex items-center justify-center ${
                  run.status === "completed" ? "bg-emerald-500" : "bg-destructive"
                }`} />

                <Card className="rounded-xl border border-border p-4 bg-background hover:border-primary/25 transition">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-border pb-2">
                    <div>
                      <p className="text-xs font-bold text-foreground">
                        Pipeline Executed: AI Generated Pipeline
                      </p>
                      <p className="text-[10px] text-muted-foreground font-mono">Run ID: {run.run_id}</p>
                    </div>
                    <Badge
                      variant="secondary"
                      className={`rounded-full text-[9px] uppercase font-bold ${
                        run.status === "completed"
                          ? "bg-emerald-500/10 text-emerald-500"
                          : "bg-destructive/10 text-destructive"
                      }`}
                    >
                      {run.status}
                    </Badge>
                  </div>

                  <div className="pt-2 grid grid-cols-2 sm:grid-cols-3 gap-4 text-[11px] text-muted-foreground">
                    <div>
                      <span className="font-semibold text-foreground block">Target Dataset</span>
                      <span className="font-mono">{run.dataset_id.slice(0, 10)}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-foreground block">Dimensions Shift</span>
                      <span>
                        {run.rows_before || "—"} → {run.rows_after || "—"} rows
                      </span>
                    </div>
                    <div className="col-span-2 sm:col-span-1">
                      <span className="font-semibold text-foreground block">Executed Timestamp</span>
                      <span>{new Date(run.started_at).toLocaleString()}</span>
                    </div>
                  </div>

                  {run.error_message && (
                    <div className="mt-3 p-2 bg-destructive/10 border border-destructive/20 rounded-lg text-[10px] text-destructive flex items-center gap-1.5 font-mono">
                      <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                      <span>{run.error_message}</span>
                    </div>
                  )}
                </Card>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
