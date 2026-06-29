"use client";

import { useAppStore } from "@/store/app-store";
import { useState, useEffect } from "react";
import { dashboardService } from "@/services/dashboard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  LineChart as RechartsLineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  ScatterChart as RechartsScatterChart,
  Scatter,
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Sparkles, BarChart3, TrendingUp, AlertCircle, FileSpreadsheet, RefreshCw } from "lucide-react";

export default function DashboardsPage() {
  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasets = Object.values(datasetCache);

  const [selectedId, setSelectedId] = useState("");
  const [dashboardData, setDashboardData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  // Set default selected dataset
  useEffect(() => {
    if (datasets.length > 0 && !selectedId) {
      setSelectedId(datasets[0].dataset_id);
    }
  }, [datasets, selectedId]);

  const fetchDashboard = async (dsId: string) => {
    if (!dsId) return;
    setLoading(true);
    try {
      const res = await dashboardService.generate(dsId);
      setDashboardData(res);
    } catch (e) {
      console.error("Failed to load dashboard: ", e);
      setDashboardData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedId) {
      fetchDashboard(selectedId);
    }
  }, [selectedId]);

  // Generate mock data for chart based on column information
  const generateChartData = (chartSpec: any, profile: any[]) => {
    const xName = chartSpec.x;
    const yName = chartSpec.y;
    
    // Find profiling statistics
    const xProfile = profile?.find((p) => p.column_name === xName);
    const yProfile = profile?.find((p) => p.column_name === yName);

    // Mock data records
    const records = [];
    const count = 8;
    
    for (let i = 0; i < count; i++) {
      const record: Record<string, any> = {};
      
      // X Axis Generation
      if (xProfile?.data_type === "String") {
        const labels = ["North", "South", "East", "West", "Central", "Online", "Store", "Partner"];
        record[xName] = labels[i % labels.length] + ` ${Math.floor(i / labels.length) || ""}`;
      } else if (xName?.toLowerCase().includes("date") || xName?.toLowerCase().includes("year")) {
        record[xName] = `2026-06-${20 + i}`;
      } else {
        record[xName] = i * 10;
      }

      // Y Axis Generation
      const mean = yProfile?.mean !== undefined && yProfile?.mean !== null ? yProfile.mean : 50;
      const min = yProfile?.min !== undefined && yProfile?.min !== null ? Number(yProfile.min) : 0;
      const max = yProfile?.max !== undefined && yProfile?.max !== null ? Number(yProfile.max) : 100;
      
      // Generate realistic values surrounding the mean
      const deviation = (max - min) * 0.15;
      const randomValue = mean + (Math.random() - 0.5) * deviation * 2;
      record[yName] = Math.max(min, Math.min(max, Math.round(randomValue * 100) / 100));

      records.push(record);
    }
    return records;
  };

  const currentDatasetProfile = selectedId ? datasetCache[selectedId]?.analysis?.profile || [] : [];

  const handleRegenerate = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await dashboardService.regenerate(selectedId);
      // Fetch full details again
      await fetchDashboard(selectedId);
    } catch (e) {
      alert("Failed to regenerate dashboard");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Dashboard Generator</h1>
          <p className="text-sm text-muted-foreground">
            Instantly render dashboards, calculate KPI metrics, and chart statistics for any dataset.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="text-xs rounded-lg border border-border p-2 bg-background font-semibold"
          >
            {datasets.length === 0 ? (
              <option value="">No datasets available</option>
            ) : (
              datasets.map((d) => (
                <option key={d.dataset_id} value={d.dataset_id}>
                  {d.filename}
                </option>
              ))
            )}
          </select>
          
          <Button
            size="sm"
            variant="outline"
            disabled={!selectedId || loading}
            onClick={handleRegenerate}
            className="h-9 gap-1 text-xs"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Skeleton className="h-28 rounded-xl bg-accent/20" />
            <Skeleton className="h-28 rounded-xl bg-accent/20" />
            <Skeleton className="h-28 rounded-xl bg-accent/20" />
          </div>
          <Skeleton className="h-96 rounded-xl bg-accent/20" />
        </div>
      ) : !dashboardData ? (
        <div className="flex h-96 flex-col items-center justify-center text-center space-y-4">
          <FileSpreadsheet className="h-12 w-12 text-muted-foreground/30 animate-pulse" />
          <h3 className="text-sm font-semibold">Select a dataset to load dashboard views</h3>
          <p className="text-xs text-muted-foreground max-w-xs">
            Generate interactive graphics based on your analytical contexts.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Executive Overview */}
          <div className="grid gap-6 md:grid-cols-3">
            <Card className="rounded-xl border border-border bg-card md:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Business Explanation & Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {dashboardData.explanation?.summary || "Analyzing dataset trends and characteristics..."}
              </CardContent>
            </Card>

            <Card className="rounded-xl border border-border bg-card">
              <CardHeader>
                <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Dashboard Context
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="flex justify-between border-b border-border pb-1">
                  <span className="text-muted-foreground">Title:</span>
                  <span className="font-semibold">{dashboardData.title}</span>
                </div>
                <div className="flex justify-between border-b border-border pb-1">
                  <span className="text-muted-foreground">Domain:</span>
                  <span className="font-bold text-primary">{dashboardData.domain}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Pages / Tabs */}
          <Tabs defaultValue="page-0" className="space-y-6">
            <TabsList className="bg-background border border-border p-1 rounded-lg">
              {dashboardData.specification?.dashboard?.pages?.map((page: any, index: number) => (
                <TabsTrigger key={index} value={`page-${index}`} className="text-xs">
                  {page.name || `Section ${index + 1}`}
                </TabsTrigger>
              ))}
            </TabsList>

            {dashboardData.specification?.dashboard?.pages?.map((page: any, pageIdx: number) => (
              <TabsContent key={pageIdx} value={`page-${pageIdx}`} className="space-y-6">
                {/* KPIs Row */}
                {page.kpis && page.kpis.length > 0 && (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {page.kpis.map((kpi: any, kpiIdx: number) => (
                      <Card key={kpiIdx} className="rounded-xl border border-border bg-card shadow-sm">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                            {kpi.name}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-black text-foreground">
                            {kpi.value} {kpi.unit || ""}
                          </div>
                          {kpi.description && (
                            <p className="text-[10px] text-muted-foreground mt-1">{kpi.description}</p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* Charts Grid */}
                {page.charts && page.charts.length > 0 && (
                  <div className="grid gap-6 md:grid-cols-2">
                    {page.charts.map((chart: any, chartIdx: number) => {
                      const mockData = generateChartData(chart, currentDatasetProfile);
                      return (
                        <Card key={chartIdx} className="rounded-xl border border-border bg-card">
                          <CardHeader>
                            <CardTitle className="text-xs font-bold">{chart.title}</CardTitle>
                            <CardDescription className="text-[10px]">
                              X: {chart.x} | Y: {chart.y}
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="h-72">
                            <ResponsiveContainer width="100%" height="100%">
                              {chart.type?.toLowerCase()?.includes("bar") ? (
                                <RechartsBarChart data={mockData}>
                                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                  <XAxis dataKey={chart.x} stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <Tooltip />
                                  <Bar dataKey={chart.y} fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                                </RechartsBarChart>
                              ) : chart.type?.toLowerCase()?.includes("pie") ? (
                                <RechartsPieChart>
                                  <Pie
                                    data={mockData}
                                    dataKey={chart.y}
                                    nameKey={chart.x}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={80}
                                    fill="hsl(var(--primary))"
                                    label
                                  >
                                    {mockData.map((entry: any, index: number) => (
                                      <Cell
                                        key={`cell-${index}`}
                                        fill={index % 2 === 0 ? "hsl(var(--primary))" : "hsl(var(--muted-foreground))"}
                                      />
                                    ))}
                                  </Pie>
                                  <Tooltip />
                                </RechartsPieChart>
                              ) : chart.type?.toLowerCase()?.includes("scatter") ? (
                                <RechartsScatterChart>
                                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                  <XAxis dataKey={chart.x} stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <YAxis dataKey={chart.y} stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                                  <Scatter data={mockData} fill="hsl(var(--primary))" />
                                </RechartsScatterChart>
                              ) : chart.type?.toLowerCase()?.includes("area") ? (
                                <RechartsAreaChart data={mockData}>
                                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                  <XAxis dataKey={chart.x} stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <Tooltip />
                                  <Area type="monotone" dataKey={chart.y} stroke="hsl(var(--primary))" fill="hsl(var(--primary)/20%)" />
                                </RechartsAreaChart>
                              ) : (
                                // Default fallback: Line Chart
                                <RechartsLineChart data={mockData}>
                                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                  <XAxis dataKey={chart.x} stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} />
                                  <Tooltip />
                                  <Line type="monotone" dataKey={chart.y} stroke="hsl(var(--primary))" strokeWidth={2} />
                                </RechartsLineChart>
                              )}
                            </ResponsiveContainer>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </div>
      )}
    </div>
  );
}
