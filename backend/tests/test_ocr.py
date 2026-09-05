import io
import os
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from app.main import app
from app.services.ocr_service import OCRService

client = TestClient(app)


def generate_synthetic_label_buffer(lines) -> io.BytesIO:
    """Helper to create a high-contrast label image with specified lines of text."""
    img = Image.new("RGB", (700, 350), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(10, 10), (690, 340)], outline="#000000", width=2)

    y = 30
    for line in lines:
        draw.text((30, y), line, fill="#000000")
        y += 40

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_ocr_service_direct_extraction(tmp_path):
    # Create an image on disk
    img_path = str(tmp_path / "label_direct.jpg")
    img = Image.new("RGB", (600, 200), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((20, 40), "AMUL BUTTER 500g", fill="#000000")
    draw.text((20, 90), "MRP Rs. 275.00 INCL OF ALL TAXES", fill="#000000")
    img.save(img_path, "JPEG")

    ocr_service = OCRService()
    results = ocr_service.extract_text(img_path)

    assert isinstance(results, list)
    assert len(results) > 0
    first_block = results[0]
    assert "text" in first_block
    assert "bounding_box" in first_block
    assert len(first_block["bounding_box"]) == 4
    assert "confidence" in first_block
    assert first_block["confidence"] >= 0.0

    all_text = " ".join(b["text"] for b in results).upper()
    assert "AMUL" in all_text or "BUTTER" in all_text or "MRP" in all_text


def test_upload_flow_triggers_ocr_and_raw_text_endpoint():
    lines = [
        "PARLE-G ORIGINAL GLUCOSE BISCUITS",
        "NET WEIGHT: 800 g",
        "MRP Rs. 90.00 (INCL. OF ALL TAXES)",
        "MFG DATE: 09/2026",
    ]
    img_buf = generate_synthetic_label_buffer(lines)
    files = {"file": ("parle_g_label.jpg", img_buf, "image/jpeg")}

    # 1. Test upload triggers OCR
    res = client.post("/api/scan/upload", files=files)
    assert res.status_code == 201
    upload_data = res.json()
    assert upload_data["status"] == "processed"
    scan_id = upload_data["scan_id"]

    # 2. Test raw-text endpoint
    raw_res = client.get(f"/api/scan/{scan_id}/raw-text")
    assert raw_res.status_code == 200
    raw_data = raw_res.json()

    assert raw_data["scan_id"] == scan_id
    assert raw_data["status"] == "processed"
    assert raw_data["total_blocks"] > 0
    assert len(raw_data["blocks"]) > 0
    assert "GLUCOSE" in raw_data["full_text"].upper() or "PARLE" in raw_data["full_text"].upper()
