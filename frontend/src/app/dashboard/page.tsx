"use client";

import { useAppStore } from "@/store/app-store";
import { usePipelines, usePipelineHistory } from "@/hooks/use-pipelines";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Database,
  GitBranch,
  Activity,
  ArrowUpRight,
  TrendingUp,
  BrainCircuit,
  FileSpreadsheet,
} from "lucide-react";
import Link from "next/link";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Dashboard() {
  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasetsList = Object.values(datasetCache);
  
  const { data: pipelines, isLoading: pipelinesLoading } = usePipelines();
  const { data: history, isLoading: historyLoading } = usePipelineHistory();

  // Metrics calculations
  const totalDatasets = datasetsList.length;
  const avgQualityScore = totalDatasets
    ? Math.round(
        datasetsList.reduce((acc, curr) => acc + (curr.analysis?.quality?.quality_score || 0), 0) /
          totalDatasets
      )
    : 0;
  const totalPipelines = pipelines?.length || 0;
  const recentRuns = history?.slice(0, 5) || [];

  // Data for quality distribution chart
  const chartData = datasetsList.map((d) => ({
    name: d.filename.length > 15 ? d.filename.slice(0, 12) + "..." : d.filename,
    quality: d.analysis?.quality?.quality_score || 0,
  }));

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Enterprise Console</h1>
          <p className="text-sm text-muted-foreground">
            Overview of dataset quality, active pipelines, and system execution status.
          </p>
        </div>
        <Link href="/upload">
          <Button className="rounded-full bg-primary hover:bg-primary/95 text-primary-foreground">
            Upload New File
          </Button>
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Total Datasets
            </CardTitle>
            <Database className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold">{totalDatasets}</div>
            <p className="text-[10px] text-muted-foreground mt-1">Session & local storage cached</p>
          </CardContent>
        </Card>

        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Avg Quality Score
            </CardTitle>
            <TrendingUp className="h-5 w-5 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold">
              {avgQualityScore}%
            </div>
            <div className="flex items-center gap-1.5 mt-1 text-[10px] text-muted-foreground">
              <span>Overall completeness rating</span>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Active Pipelines
            </CardTitle>
            <GitBranch className="h-5 w-5 text-purple-500" />
          </CardHeader>
          <CardContent>
            {pipelinesLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-extrabold">{totalPipelines}</div>
            )}
            <p className="text-[10px] text-muted-foreground mt-1">Configured cleaning templates</p>
          </CardContent>
        </Card>

        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Execution Runs
            </CardTitle>
            <Activity className="h-5 w-5 text-orange-500" />
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-extrabold">{history?.length || 0}</div>
            )}
            <p className="text-[10px] text-muted-foreground mt-1">Total database audit executions</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Quality Chart */}
        <Card className="rounded-xl border border-border lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-bold">Dataset Quality Index</CardTitle>
            <CardDescription>Visual comparison of analysis scores.</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            {chartData.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-xs text-muted-foreground">
                <FileSpreadsheet className="h-10 w-10 text-muted-foreground/30 mb-2" />
                No datasets uploaded yet. Upload a CSV to view the quality index.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--background))",
                      borderColor: "hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="quality" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Recent uploads */}
        <Card className="rounded-xl border border-border">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-bold">Recent Uploads</CardTitle>
              <CardDescription>Click to explore details.</CardDescription>
            </div>
            <Link href="/datasets">
              <Button variant="ghost" size="icon">
                <ArrowUpRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="space-y-4">
            {datasetsList.length === 0 ? (
              <div className="text-center text-xs text-muted-foreground py-8">
                No recent uploads
              </div>
            ) : (
              datasetsList.slice(0, 5).map((d) => (
                <div
                  key={d.dataset_id}
                  className="flex items-center justify-between rounded-lg border border-border p-3 hover:bg-accent/40 transition"
                >
                  <div className="overflow-hidden pr-2">
                    <p className="text-xs font-semibold truncate">{d.filename}</p>
                    <p className="text-[10px] text-muted-foreground">
                      Rows: {d.analysis?.metadata?.rows}, Cols: {d.analysis?.metadata?.columns}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-primary">
                      {d.analysis?.quality?.quality_score}%
                    </span>
                    <Link href={`/datasets/${d.dataset_id}`}>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        Inspect
                      </Button>
                    </Link>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* History table */}
      <Card className="rounded-xl border border-border">
        <CardHeader>
          <CardTitle className="text-sm font-bold">Audit & Execution Timeline</CardTitle>
          <CardDescription>Audit results from recent pipeline executions.</CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : recentRuns.length === 0 ? (
            <div className="text-center text-xs text-muted-foreground py-8">
              No executions logged. Go to Pipeline Builder to execute transformations.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground font-semibold">
                    <th className="py-2">Run ID</th>
                    <th className="py-2">Pipeline Name</th>
                    <th className="py-2">Dataset ID</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Rows Affected</th>
                    <th className="py-2">Completed At</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRuns.map((run) => (
                    <tr key={run.run_id} className="border-b border-border hover:bg-accent/10 transition">
                      <td className="py-3 font-mono font-bold text-muted-foreground">{run.run_id.slice(0, 8)}</td>
                      <td className="py-3 font-semibold">AI Generated Pipeline</td>
                      <td className="py-3 font-mono text-muted-foreground">{run.dataset_id.slice(0, 8)}</td>
                      <td className="py-3">
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            run.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-500"
                              : "bg-destructive/10 text-destructive"
                          }`}
                        >
                          {run.status}
                        </span>
                      </td>
                      <td className="py-3">
                        {run.rows_before} → {run.rows_after}
                      </td>
                      <td className="py-3 text-muted-foreground">
                        {new Date(run.started_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
