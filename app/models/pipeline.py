from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from app.db.session import Base

class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    dataset_id = Column(String(12), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    is_template = Column(Boolean, default=False)
    stop_on_error = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PipelineStep(Base):
    __tablename__ = "pipeline_steps"

    id = Column(String(36), primary_key=True, index=True)
    pipeline_id = Column(String(36), ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    transformation = Column(String(100), nullable=False)
    params = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String(36), primary_key=True, index=True)
    pipeline_id = Column(String(36), ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(String(12), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    steps_executed = Column(Integer, default=0)
    steps_failed = Column(Integer, default=0)
    rows_before = Column(Integer, nullable=True)
    rows_after = Column(Integer, nullable=True)
    columns_modified = Column(Integer, nullable=True)
    error_summary = Column(Text, nullable=True)

class PipelineExecutionLog(Base):
    __tablename__ = "pipeline_execution_logs"

    id = Column(String(36), primary_key=True, index=True)
    run_id = Column(String(36), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    transformation = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Float, nullable=True)
    rows_affected = Column(Integer, nullable=True)
    columns_affected = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
