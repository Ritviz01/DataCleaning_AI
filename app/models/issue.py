from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.session import Base

class QualityIssue(Base):
    __tablename__ = "quality_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(String(12), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(100), nullable=True)
    issue_type = Column(String(100), nullable=False)
    original_value = Column(String(500), nullable=True)
    confidence = Column(Float, nullable=True)
    recommendation = Column(String(1000), nullable=True)
    status = Column(String(50), default="proposed")
