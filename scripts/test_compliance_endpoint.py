import os
import json
import glob
import httpx

API_BASE = "http://127.0.0.1:8000/api/scan"
sample_files = sorted(glob.glob("sample_images/*.jpg"))

print("Evaluating LMPC Compliance across sample products...\n" + "=" * 75)

with httpx.Client(timeout=60.0) as client:
    for filepath in sample_files:
        filename = os.path.basename(filepath)
        print(f"\nEvaluating: {filename}")

        # Upload to ensure fresh scan record
        with open(filepath, "rb") as f:
            upload_res = client.post(f"{API_BASE}/upload", files={"file": (filename, f.read(), "image/jpeg")})

        if upload_res.status_code != 201:
            print(f"Failed upload: {upload_res.status_code}")
            continue

        scan_id = upload_res.json()["scan_id"]

        # Call compliance endpoint
        comp_res = client.get(f"{API_BASE}/{scan_id}/compliance")
        if comp_res.status_code != 200:
            print(f"Failed compliance check: {comp_res.status_code}")
            continue

        report = comp_res.json()
        status_badge = "[COMPLIANT]" if report["overall_status"] == "compliant" else "[NON-COMPLIANT]"

        print(f" -> Scan ID: {scan_id}")
        print(f" -> Overall Status: {status_badge} ({report['compliance_score']}% compliance score)")
        print(f" -> Passed Rules: {report['passed_rules_count']}/{report['total_mandatory_rules']}")
        print(f"    Passed Fields: {', '.join(report['passed_fields'])}")

        if report["violations"]:
            print(" -> VIOLATIONS DETECTED:")
            for v in report["violations"]:
                print(f"    - [{v['severity']}] {v['field']} ({v['legal_reference']}): {v['description']}")

        font_eval = report.get("font_size_assessment", {})
        print(f" -> Font Size Check (Advisory): Median text height: {font_eval.get('label_median_height_px')}px, Soft flags: {font_eval.get('soft_flags_count', 0)}")
        if font_eval.get("soft_flags"):
            for sf in font_eval["soft_flags"]:
                print(f"    * Soft Flag: {sf['advisory']}")

print("\n" + "=" * 75 + "\nCOMPLIANCE EVALUATION COMPLETED.")
