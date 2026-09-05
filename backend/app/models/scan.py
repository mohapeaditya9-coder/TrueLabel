import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class ProductScan(Base):
    __tablename__ = "product_scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(64), unique=True, index=True, nullable=False)
    image_path = Column(String(512), nullable=False)
    image_filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), index=True, nullable=True)
    mime_type = Column(String(64), nullable=False)
    status = Column(String(32), default="pending", index=True, nullable=False)  # pending / processed / failed
    ocr_results = Column(JSON, nullable=True)
    classified_fields = Column(JSON, nullable=True)
    compliance_results = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "image_path": self.image_path,
            "image_filename": self.image_filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "status": self.status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Alias for backward compatibility
ScanRecord = ProductScan
