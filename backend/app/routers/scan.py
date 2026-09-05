from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.scan import ProductScan
from ..schemas.scan import ScanStatusResponse
from ..services.field_classifier import FieldClassifier
from ..services.rule_engine import RuleEngine

router = APIRouter(prefix="/api/scan", tags=["Scan & Upload"])


@router.get(
    "/{scan_id}/compliance",
    summary="Evaluate LMPC compliance and violations",
    description="Evaluates detected declarations against Legal Metrology Rules, 2011, returning overall status, violation list, and font size assessment.",
)
def get_compliance_results(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(ProductScan).filter(ProductScan.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found",
        )

    # Ensure classified_fields are available
    fields = scan.classified_fields
    if not fields and scan.ocr_results and isinstance(scan.ocr_results, list):
        classifier = FieldClassifier()
        fields = classifier.classify_blocks(scan.ocr_results)
        scan.classified_fields = fields

    if not fields:
        classifier = FieldClassifier()
        fields = classifier._empty_results()

    # Evaluate against config-driven rule engine
    engine = RuleEngine()
    compliance_report = engine.evaluate(fields, scan.ocr_results)

    # Persist in database
    scan.compliance_results = compliance_report
    db.commit()
    db.refresh(scan)

    return {
        "scan_id": scan.scan_id,
        "status": scan.status,
        "original_filename": scan.original_filename,
        **compliance_report,
    }


@router.get(
    "/{scan_id}/fields",
    summary="Get classified mandatory LMPC fields",
    description="Returns mapped declaration fields (manufacturer, net quantity, MRP, mfg date, consumer care, origin, USP) with source text and bounding boxes.",
)
def get_classified_fields(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(ProductScan).filter(ProductScan.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found",
        )

    fields = scan.classified_fields
    # If not previously classified (e.g. earlier test scans), classify on the fly
    if not fields and scan.ocr_results and isinstance(scan.ocr_results, list):
        classifier = FieldClassifier()
        fields = classifier.classify_blocks(scan.ocr_results)
        scan.classified_fields = fields
        db.commit()
        db.refresh(scan)

    if not fields:
        classifier = FieldClassifier()
        fields = classifier._empty_results()

    fields_found = [k for k, v in fields.items() if v.get("found")]
    missing_fields = [k for k, v in fields.items() if not v.get("found")]

    return {
        "scan_id": scan.scan_id,
        "status": scan.status,
        "original_filename": scan.original_filename,
        "summary": {
            "total_mandatory_fields": 7,
            "fields_detected_count": len(fields_found),
            "fields_detected": fields_found,
            "missing_fields": missing_fields,
        },
        "fields": fields,
    }


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
