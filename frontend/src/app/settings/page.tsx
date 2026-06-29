"use client";

import { useAppStore } from "@/store/app-store";
import { useTheme } from "next-themes";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Settings, Shield, Moon, Sun, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";
import { api } from "@/services/api";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { settings, updateSettings } = useAppStore();
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  const checkConnection = async () => {
    setBackendStatus("checking");
    try {
      await api.get("/");
      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
  };

  useEffect(() => {
    checkConnection();
  }, []);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage system configurations, API credentials, and interface themes.
        </p>
      </div>

      {/* Connection Check */}
      <Card className="rounded-xl border border-border bg-card">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div>
            <CardTitle className="text-sm font-bold">API Connection Status</CardTitle>
            <CardDescription>Verification check with backend FastAPI server.</CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={checkConnection} disabled={backendStatus === "checking"}>
            <RefreshCw className={`h-4 w-4 ${backendStatus === "checking" ? "animate-spin" : ""}`} />
          </Button>
        </CardHeader>
        <CardContent className="flex items-center gap-3 text-xs">
          {backendStatus === "checking" ? (
            <span className="text-muted-foreground">Checking connection...</span>
          ) : backendStatus === "online" ? (
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-emerald-500" />
              <span className="font-semibold text-emerald-500">Service is Online</span>
              <Badge variant="outline" className="text-[10px] ml-2">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </Badge>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span className="font-semibold text-destructive">Backend Offline</span>
              <span className="text-muted-foreground">Ensure uvicorn is running on port 8000</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Theme selection */}
      <Card className="rounded-xl border border-border bg-card">
        <CardHeader>
          <CardTitle className="text-sm font-bold flex items-center gap-1.5">
            <Settings className="h-4 w-4 text-primary" />
            Interface Theme
          </CardTitle>
          <CardDescription>Toggle between dark and light mode views.</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between py-2 text-xs">
          <span className="font-semibold">Dark mode enabled</span>
          <Switch
            checked={theme === "dark"}
            onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
          />
        </CardContent>
      </Card>

      {/* LLM Credentials */}
      <Card className="rounded-xl border border-border bg-card">
        <CardHeader>
          <CardTitle className="text-sm font-bold flex items-center gap-1.5">
            <Shield className="h-4 w-4 text-primary" />
            AI LLM Providers
          </CardTitle>
          <CardDescription>Check configurations of connected generative models.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <p className="font-semibold">OpenAI GPT-4o-mini</p>
              <p className="text-[10px] text-muted-foreground">Required for AI Copilot chat and dashboards</p>
            </div>
            <Badge variant="secondary" className="rounded-full text-[10px] uppercase font-bold">
              Configured via Env
            </Badge>
          </div>

          <div className="flex items-center justify-between py-1">
            <div>
              <p className="font-semibold">Google Gemini Pro</p>
              <p className="text-[10px] text-muted-foreground">Optional fallback logic for semantic cleaners</p>
            </div>
            <Badge variant="outline" className="rounded-full text-[10px] uppercase font-bold text-muted-foreground">
              Optional fallback
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
