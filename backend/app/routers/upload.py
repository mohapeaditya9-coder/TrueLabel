import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.scan import ProductScan
from ..schemas.scan import ScanUploadResponse
from ..services.storage_service import StorageService
from ..services.ocr_service import OCRService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["Scan & Upload"])


@router.post(
    "/upload",
    response_model=ScanUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload commodity label image and trigger OCR",
    description="Accepts an image file (JPG/PNG/WEBP up to 10MB), stores it on disk, automatically executes EasyOCR extraction, and updates the ProductScan database record.",
)
async def upload_label_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or "unknown.jpg"

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}",
        )

    # 1. Validate and save image to disk
    try:
        scan_id, saved_filename, full_file_path, file_hash = StorageService.validate_and_save_image(
            file_bytes=content,
            original_filename=filename,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing image: {str(e)}",
        )

    mime_type = file.content_type or ("image/png" if filename.lower().endswith(".png") else "image/jpeg")

    # 2. Create initial database record (status: pending)
    scan_record = ProductScan(
        scan_id=scan_id,
        image_path=full_file_path,
        image_filename=saved_filename,
        original_filename=filename,
        file_size=len(content),
        file_hash=file_hash,
        mime_type=mime_type,
        status="pending",
    )

    db.add(scan_record)
    db.commit()
    db.refresh(scan_record)

    # 3. Synchronously trigger OCR extraction
    # =========================================================================
    # PHASE 2 ARCHITECTURAL NOTE / PRODUCTION IMPROVEMENT:
    # For hackathon simplicity and immediate client feedback, OCR processing
    # is executed synchronously within this request cycle.
    # In a high-throughput production environment, this should be offloaded to
    # an asynchronous task queue (e.g., Celery, Redis Queue, or FastAPI
    # BackgroundTasks) paired with WebSockets or polling for status updates
    # to avoid blocking request worker threads during intensive neural model inference.
    # =========================================================================
    try:
        ocr_service = OCRService()
        ocr_blocks = ocr_service.extract_text(full_file_path)
        scan_record.ocr_results = ocr_blocks
        scan_record.status = "processed"
        logger.info(f"Scan {scan_id}: Extracted {len(ocr_blocks)} OCR text blocks.")
    except Exception as ocr_err:
        logger.error(f"Scan {scan_id}: OCR extraction error: {ocr_err}")
        scan_record.status = "failed"
        scan_record.ocr_results = [{"error": str(ocr_err)}]

    db.commit()
    db.refresh(scan_record)

    return scan_record
