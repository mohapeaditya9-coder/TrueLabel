import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from .database import Base


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(64), unique=True, index=True, nullable=False)
    image_filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), index=True)
    mime_type = Column(String(64), nullable=False)
    status = Column(String(32), default="UPLOADED", index=True)
    ocr_results = Column(JSON, nullable=True)
    classified_fields = Column(JSON, nullable=True)
    compliance_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
