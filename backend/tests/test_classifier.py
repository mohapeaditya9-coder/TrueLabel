import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.field_classifier import FieldClassifier

client = TestClient(app)


def test_field_classifier_comprehensive():
    sample_blocks = [
        {"text": "AASHIRVAAD SHUDH CHAKKI ATTA", "bounding_box": [[10, 10], [200, 10], [200, 30], [10, 30]], "confidence": 0.95},
        {"text": "NET QUANTITY: 5 kg", "bounding_box": [[10, 40], [150, 40], [150, 60], [10, 60]], "confidence": 0.98},
        {"text": "MRP Rs. 260.00 (INCL. OF ALL TAXES)", "bounding_box": [[10, 70], [250, 70], [250, 90], [10, 90]], "confidence": 0.92},
        {"text": "UNIT SALE PRICE: Rs. 52.00 per kg", "bounding_box": [[10, 100], [220, 100], [220, 120], [10, 120]], "confidence": 0.91},
        {"text": "PKD. ON: 15/08/2026", "bounding_box": [[10, 130], [140, 130], [140, 150], [10, 150]], "confidence": 0.94},
        {"text": "MANUFACTURED & PACKED BY: ITC Limited, 37 J.L. Nehru Road, Kolkata - 700071", "bounding_box": [[10, 160], [450, 160], [450, 180], [10, 180]], "confidence": 0.96},
        {"text": "COUNTRY OF ORIGIN: India", "bounding_box": [[10, 190], [180, 190], [180, 210], [10, 210]], "confidence": 0.97},
        {"text": "FEEDBACK / GRIEVANCE: Tel: 1800-425-4444 | itccares@itc.in", "bounding_box": [[10, 220], [380, 220], [380, 240], [10, 240]], "confidence": 0.93},
    ]

    classifier = FieldClassifier()
    result = classifier.classify_blocks(sample_blocks)

    # 1. Manufacturer
    mfg = result["manufacturer_name_and_address"]
    assert mfg["found"] is True
    assert "ITC Limited" in mfg["value"]
    assert "700071" in mfg["value"]
    assert mfg["bounding_box"] is not None

    # 2. Net Quantity
    qty = result["net_quantity"]
    assert qty["found"] is True
    assert "5 kg" in qty["value"]
    assert qty["details"]["magnitude"] == 5.0
    assert qty["details"]["unit"] == "kg"

    # 3. MRP
    mrp = result["mrp"]
    assert mrp["found"] is True
    assert "260" in mrp["value"]
    assert mrp["details"]["amount"] == 260.0
    assert mrp["details"]["includes_taxes_phrase"] is True

    # 4. Mfg Date
    mfg_date = result["month_year_of_manufacture_or_import"]
    assert mfg_date["found"] is True
    assert "15/08/2026" in mfg_date["value"] or "08/2026" in mfg_date["value"]

    # 5. Consumer care
    care = result["consumer_care_details"]
    assert care["found"] is True
    assert care["details"]["has_phone"] is True
    assert care["details"]["has_email"] is True
    assert "1800-425-4444" in care["details"]["phone"]
    assert "itccares@itc.in" in care["details"]["email"]

    # 6. Country of origin
    origin = result["country_of_origin"]
    assert origin["found"] is True
    assert "India" in origin["value"]

    # 7. Unit Sale Price
    usp = result["unit_sale_price"]
    assert usp["found"] is True
    assert "52" in usp["value"]


def test_split_block_classification():
    # Test key in one block, value in adjacent block
    split_blocks = [
        {"text": "NET QUANTITY:", "bounding_box": [[10, 10], [80, 10], [80, 25], [10, 25]], "confidence": 0.85},
        {"text": "500 g", "bounding_box": [[100, 10], [140, 10], [140, 25], [100, 25]], "confidence": 0.95},
        {"text": "MRP (INCL OF ALL TAXES):", "bounding_box": [[10, 30], [120, 30], [120, 45], [10, 45]], "confidence": 0.88},
        {"text": "Rs. 175.00", "bounding_box": [[130, 30], [180, 30], [180, 45], [130, 45]], "confidence": 0.92},
    ]

    classifier = FieldClassifier()
    result = classifier.classify_blocks(split_blocks)

    assert result["net_quantity"]["found"] is True
    assert "500" in result["net_quantity"]["value"]

    assert result["mrp"]["found"] is True
    assert "175" in result["mrp"]["value"]
    assert result["mrp"]["details"]["includes_taxes_phrase"] is True
