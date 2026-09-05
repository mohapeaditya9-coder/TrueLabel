import pytest
from app.services.rule_engine import RuleEngine


def test_fully_compliant_product():
    """Test pure rule engine evaluation on a fully compliant package."""
    fake_fields = {
        "manufacturer_name_and_address": {
            "value": "Amul Dairy, Anand - 388001, Gujarat",
            "found": True,
            "confidence": 0.95,
            "bounding_box": [[10, 10], [100, 10], [100, 30], [10, 30]],
            "details": {"has_pincode": True},
        },
        "net_quantity": {
            "value": "500 g",
            "found": True,
            "confidence": 0.98,
            "bounding_box": [[10, 40], [100, 40], [100, 60], [10, 60]],
            "details": {"magnitude": 500.0, "unit": "g"},
        },
        "mrp": {
            "value": "MRP Rs. 275.00 (Inclusive of all taxes)",
            "found": True,
            "confidence": 0.92,
            "bounding_box": [[10, 70], [100, 70], [100, 90], [10, 90]],
            "details": {"amount": 275.0, "includes_taxes_phrase": True},
        },
        "month_year_of_manufacture_or_import": {
            "value": "08/2026",
            "found": True,
            "confidence": 0.94,
            "bounding_box": [[10, 100], [100, 100], [100, 120], [10, 120]],
            "details": {"raw_date": "08/2026"},
        },
        "consumer_care_details": {
            "value": "1800-258-3333 | care@amul.coop",
            "found": True,
            "confidence": 0.96,
            "bounding_box": [[10, 130], [100, 130], [100, 150], [10, 150]],
            "details": {"phone": "1800-258-3333", "email": "care@amul.coop", "has_phone": True, "has_email": True},
        },
        "country_of_origin": {
            "value": "India",
            "found": True,
            "confidence": 0.99,
            "bounding_box": [[10, 160], [100, 160], [100, 180], [10, 180]],
            "details": {"country": "India"},
        },
        "unit_sale_price": {
            "value": "Rs. 0.55 / g",
            "found": True,
            "confidence": 0.91,
            "bounding_box": [[10, 190], [100, 190], [100, 210], [10, 210]],
            "details": {"unit_rate": 0.55, "unit": "g"},
        },
    }

    engine = RuleEngine()
    result = engine.evaluate(fake_fields)

    assert result["overall_status"] == "compliant"
    assert len(result["violations"]) == 0
    assert result["compliance_score"] == 100.0
    assert len(result["passed_fields"]) >= 6


def test_missing_mandatory_declarations():
    """Test missing manufacturer and net quantity declarations."""
    fake_fields = {
        "manufacturer_name_and_address": {"value": None, "found": False, "details": {}},
        "net_quantity": {"value": None, "found": False, "details": {}},
        "mrp": {"value": "MRP Rs. 100.00 (incl of all taxes)", "found": True, "details": {"includes_taxes_phrase": True}},
        "month_year_of_manufacture_or_import": {"value": "08/2026", "found": True, "details": {}},
        "consumer_care_details": {"value": "care@test.com", "found": True, "details": {"has_email": True}},
        "country_of_origin": {"value": "India", "found": True, "details": {}},
        "unit_sale_price": {"value": "Rs. 1.00 / g", "found": True, "details": {}},
    }

    engine = RuleEngine()
    result = engine.evaluate(fake_fields)

    assert result["overall_status"] == "non_compliant"
    assert result["violations_count"] >= 2
    violation_fields = [v["field"] for v in result["violations"]]
    assert "manufacturer_name_and_address" in violation_fields
    assert "net_quantity" in violation_fields
    for v in result["violations"]:
        if v["field"] in {"manufacturer_name_and_address", "net_quantity"}:
            assert v["violation_type"] == "missing"
            assert v["severity"] == "CRITICAL"


def test_mrp_missing_inclusive_of_taxes():
    """Test format violation when MRP is present but lacks 'inclusive of all taxes'."""
    fake_fields = {
        "manufacturer_name_and_address": {"value": "ABC Foods Ltd, Mumbai", "found": True, "details": {}},
        "net_quantity": {"value": "1 kg", "found": True, "details": {"unit": "kg"}},
        "mrp": {
            "value": "MRP Rs. 150.00",  # Missing taxes phrase!
            "found": True,
            "details": {"amount": 150.0, "includes_taxes_phrase": False},
        },
        "month_year_of_manufacture_or_import": {"value": "05/2026", "found": True, "details": {}},
        "consumer_care_details": {"value": "1800-111-2222", "found": True, "details": {"has_phone": True}},
        "country_of_origin": {"value": "India", "found": True, "details": {}},
        "unit_sale_price": {"value": "Rs. 150 / kg", "found": True, "details": {}},
    }

    engine = RuleEngine()
    result = engine.evaluate(fake_fields)

    assert result["overall_status"] == "non_compliant"
    mrp_violations = [v for v in result["violations"] if v["field"] == "mrp"]
    assert len(mrp_violations) == 1
    assert mrp_violations[0]["violation_type"] == "incorrect_format"
    assert "inclusive of all taxes" in mrp_violations[0]["description"].lower()
    assert mrp_violations[0]["severity"] == "CRITICAL"


def test_relative_font_size_soft_flag():
    """Test best-effort font-size estimation soft-flagging disproportionately small text."""
    # Label where median text height is 30px, but consumer care is only 8px (below 40% of median = 12px)
    fake_ocr_blocks = [
        {"text": "BRAND NAME", "bounding_box": [[10, 10], [200, 10], [200, 42], [10, 42]], "confidence": 0.95}, # h=32
        {"text": "NET QUANTITY 1kg", "bounding_box": [[10, 50], [150, 50], [150, 80], [10, 80]], "confidence": 0.95}, # h=30
        {"text": "MRP Rs 100", "bounding_box": [[10, 90], [150, 90], [150, 120], [10, 120]], "confidence": 0.95}, # h=30
    ]

    fake_fields = {
        "consumer_care_details": {
            "value": "1800-000-0000",
            "found": True,
            "bounding_box": [[10, 130], [80, 130], [80, 138], [10, 138]], # h=8px!
            "details": {"has_phone": True},
        }
    }

    engine = RuleEngine()
    result = engine.evaluate(fake_fields, ocr_blocks=fake_ocr_blocks)

    font_eval = result["font_size_assessment"]
    assert font_eval["status"] == "advisory"
    assert font_eval["soft_flags_count"] >= 1
    flag = font_eval["soft_flags"][0]
    assert flag["field"] == "consumer_care_details"
    assert flag["flag_type"] == "soft_flag"
    assert "Possible readability issue" in flag["advisory"]
