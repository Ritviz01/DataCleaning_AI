"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAppStore } from "@/store/app-store";
import { useCopilotStore } from "@/store/copilot-store";
import { useCopilotGenerateMutation } from "@/hooks/use-copilot";
import { useRunPipelineMutation } from "@/hooks/use-pipelines";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Bot,
  User,
  Send,
  Database,
  ArrowRight,
  Sparkles,
  Play,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  HelpCircle,
} from "lucide-react";

export default function CopilotPage() {
  const router = useRouter();
  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasets = Object.values(datasetCache);
  
  const [selectedId, setSelectedId] = useState("");
  const [inputText, setInputText] = useState("");

  const { sessionId, messages, initializeSession, addMessage, clearChat } = useCopilotStore();
  const generateMutation = useCopilotGenerateMutation();
  const runMutation = useRunPipelineMutation();

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initialize session ID
  useEffect(() => {
    initializeSession();
  }, [initializeSession]);

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Set default selected dataset
  useEffect(() => {
    if (datasets.length > 0 && !selectedId) {
      setSelectedId(datasets[0].dataset_id);
    }
  }, [datasets, selectedId]);

  const handleSend = () => {
    if (!inputText.trim() || !selectedId) return;

    const userPrompt = inputText.trim();
    setInputText("");

    // 1. Add user message
    addMessage({
      sender: "user",
      text: userPrompt,
    });

    // 2. Call generator API
    generateMutation.mutate({
      datasetId: selectedId,
      prompt: userPrompt,
      sessionId: sessionId,
    });
  };

  const handleExecute = (pipeline: any) => {
    if (!selectedId || !pipeline) return;

    runMutation.mutate(
      {
        pipelineId: pipeline.pipeline_id || "temp_ai_pipeline",
        datasetId: selectedId,
      },
      {
        onSuccess: (data) => {
          // Add success response bubble
          addMessage({
            sender: "assistant",
            text: `Pipeline executed successfully. Cleaned dataset version stored with row count: ${data.rows_after} (Original rows: ${data.rows_before}). Output Dataset ID is ${data.output_dataset_id || data.dataset_id}.`,
          });
        },
      }
    );
  };

  return (
    <div className="grid gap-6 md:grid-cols-4 h-[calc(100vh-140px)] overflow-hidden">
      {/* Left panel */}
      <Card className="rounded-xl border border-border bg-card flex flex-col justify-between h-full">
        <div>
          <CardHeader>
            <CardTitle className="text-sm font-bold flex items-center gap-1.5">
              <Database className="h-4 w-4 text-primary" />
              Active Dataset
            </CardTitle>
            <CardDescription>Select a target dataset to inspect.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="w-full text-xs rounded-lg border border-border p-2 bg-background font-semibold"
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

            {datasets.length === 0 && (
              <div className="text-[10px] text-destructive flex items-center gap-1 mt-2">
                <AlertCircle className="h-3 w-3" />
                Upload a file first to clean it.
              </div>
            )}
          </CardContent>
        </div>

        <div className="p-4 border-t border-border space-y-2">
          <Button
            variant="outline"
            className="w-full text-xs rounded-lg h-9 gap-1"
            onClick={clearChat}
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Clear Conversation
          </Button>
        </div>
      </Card>

      {/* Main chat window */}
      <Card className="rounded-xl border border-border bg-card md:col-span-3 flex flex-col justify-between h-full overflow-hidden">
        {/* Messages Stream */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-[85%] ${
                msg.sender === "user" ? "ml-auto flex-row-reverse" : ""
              }`}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center text-white shrink-0 ${
                  msg.sender === "user" ? "bg-primary" : "bg-zinc-800"
                }`}
              >
                {msg.sender === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              <div className="space-y-2">
                <div
                  className={`rounded-xl px-4 py-2.5 text-xs leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground font-semibold"
                      : "bg-accent/40 text-foreground"
                  }`}
                >
                  {msg.text}
                </div>

                {/* If assistant returned generated pipeline content */}
                {msg.pipeline && (
                  <Card className="rounded-xl border border-border p-4 bg-background max-w-xl space-y-4">
                    <div className="flex items-center justify-between border-b border-border pb-2">
                      <span className="text-xs font-bold text-foreground">
                        {msg.pipeline.pipeline_name}
                      </span>
                      <Badge variant="outline" className="text-[9px] rounded-full uppercase">
                        AI Generated
                      </Badge>
                    </div>

                    {/* Step lists */}
                    <div className="space-y-2">
                      {msg.pipeline.steps?.map((step: any) => (
                        <div
                          key={step.order}
                          className="flex items-center justify-between text-[11px] bg-accent/25 rounded-md p-2"
                        >
                          <span className="font-mono font-bold text-muted-foreground">
                            {step.order}. {step.transformation}
                          </span>
                          <span className="text-[10px] text-muted-foreground font-semibold">
                            {JSON.stringify(step.params)}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Validation layer */}
                    {msg.validation && (
                      <div className="flex items-center gap-1.5 text-[10px]">
                        {msg.validation.valid ? (
                          <>
                            <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                            <span className="text-emerald-500 font-semibold">Pipeline Validated</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="h-3.5 w-3.5 text-destructive" />
                            <span className="text-destructive font-semibold">
                              Validation Errors: {msg.validation.errors?.map((e: any) => e.message).join(", ")}
                            </span>
                          </>
                        )}
                      </div>
                    )}

                    {/* Execution triggers */}
                    {msg.validation?.valid && (
                      <Button
                        size="sm"
                        className="rounded-full gap-1"
                        onClick={() => handleExecute(msg.pipeline)}
                        disabled={runMutation.isPending}
                      >
                        <Play className="h-3 w-3" />
                        Execute Pipeline
                      </Button>
                    )}
                  </Card>
                )}
              </div>
            </div>
          ))}

          {/* Generator loading bubbles */}
          {generateMutation.isPending && (
            <div className="flex gap-3 max-w-[85%]">
              <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center text-white shrink-0">
                <Bot className="h-4 w-4" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-8 w-60 rounded-xl" />
                <Skeleton className="h-32 w-80 rounded-xl" />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Prompt input field */}
        <div className="p-4 border-t border-border flex items-center gap-3">
          <Input
            placeholder={
              selectedId
                ? "Instruct the Copilot to clean dataset... (E.g. Deduplicate rows)"
                : "Select an active dataset first to start chatting"
            }
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={!selectedId || generateMutation.isPending}
            className="flex-1 rounded-lg"
          />
          <Button
            onClick={handleSend}
            disabled={!selectedId || !inputText.trim() || generateMutation.isPending}
            className="rounded-lg h-10 w-10 p-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    </div>
  );
}
