import os
import json
import glob
import httpx

API_UPLOAD_URL = "http://127.0.0.1:8000/api/scan/upload"
BASE_URL = "http://127.0.0.1:8000/api/scan"

sample_files = sorted(glob.glob("sample_images/*.jpg"))
print(f"Testing Field Classifier on {len(sample_files)} sample label images...\n" + "=" * 75)

summary_results = {}

with httpx.Client(timeout=60.0) as client:
    for filepath in sample_files:
        filename = os.path.basename(filepath)
        print(f"\n===========================================================================")
        print(f"PRODUCT: {filename}")
        print("===========================================================================")

        # Upload and trigger OCR + Classification
        with open(filepath, "rb") as f:
            files = {"file": (filename, f.read(), "image/jpeg")}
            res = client.post(API_UPLOAD_URL, files=files)

        if res.status_code != 201:
            print(f"Upload failed: {res.status_code} {res.text}")
            continue

        data = res.json()
        scan_id = data["scan_id"]

        # Fetch classified fields endpoint
        fields_res = client.get(f"{BASE_URL}/{scan_id}/fields")
        if fields_res.status_code != 200:
            print(f"Failed to fetch fields: {fields_res.status_code}")
            continue

        fields_data = fields_res.json()
        fields = fields_data["fields"]
        summary = fields_data["summary"]

        summary_results[filename] = {
            "scan_id": scan_id,
            "detected_count": summary["fields_detected_count"],
            "missing": summary["missing_fields"],
            "fields": fields,
        }

        print(f"Scan ID: {scan_id}")
        print(f"Fields Detected: {summary['fields_detected_count']}/7")
        if summary["missing_fields"]:
            print(f"Missing Fields: {summary['missing_fields']}")

        print("\n--- CLASSIFIED DECLARATIONS ---")
        for field_name, item in fields.items():
            status_icon = "[PASS]" if item["found"] else "[FAIL]"
            val = item["value"]
            conf = f"({item['confidence']*100:.1f}%)" if item["found"] else ""
            print(f"  {status_icon} {field_name.upper():<36}: {val or '<NOT FOUND>'} {conf}")
            if item.get("details"):
                print(f"       -> Details: {item['details']}")

print("\n" + "=" * 75)
print("CLASSIFIER TEST COMPLETE ACROSS ALL SAMPLES.")
