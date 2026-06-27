from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from app.db.session import Base

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(String(12), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    dashboard_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
