import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.scan import ProductScan
from ..schemas.scan import ScanUploadResponse
from ..services.storage_service import StorageService

router = APIRouter(prefix="/api/scan", tags=["Scan & Upload"])


@router.post(
    "/upload",
    response_model=ScanUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload commodity label image",
    description="Accepts an image file (JPG/PNG/WEBP up to 10MB), stores it on disk, and creates a pending ProductScan database record.",
)
async def upload_label_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate content-type or filename extension
    filename = file.filename or "unknown.jpg"
    
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}",
        )

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

    # Determine MIME type
    mime_type = file.content_type or ("image/png" if filename.lower().endswith(".png") else "image/jpeg")

    # Create ProductScan database record
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

    return scan_record
