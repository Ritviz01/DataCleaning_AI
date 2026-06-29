export interface DatasetMetadata {
  filename?: string;
  rows?: number;
  columns?: number;
  size_bytes?: number;
  column_names?: string[];
}

export interface DatasetColumn {
  column_name: string;
  type: string;
  semantic_type: string;
}

export interface DatasetProfile {
  column_name: string;
  data_type: string;
  null_count: number;
  null_percentage: number;
  unique_values: number;
  min?: any;
  max?: any;
  mean?: number;
  std_dev?: number;
}

export interface DatasetQuality {
  quality_score: number;
  grade: string;
  sub_scores: {
    completeness: number;
    uniqueness: number;
    validity: number;
  };
}

export interface DatasetIssue {
  column?: string;
  issue_type: string;
  count: number;
  severity: "high" | "medium" | "low";
  description?: string;
}

export interface DatasetRecommendation {
  column: string;
  recommended_action: string;
  reason: string;
}

export interface TypeSuggestion {
  column: string;
  current_type: string;
  suggested_type: string;
}

export interface DatasetAnalysis {
  metadata: DatasetMetadata;
  schema: DatasetColumn[];
  profile: DatasetProfile[];
  quality: DatasetQuality;
  issues: DatasetIssue[];
  recommendations: DatasetRecommendation[];
  type_suggestions: TypeSuggestion[];
  insights: string[];
}

export interface KPI {
  name: string;
  value: string | number;
  description?: string;
}

export interface ChartRecommendation {
  chart: string;
  x: string;
  y: string | string[];
  description?: string;
}

export interface SQLQuery {
  title: string;
  query: string;
  explanation: string;
}

export interface DatasetEnrichment {
  dataset_type: string;
  recommended_kpis: string[];
  recommended_charts: ChartRecommendation[];
  human_review_flags: any[];
  data_dictionary: any[];
  sql_queries: SQLQuery[];
  executive_report: string;
}

export interface DatasetDetailsResponse extends DatasetEnrichment {
  dataset_id: string;
  filename: string;
  analysis: DatasetAnalysis;
  dashboard: any;
  export?: {
    filename: string;
    download_url: string;
  };
}

export interface PipelineStep {
  step_id?: string;
  order: number;
  transformation: string;
  params: Record<string, any>;
}

export interface Pipeline {
  pipeline_id: string;
  name: string;
  description?: string;
  dataset_id?: string;
  stop_on_error: boolean;
  created_at?: string;
  steps?: PipelineStep[];
}

export interface PipelineExecutionLog {
  id: string;
  step_order: number;
  transformation: string;
  status: "success" | "failure" | "skipped";
  rows_before?: number;
  rows_after?: number;
  duration_ms?: number;
  error_message?: string;
}

export interface PipelineRun {
  run_id: string;
  pipeline_id: string;
  dataset_id: string;
  status: "completed" | "failed" | "running";
  rows_before?: number;
  rows_after?: number;
  started_at: string;
  completed_at?: string;
  error_message?: string;
  output_dataset_id?: string;
  logs?: PipelineExecutionLog[];
}

export interface CopilotTurn {
  question: string;
  answer: string;
  generated_pipeline: {
    pipeline_name: string;
    description: string;
    steps: PipelineStep[];
  };
  user_feedback?: string;
}

export interface CopilotHistory {
  session_history: CopilotTurn[];
  saved_pipelines: {
    pipeline_id: string;
    name: string;
    description: string;
    dataset_id?: string;
    created_at?: string;
  }[];
}
