import json
import yaml
from typing import Dict, Any, List
from app.models.pipeline import Pipeline, PipelineStep

def export_pipeline_as_json(pipeline: Pipeline, steps: List[PipelineStep]) -> Dict[str, Any]:
    """
    Exports a pipeline and its steps as a JSON-serializable dictionary.
    """
    sorted_steps = sorted(steps, key=lambda s: s.order)
    return {
        "pipeline_name": pipeline.name,
        "description": pipeline.description,
        "is_template": pipeline.is_template,
        "stop_on_error": pipeline.stop_on_error,
        "steps": [
            {
                "order": step.order,
                "transformation": step.transformation,
                "params": json.loads(step.params) if step.params else {}
            }
            for step in sorted_steps
        ]
    }

def export_pipeline_as_yaml(pipeline: Pipeline, steps: List[PipelineStep]) -> str:
    """
    Exports a pipeline and its steps as a YAML string.
    """
    data = export_pipeline_as_json(pipeline, steps)
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)

def export_pipeline_as_template(pipeline: Pipeline, steps: List[PipelineStep]) -> Dict[str, Any]:
    """
    Exports the pipeline as a reusable template definition.
    """
    data = export_pipeline_as_json(pipeline, steps)
    return {
        "template_name": data["pipeline_name"],
        "description": data["description"],
        "steps": [
            {
                "order": s["order"],
                "transformation": s["transformation"],
                "params": s["params"]
            }
            for s in data["steps"]
        ]
    }

def generate_execution_report(run_details: Dict[str, Any]) -> str:
    """
    Generates a human-readable markdown execution report of a pipeline run.
    """
    steps = run_details.get("steps", [])
    steps_md = []
    
    for s in steps:
        step_status_emoji = "✅" if s["status"] == "success" else "❌" if s["status"] == "failed" else "⚠️"
        steps_md.append(
            f"### Step {s['step_order']}: {s['transformation']}\n"
            f"- **Status**: {step_status_emoji} {s['status'].upper()}\n"
            f"- **Duration**: {s['duration_ms']} ms\n"
            f"- **Rows Affected**: {s['rows_affected']}\n"
            f"- **Columns Affected**: {', '.join(s['columns_affected']) if s['columns_affected'] else 'None'}\n"
        )
        if s.get("error_message"):
            steps_md.append(f"- **Error**: `{s['error_message']}`\n")
            
    steps_section = "\n".join(steps_md)
    
    status_emoji = "🟢" if run_details["status"] == "completed" else "🔴" if run_details["status"] == "failed" else "🟡"
    
    return f"""# Pipeline Execution Report
**Run ID**: {run_details['run_id']}
**Pipeline ID**: {run_details['pipeline_id']}
**Dataset ID**: {run_details['dataset_id']}
**Status**: {status_emoji} {run_details['status'].upper()}
**Started At**: {run_details['started_at']}
**Completed At**: {run_details['completed_at']}
**Duration**: {run_details['duration_seconds']} seconds

## Metrics Summary
- **Steps Executed**: {run_details['steps_executed']}
- **Steps Failed**: {run_details['steps_failed']}
- **Rows Before**: {run_details['rows_before']}
- **Rows After**: {run_details['rows_after']}
- **Columns Modified**: {run_details['columns_modified']}

## Detailed Steps Executed
{steps_section}
"""

def generate_audit_report(run_details: Dict[str, Any]) -> str:
    """
    Generates a detailed audit markdown report focusing on data compliance and changes made.
    """
    steps = run_details.get("steps", [])
    audit_rows = []
    
    for s in steps:
        if s["status"] == "success" and s["rows_affected"] > 0:
            details_str = json.dumps(s.get("details", {}).get("params", {}))
            audit_rows.append(
                f"| {s['step_order']} | {s['transformation']} | {s['rows_affected']} | {', '.join(s['columns_affected']) if s['columns_affected'] else 'None'} | {details_str} |"
            )
            
    audit_table = "\n".join(audit_rows)
    if not audit_table:
        audit_table = "| - | No structural changes were made | - | - | - |"
        
    return f"""# Pipeline Audit Compliance Report
**Run ID**: {run_details['run_id']}
**Timestamp**: {run_details['completed_at'] or run_details['started_at']}
**Execution Status**: {run_details['status'].upper()}

## Summary of Mutations
Every transformation executed by the pipeline is audited below.

| Step | Transformation | Rows Mutated / Affected | Columns Mutated | Parameters / Rules Applied |
|---|---|---|---|---|
{audit_table}

---
*Generated automatically by DataClean AI Pipeline Audit compliance logger.*
"""
