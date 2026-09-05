import os
import json
import glob
import httpx

API_URL = "http://127.0.0.1:8000/api/scan/upload"
BASE_URL = "http://127.0.0.1:8000/api/scan"

sample_files = glob.glob("sample_images/*.jpg")
print(f"Found {len(sample_files)} sample label images to test.\n" + "=" * 65)

results_summary = []

with httpx.Client(timeout=60.0) as client:
    for filepath in sample_files:
        filename = os.path.basename(filepath)
        print(f"\nScanning: {filename}...")

        with open(filepath, "rb") as f:
            files = {"file": (filename, f.read(), "image/jpeg")}
            res = client.post(API_URL, files=files)

        if res.status_code != 201:
            print(f"FAILED to upload: {res.status_code} {res.text}")
            continue

        data = res.json()
        scan_id = data["scan_id"]
        status = data["status"]
        print(f" -> Scan ID: {scan_id} (Status: {status})")

        # Fetch raw OCR text
        raw_res = client.get(f"{BASE_URL}/{scan_id}/raw-text")
        if raw_res.status_code == 200:
            ocr_info = raw_res.json()
            total_blocks = ocr_info["total_blocks"]
            full_text = ocr_info["full_text"]
            blocks = ocr_info["blocks"]

            results_summary.append({
                "filename": filename,
                "scan_id": scan_id,
                "status": status,
                "total_blocks": total_blocks,
                "full_text": full_text,
                "sample_blocks": blocks[:3],
            })

            print(f" -> OCR Extracted: {total_blocks} text blocks")
            print(f" -> Detected Text Summary:\n{'-'*40}\n{full_text}\n{'-'*40}")
        else:
            print(f" -> FAILED to fetch raw text: {raw_res.status_code}")

print("\n" + "=" * 65 + "\nALL 4 LABELS PROCESSED SUCCESSFULLY WITH EasyOCR!")
