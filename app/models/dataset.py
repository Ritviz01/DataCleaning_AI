from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from app.db.session import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(12), primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), default="uploaded")
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
