from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.scan import ProductScan
from ..schemas.scan import ScanStatusResponse

router = APIRouter(prefix="/api/scan", tags=["Scan & Upload"])


@router.get(
    "/{scan_id}/raw-text",
    summary="Get raw OCR text output and bounding boxes",
    description="Returns full reconstructed text and individual OCR blocks with coordinates and confidence for debugging.",
)
def get_raw_ocr_text(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(ProductScan).filter(ProductScan.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found",
        )

    raw_blocks = scan.ocr_results or []
    if isinstance(raw_blocks, list):
        full_text = "\n".join(b.get("text", "") for b in raw_blocks if isinstance(b, dict) and "text" in b)
    else:
        full_text = str(raw_blocks)

    return {
        "scan_id": scan.scan_id,
        "status": scan.status,
        "original_filename": scan.original_filename,
        "total_blocks": len(raw_blocks) if isinstance(raw_blocks, list) else 0,
        "full_text": full_text,
        "blocks": raw_blocks,
    }


@router.get(
    "/{scan_id}",
    response_model=ScanStatusResponse,
    summary="Get scan record by scan_id",
)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(ProductScan).filter(ProductScan.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found",
        )
    return scan


@router.get(
    "/",
    response_model=List[ScanStatusResponse],
    summary="List recent scans",
)
def list_scans(limit: int = 20, db: Session = Depends(get_db)):
    scans = db.query(ProductScan).order_by(ProductScan.uploaded_at.desc()).limit(limit).all()
    return scans
