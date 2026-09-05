import io
import os
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal
from app.models.scan import ProductScan

client = TestClient(app)


def create_test_image(format="JPEG", size=(200, 200), color="blue") -> io.BytesIO:
    """Helper to generate an in-memory valid test image."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_upload_valid_jpeg():
    img_buf = create_test_image(format="JPEG")
    files = {"file": ("test_label.jpg", img_buf, "image/jpeg")}

    response = client.post("/api/scan/upload", files=files)
    assert response.status_code == 201
    data = response.json()

    assert "scan_id" in data
    assert data["original_filename"] == "test_label.jpg"
    assert data["status"] == "processed"
    assert data["file_size"] > 0
    assert os.path.exists(data["image_path"])

    # Verify database persistence
    db = SessionLocal()
    try:
        record = db.query(ProductScan).filter(ProductScan.scan_id == data["scan_id"]).first()
        assert record is not None
        assert record.status == "processed"
        assert record.original_filename == "test_label.jpg"
        assert record.file_size == data["file_size"]
    finally:
        db.close()


def test_upload_valid_png():
    img_buf = create_test_image(format="PNG", color="green")
    files = {"file": ("sample_pkg.png", img_buf, "image/png")}

    response = client.post("/api/scan/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["scan_id"] is not None
    assert data["status"] == "processed"


def test_upload_invalid_extension():
    fake_content = io.BytesIO(b"Hello world this is not an image")
    files = {"file": ("malicious.exe", fake_content, "application/octet-stream")}

    response = client.post("/api/scan/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_upload_corrupted_image():
    # File named .jpg but contains corrupted bytes
    fake_content = io.BytesIO(b"corrupted image content here")
    files = {"file": ("corrupt.jpg", fake_content, "image/jpeg")}

    response = client.post("/api/scan/upload", files=files)
    assert response.status_code == 400
    assert "Invalid or corrupted image" in response.json()["detail"]


def test_get_scan_record_by_id():
    img_buf = create_test_image(format="JPEG", color="red")
    upload_res = client.post("/api/scan/upload", files={"file": ("red_label.jpg", img_buf, "image/jpeg")})
    assert upload_res.status_code == 201
    scan_id = upload_res.json()["scan_id"]

    get_res = client.get(f"/api/scan/{scan_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["scan_id"] == scan_id
    assert data["status"] == "processed"
    assert data["original_filename"] == "red_label.jpg"
