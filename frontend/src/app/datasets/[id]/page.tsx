"use client";

import { useAppStore } from "@/store/app-store";
import { useParams, useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileSpreadsheet,
  AlertTriangle,
  Sparkles,
  Layers,
  Settings,
  Bot,
  Activity,
  ArrowLeft,
  Download,
} from "lucide-react";
import Link from "next/link";

export default function DatasetDetails() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const datasetCache = useAppStore((state) => state.datasetCache);
  const data = datasetCache[id];

  if (!data) {
    return (
      <div className="flex h-96 flex-col items-center justify-center text-center space-y-4">
        <FileSpreadsheet className="h-12 w-12 text-muted-foreground/30 animate-pulse" />
        <h3 className="text-sm font-semibold">Dataset not loaded in current session</h3>
        <p className="text-xs text-muted-foreground max-w-xs">
          Please upload or inspect active files to build quality profiles.
        </p>
        <Link href="/upload">
          <Button size="sm" className="rounded-full">Go to Ingest</Button>
        </Link>
      </div>
    );
  }

  const analysis = data.analysis || {};
  const metadata = analysis.metadata || {};
  const schema = analysis.schema || [];
  const profile = analysis.profile || [];
  const issues = analysis.issues || [];
  const recommendations = analysis.recommendations || [];
  const score = analysis.quality?.quality_score || 0;
  const grade = analysis.quality?.grade || "N/A";

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link href="/datasets">
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full border border-border bg-background">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight">{data.filename}</h1>
              <Badge variant="outline" className="text-[10px] font-bold uppercase rounded-full">
                {data.dataset_type || "General"}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground font-mono">ID: {data.dataset_id}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Link href="/copilot">
            <Button size="sm" className="rounded-full gap-1.5 bg-primary hover:bg-primary/95 text-primary-foreground">
              <Bot className="h-4 w-4" />
              Open Copilot
            </Button>
          </Link>
          {data.export?.download_url && (
            <a href={`${process.env.NEXT_PUBLIC_API_URL}${data.export.download_url}`} download>
              <Button size="sm" variant="outline" className="rounded-full gap-1.5 border-border bg-background text-foreground">
                <Download className="h-4 w-4" />
                Download Export
              </Button>
            </a>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-background border border-border p-1 rounded-lg">
          <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
          <TabsTrigger value="schema" className="text-xs">Schema ({schema.length})</TabsTrigger>
          <TabsTrigger value="profile" className="text-xs">Profile</TabsTrigger>
          <TabsTrigger value="issues" className="text-xs">
            Issues
            {issues.length > 0 && (
              <Badge variant="destructive" className="ml-1.5 h-4 px-1 rounded-full text-[9px] font-extrabold">
                {issues.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="text-xs">Recommendations</TabsTrigger>
        </TabsList>

        {/* 1. Overview */}
        <TabsContent value="overview">
          <div className="grid gap-6 md:grid-cols-3">
            <Card className="rounded-xl border border-border bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Quality Index
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                <div className="relative flex items-center justify-center">
                  <span className="text-4xl font-black">{score}%</span>
                </div>
                <p className="text-xs font-semibold mt-2">Grade {grade}</p>
                <p className="text-[10px] text-muted-foreground mt-1">Based on completeness & types</p>
              </CardContent>
            </Card>

            <Card className="rounded-xl border border-border bg-card md:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Executive Summary
                </CardTitle>
                <CardDescription>AI generated quality highlights and domain recommendations.</CardDescription>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap max-h-60 overflow-y-auto">
                {data.executive_report || "No summary report was generated for this dataset."}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 2. Schema */}
        <TabsContent value="schema">
          <Card className="rounded-xl border border-border bg-card">
            <CardHeader>
              <CardTitle className="text-sm font-bold">Data Dictionary & Column Types</CardTitle>
              <CardDescription>System inferred columns and database typings.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground font-semibold">
                      <th className="py-2">Column Name</th>
                      <th className="py-2">Inferred Type</th>
                      <th className="py-2">Semantic Classifier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {schema.map((col: any) => (
                      <tr key={col.column_name} className="border-b border-border hover:bg-accent/10 transition">
                        <td className="py-3 font-semibold">{col.column_name}</td>
                        <td className="py-3 font-mono text-muted-foreground">{col.type}</td>
                        <td className="py-3">
                          <Badge variant="outline" className="rounded-full text-[10px]">
                            {col.semantic_type}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 3. Profile */}
        <TabsContent value="profile">
          <Card className="rounded-xl border border-border bg-card">
            <CardHeader>
              <CardTitle className="text-sm font-bold">Statistical Profiling</CardTitle>
              <CardDescription>Detailed statistical bounds calculated natively in Polars.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground font-semibold">
                      <th className="py-2">Column</th>
                      <th className="py-2">Nulls (%)</th>
                      <th className="py-2">Distinct Count</th>
                      <th className="py-2">Min Value</th>
                      <th className="py-2">Max Value</th>
                      <th className="py-2">Mean</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profile.map((p: any) => (
                      <tr key={p.column_name} className="border-b border-border hover:bg-accent/10 transition">
                        <td className="py-3 font-semibold">{p.column_name}</td>
                        <td className="py-3 text-muted-foreground">
                          {p.null_count} ({Math.round(p.null_percentage * 100)}%)
                        </td>
                        <td className="py-3">{p.unique_values}</td>
                        <td className="py-3 font-mono text-muted-foreground">{p.min !== undefined && p.min !== null ? String(p.min) : "—"}</td>
                        <td className="py-3 font-mono text-muted-foreground">{p.max !== undefined && p.max !== null ? String(p.max) : "—"}</td>
                        <td className="py-3 font-mono text-muted-foreground">
                          {p.mean !== undefined && p.mean !== null ? p.mean.toFixed(2) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 4. Issues */}
        <TabsContent value="issues">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {issues.length === 0 ? (
              <div className="col-span-full text-center py-12 text-muted-foreground text-xs">
                No quality issues detected. Quality score is perfect!
              </div>
            ) : (
              issues.map((issue: any, idx: number) => (
                <Card key={idx} className="rounded-xl border border-destructive/20 bg-card">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="destructive" className="rounded-full text-[9px] font-extrabold uppercase">
                        {issue.severity}
                      </Badge>
                      <AlertTriangle className="h-4 w-4 text-destructive" />
                    </div>
                    <CardTitle className="text-xs font-bold pt-2">
                      Column: {issue.column || "Dataset-wide"}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-xs font-semibold text-foreground">{issue.issue_type}</p>
                    <p className="text-[10px] text-muted-foreground">
                      Anomalous record count: {issue.count}
                    </p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* 5. Recommendations */}
        <TabsContent value="recommendations">
          <div className="space-y-4">
            {recommendations.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground text-xs">
                No recommendations available.
              </div>
            ) : (
              recommendations.map((rec: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-start justify-between rounded-lg border border-border p-4 hover:bg-accent/10 transition bg-background"
                >
                  <div className="space-y-1">
                    <p className="text-xs font-bold text-foreground">
                      Column: <span className="font-mono text-muted-foreground">{rec.column}</span>
                    </p>
                    <p className="text-xs text-foreground font-semibold">
                      Action: <Badge variant="secondary" className="rounded-full">{rec.recommended_action}</Badge>
                    </p>
                    <p className="text-[10px] text-muted-foreground">{rec.reason}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
