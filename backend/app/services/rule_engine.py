"""
Rule Engine for Legal Metrology (Packaged Commodities) Rules, 2011.

PURE CONFIG-DRIVEN VALIDATOR:
- Zero OCR, CV, or database code inside this engine.
- Pure JSON in, JSON out.
- Driven entirely by /rules/compliance_rules.json.
- Non-programmers can add, modify, or tune rules without altering Python source code.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            # Look in backend/app/rules or root rules/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_app_rules = os.path.join(os.path.dirname(current_dir), "rules", "compliance_rules.json")
            root_rules = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "rules", "compliance_rules.json")

            if os.path.exists(backend_app_rules):
                rules_path = backend_app_rules
            elif os.path.exists(root_rules):
                rules_path = root_rules
            else:
                rules_path = backend_app_rules

        self.rules_path = rules_path
        self.rules_config = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if os.path.exists(self.rules_path):
            with open(self.rules_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception as e:
                    logger.error(f"Failed to parse rules JSON from {self.rules_path}: {e}")
                    return {"rules": []}
        return {"rules": []}

    def evaluate(
        self,
        classified_fields: Dict[str, Any],
        ocr_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Validates classified declarations against JSON rules.

        Args:
            classified_fields: { field_name: { value, found, source_text, bounding_box, confidence, details } }
            ocr_blocks: Optional raw OCR blocks for relative font size analysis.

        Returns:
            {
                "overall_status": "compliant" | "non_compliant",
                "compliance_score": float,
                "total_mandatory_rules": int,
                "passed_rules_count": int,
                "violations_count": int,
                "violations": [
                    {
                        "field": str,
                        "rule_id": str,
                        "violation_type": "missing" | "incorrect_format" | "illegible" | "misplaced",
                        "description": str,
                        "severity": "CRITICAL" | "MAJOR" | "MINOR",
                        "legal_reference": str
                    }
                ],
                "passed_fields": [str, ...],
                "font_size_assessment": {
                    "method": "relative_bounding_box_height",
                    "status": "advisory",
                    "soft_flags": [...],
                    "limitation_note": str
                }
            }
        """
        rules = self.rules_config.get("rules", [])
        violations: List[Dict[str, Any]] = []
        passed_fields: List[str] = []

        for rule in rules:
            field_name = rule["field"]
            field_data = classified_fields.get(field_name, {})
            found = field_data.get("found", False)
            value = field_data.get("value")
            details = field_data.get("details", {})
            rule_id = rule.get("rule_id", f"RULE-{field_name}")
            legal_ref = rule.get("legal_reference", "LMPC Rules, 2011")
            severity = rule.get("severity", "MAJOR")
            check_type = rule.get("check_type", "presence")

            # 1. Presence Check
            if rule.get("mandatory", False) and not found:
                violations.append({
                    "field": field_name,
                    "rule_id": rule_id,
                    "violation_type": "missing",
                    "description": rule.get("violation_if_missing", f"{field_name} declaration missing."),
                    "severity": severity,
                    "legal_reference": legal_ref,
                })
                continue

            # If field is optional and not found, it's not a violation
            if not found:
                continue

            # 2. Format & Phrasing Checks
            field_has_violation = False

            if check_type == "presence_and_phrase":
                phrase = rule.get("must_contain_phrase", "inclusive of all taxes").lower()
                has_phrase = details.get("includes_taxes_phrase", False)
                if not has_phrase and phrase not in (value or "").lower():
                    violations.append({
                        "field": field_name,
                        "rule_id": rule_id,
                        "violation_type": "incorrect_format",
                        "description": rule.get("violation_if_format_wrong", f"Field missing required phrase '{phrase}'."),
                        "severity": severity,
                        "legal_reference": legal_ref,
                    })
                    field_has_violation = True

            elif check_type == "presence_and_format":
                # Check unit / regex
                allowed_units = rule.get("allowed_units")
                if allowed_units and "unit" in details:
                    unit = details.get("unit")
                    if unit and unit.lower() not in [u.lower() for u in allowed_units]:
                        violations.append({
                            "field": field_name,
                            "rule_id": rule_id,
                            "violation_type": "incorrect_format",
                            "description": rule.get("violation_if_format_wrong", f"Invalid unit '{unit}'."),
                            "severity": severity,
                            "legal_reference": legal_ref,
                        })
                        field_has_violation = True

                fmt_regex = rule.get("format_regex")
                if fmt_regex and value:
                    if not re.search(fmt_regex, value, re.IGNORECASE):
                        violations.append({
                            "field": field_name,
                            "rule_id": rule_id,
                            "violation_type": "incorrect_format",
                            "description": rule.get("violation_if_format_wrong", "Invalid declaration format."),
                            "severity": severity,
                            "legal_reference": legal_ref,
                        })
                        field_has_violation = True

            elif check_type == "presence_and_contact":
                # Consumer care must contain telephone and/or email
                has_phone = details.get("has_phone", False)
                has_email = details.get("has_email", False)
                if not has_phone and not has_email:
                    violations.append({
                        "field": field_name,
                        "rule_id": rule_id,
                        "violation_type": "incorrect_format",
                        "description": rule.get("violation_if_format_wrong", "Contact details must include phone or email."),
                        "severity": severity,
                        "legal_reference": legal_ref,
                    })
                    field_has_violation = True

            if not field_has_violation:
                passed_fields.append(field_name)

        # Compute compliance status
        critical_or_major_count = sum(1 for v in violations if v["severity"] in {"CRITICAL", "MAJOR"})
        overall_status = "non_compliant" if critical_or_major_count > 0 else "compliant"

        total_rules = len(rules)
        passed_count = len(passed_fields)
        score = round((passed_count / max(total_rules, 1)) * 100, 1)

        # 3. Best-Effort Relative Font Size Estimation Check
        font_assessment = self._assess_relative_font_sizes(classified_fields, ocr_blocks)

        return {
            "overall_status": overall_status,
            "compliance_score": score,
            "total_mandatory_rules": total_rules,
            "passed_rules_count": passed_count,
            "violations_count": len(violations),
            "violations": violations,
            "passed_fields": passed_fields,
            "font_size_assessment": font_assessment,
        }

    # =========================================================================
    # Best-Effort Font Size Estimation
    # =========================================================================
    def _assess_relative_font_sizes(
        self,
        classified_fields: Dict[str, Any],
        ocr_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Estimates relative font heights from bounding boxes.

        DISCLAIMER / METHODOLOGY:
        Without a physical scale reference (e.g. coin, calibration fiducial, or known camera distance),
        pixel bounding boxes cannot be converted to physical millimeters.
        Instead, we calculate the median bounding box height of text blocks on the label.
        Text blocks that fall significantly below the median (< 40% of median height) are
        flagged with an ADVISORY 'soft flag' for manual inspection.
        """
        soft_flags: List[Dict[str, Any]] = []

        # Collect box heights
        heights = []
        if ocr_blocks:
            for b in ocr_blocks:
                h = self._get_box_height(b.get("bounding_box"))
                if h and h > 2.0:
                    heights.append(h)

        # Fallback to classified field bounding boxes if ocr_blocks not provided
        if not heights:
            for f_data in classified_fields.values():
                h = self._get_box_height(f_data.get("bounding_box"))
                if h and h > 2.0:
                    heights.append(h)

        if not heights:
            return {
                "status": "advisory",
                "method": "relative_bounding_box_height",
                "median_height_px": None,
                "soft_flags": [],
                "limitation_note": (
                    "No physical calibration target present in image. In production, a physical reference "
                    "(e.g., standard fiducial marker or fixed camera calibration) is required to certify "
                    "exact mm numeral height under Rule 9."
                ),
            }

        heights.sort()
        median_h = heights[len(heights) // 2]
        threshold = median_h * 0.40  # Flag if less than 40% of median height

        # Check each mandatory classified field
        for field_name, f_data in classified_fields.items():
            if not f_data.get("found"):
                continue
            box = f_data.get("bounding_box")
            box_h = self._get_box_height(box)
            if box_h and box_h < threshold:
                soft_flags.append({
                    "field": field_name,
                    "estimated_box_height_px": round(box_h, 1),
                    "label_median_height_px": round(median_h, 1),
                    "ratio_to_median": round(box_h / median_h, 2),
                    "flag_type": "soft_flag",
                    "advisory": (
                        f"Possible readability issue on '{field_name}' — text height ({box_h:.1f}px) is "
                        f"disproportionately small relative to median label text ({median_h:.1f}px). Verify physical packaging manually."
                    ),
                })

        return {
            "status": "advisory",
            "method": "relative_bounding_box_height",
            "label_median_height_px": round(median_h, 1),
            "soft_flags_count": len(soft_flags),
            "soft_flags": soft_flags,
            "limitation_note": (
                "Relative heuristic estimate: Flags text blocks that are disproportionately small (<40% of median text height). "
                "Precise physical millimeter verification under Rule 9 requires a calibrated physical reference scale in the capture photo."
            ),
        }

    @staticmethod
    def _get_box_height(box: Optional[List[List[float]]]) -> Optional[float]:
        if not box or len(box) != 4:
            return None
        # box: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # height = (y3 - y2 + y4 - y1) / 2
        try:
            h = abs(box[2][1] - box[1][1] + box[3][1] - box[0][1]) / 2.0
            return h if h > 0 else abs(box[2][1] - box[0][1])
        except Exception:
            return None
