from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ScanUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scan_id: str
    id: int
    image_path: str
    image_filename: str
    original_filename: str
    file_size: int
    file_hash: Optional[str] = None
    mime_type: str
    status: str
    uploaded_at: datetime


class ScanStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: str
    image_path: str
    original_filename: str
    file_size: int
    status: str
    uploaded_at: datetime
    ocr_results: Optional[Any] = None
    classified_fields: Optional[Any] = None
    compliance_results: Optional[Any] = None
