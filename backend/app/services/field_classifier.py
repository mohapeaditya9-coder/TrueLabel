"""
Field Classifier for LMPC Compliance Scanner.
Maps raw OCR text blocks to mandatory declaration fields under Legal Metrology Rules, 2011:
1. manufacturer_name_and_address
2. net_quantity (with unit: g/kg/ml/l/pieces)
3. mrp (Maximum Retail Price, inclusive of taxes check)
4. month_year_of_manufacture_or_import
5. consumer_care_details (phone/email/contact)
6. country_of_origin
7. unit_sale_price (e.g. Rs X per g/kg/ml)
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class FieldClassifier:
    def __init__(self):
        pass

    def classify_blocks(self, ocr_blocks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Takes raw OCR blocks [{text, bounding_box, confidence}, ...]
        and returns structured mapping of the 7 mandatory LMPC declaration fields.

        Output schema per field:
        {
            "value": str or None,
            "found": bool,
            "source_text": str or None,
            "bounding_box": [[x,y],...] or None,
            "confidence": float or None,
            "details": dict (extra parsed tokens)
        }
        """
        if not ocr_blocks:
            return self._empty_results()

        # Build full concatenated text and line index for multi-block search
        results = {
            "manufacturer_name_and_address": self._extract_manufacturer(ocr_blocks),
            "net_quantity": self._extract_net_quantity(ocr_blocks),
            "mrp": self._extract_mrp(ocr_blocks),
            "month_year_of_manufacture_or_import": self._extract_mfg_date(ocr_blocks),
            "consumer_care_details": self._extract_consumer_care(ocr_blocks),
            "country_of_origin": self._extract_country_of_origin(ocr_blocks),
            "unit_sale_price": self._extract_unit_sale_price(ocr_blocks),
        }

        return results

    def _empty_results(self) -> Dict[str, Dict[str, Any]]:
        field_names = [
            "manufacturer_name_and_address",
            "net_quantity",
            "mrp",
            "month_year_of_manufacture_or_import",
            "consumer_care_details",
            "country_of_origin",
            "unit_sale_price",
        ]
        return {
            f: {
                "value": None,
                "found": False,
                "source_text": None,
                "bounding_box": None,
                "confidence": 0.0,
                "details": {},
            }
            for f in field_names
        }

    # =========================================================================
    # 1. MANUFACTURER NAME & ADDRESS
    # =========================================================================
    def _extract_manufacturer(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        mfg_keywords = re.compile(
            r"(?:manufac\w*|mfg|packed|pkd|marketed|mktd|produced|mfd)\s*(?:&|\band\b)?\s*(?:by|at|for|bk)\b",
            re.IGNORECASE,
        )
        address_cues = re.compile(r"(?:ltd|limited|coop|union|pvt|road|rzad|foad|street|plot|sector|po box|box|\b\d{6}\b|india)", re.IGNORECASE)

        # Check single blocks or combined subsequent blocks
        for i, block in enumerate(blocks):
            text = block["text"]
            if mfg_keywords.search(text):
                # Found the indicator. Extract remainder of text or look at adjacent block
                val = mfg_keywords.sub("", text).strip(" :-,")
                matched_blocks = [block]
                
                # If the value in the current block is short, look ahead up to 2 blocks for the address
                if len(val) < 15 and i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    if address_cues.search(next_block["text"]):
                        val = f"{val} {next_block['text']}".strip()
                        matched_blocks.append(next_block)

                if val:
                    return {
                        "value": val,
                        "found": True,
                        "source_text": " | ".join(b["text"] for b in matched_blocks),
                        "bounding_box": self._merge_bounding_boxes([b["bounding_box"] for b in matched_blocks]),
                        "confidence": self._avg_confidence(matched_blocks),
                        "details": {"has_pincode": bool(re.search(r"\b\d{6}\b", val))},
                    }

        # Fallback: look for blocks with Ltd/Limited + Pincode
        for block in blocks:
            text = block["text"]
            if ("ltd" in text.lower() or "limited" in text.lower()) and any(w in text.lower() for w in ["road", "street", "anand", "kolkata", "mumbai", "delhi", "bangalore", "ahmedabad"]):
                return {
                    "value": text,
                    "found": True,
                    "source_text": text,
                    "bounding_box": block["bounding_box"],
                    "confidence": block["confidence"],
                    "details": {"fallback_match": True},
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {},
        }

    # =========================================================================
    # 2. NET QUANTITY
    # =========================================================================
    def _extract_net_quantity(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        qty_pattern = re.compile(
            r"(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|ml|m\.l\.|l|ltr|litre|litres|liter|liters|pieces|pcs|n|units)\b(?:\s*\(([^)]+)\))?",
            re.IGNORECASE,
        )
        keyword_pattern = re.compile(r"\b(?:net\s*(?:qty|quantity|wt|weight|content|volume|contents)|netoty)\b", re.IGNORECASE)

        # 1. Search for block with both keyword and value
        for i, block in enumerate(blocks):
            text = block["text"]
            if keyword_pattern.search(text):
                match = qty_pattern.search(text)
                if match:
                    val = match.group(0).strip()
                    num = float(match.group(1))
                    unit = match.group(2).lower()
                    return {
                        "value": val,
                        "found": True,
                        "source_text": text,
                        "bounding_box": block["bounding_box"],
                        "confidence": block["confidence"],
                        "details": {"magnitude": num, "unit": unit},
                    }
                # If keyword is in current block, check the next block for quantity value
                elif i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    next_match = qty_pattern.search(next_block["text"])
                    if next_match:
                        val = next_match.group(0).strip()
                        num = float(next_match.group(1))
                        unit = next_match.group(2).lower()
                        return {
                            "value": val,
                            "found": True,
                            "source_text": f"{text} {next_block['text']}",
                            "bounding_box": self._merge_bounding_boxes([block["bounding_box"], next_block["bounding_box"]]),
                            "confidence": self._avg_confidence([block, next_block]),
                            "details": {"magnitude": num, "unit": unit},
                        }

        # 2. Fallback: match standalone quantity pattern
        for block in blocks:
            # Exclude unit sale price lines (e.g. Rs 0.55 /g)
            if "price" in block["text"].lower() or "usp" in block["text"].lower() or "/" in block["text"]:
                continue
            match = qty_pattern.search(block["text"])
            if match:
                val = match.group(0).strip()
                num = float(match.group(1))
                unit = match.group(2).lower()
                return {
                    "value": val,
                    "found": True,
                    "source_text": block["text"],
                    "bounding_box": block["bounding_box"],
                    "confidence": block["confidence"],
                    "details": {"magnitude": num, "unit": unit, "standalone": True},
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {},
        }

    # =========================================================================
    # 3. MAXIMUM RETAIL PRICE (MRP)
    # =========================================================================
    def _extract_mrp(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        mrp_keyword = re.compile(r"\b(?:mrp|m\.r\.p|maximum\s*retail\s*price|max\s*retail\s*price)\b", re.IGNORECASE)
        tax_phrasing = re.compile(r"(?:incl\w*|inclusive)[\s.]*(?:of)?[\s.]*(?:all)?[\s.]*tax\w*", re.IGNORECASE)
        price_num_pattern = re.compile(r"(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)

        for i, block in enumerate(blocks):
            text = block["text"]
            if mrp_keyword.search(text):
                matched_blocks = [block]
                combined_text = text
                
                # Check next block if price is separated
                price_match = price_num_pattern.search(text.replace(mrp_keyword.pattern, ""))
                # If price not found or text is just "MRP (INCL OF ALL TAXES)", check next block
                if i + 1 < len(blocks) and not re.search(r"\d{2,}", text):
                    next_block = blocks[i + 1]
                    next_price = price_num_pattern.search(next_block["text"])
                    if next_price and not ("unit" in next_block["text"].lower() or "/" in next_block["text"]):
                        combined_text = f"{combined_text} {next_block['text']}"
                        matched_blocks.append(next_block)

                # Check for tax phrasing in combined text or following block
                has_taxes = bool(tax_phrasing.search(combined_text))
                if not has_taxes and i + 1 < len(blocks):
                    if tax_phrasing.search(blocks[i + 1]["text"]):
                        has_taxes = True
                        matched_blocks.append(blocks[i + 1])

                # Extract numeric amount
                amount = None
                p_match = re.search(r"(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d{1,2})?)", combined_text, re.IGNORECASE)
                if p_match:
                    try:
                        amount = float(p_match.group(1))
                    except ValueError:
                        pass

                return {
                    "value": combined_text.strip(),
                    "found": True,
                    "source_text": combined_text,
                    "bounding_box": self._merge_bounding_boxes([b["bounding_box"] for b in matched_blocks]),
                    "confidence": self._avg_confidence(matched_blocks),
                    "details": {
                        "amount": amount,
                        "includes_taxes_phrase": has_taxes,
                    },
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {"amount": None, "includes_taxes_phrase": False},
        }

    # =========================================================================
    # 4. MONTH & YEAR OF MANUFACTURE / PACKING
    # =========================================================================
    def _extract_mfg_date(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        date_keywords = re.compile(
            r"\b(?:mfg|manufactur\w*|pkd|packed|pkg|packing|phcking|date|batch|bn\d*)\b",
            re.IGNORECASE,
        )
        date_regex = re.compile(
            r"(?:\b\d{1,2}\s*[/.-]\s*)?(0[1-9]|1[0-2]|\d{1,2})\s*[/.-]\s*(20\d{2}|\d{4}|\d{2})\b"
        )

        for i, block in enumerate(blocks):
            text = block["text"]
            if date_keywords.search(text):
                # Search date in current block
                d_match = date_regex.search(text)
                if d_match:
                    return {
                        "value": d_match.group(0).strip(),
                        "found": True,
                        "source_text": text,
                        "bounding_box": block["bounding_box"],
                        "confidence": block["confidence"],
                        "details": {"raw_date": d_match.group(0).strip()},
                    }
                # Check next block
                elif i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    next_d_match = date_regex.search(next_block["text"])
                    if next_d_match:
                        return {
                            "value": next_d_match.group(0).strip(),
                            "found": True,
                            "source_text": f"{text} {next_block['text']}",
                            "bounding_box": self._merge_bounding_boxes([block["bounding_box"], next_block["bounding_box"]]),
                            "confidence": self._avg_confidence([block, next_block]),
                            "details": {"raw_date": next_d_match.group(0).strip()},
                        }

        # Fallback: scan any block containing date format MM/YYYY
        for block in blocks:
            d_match = date_regex.search(block["text"])
            if d_match and "/" in d_match.group(0):
                return {
                    "value": d_match.group(0).strip(),
                    "found": True,
                    "source_text": block["text"],
                    "bounding_box": block["bounding_box"],
                    "confidence": block["confidence"],
                    "details": {"raw_date": d_match.group(0).strip(), "fallback": True},
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {},
        }

    # =========================================================================
    # 5. CONSUMER CARE DETAILS
    # =========================================================================
    def _extract_consumer_care(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        care_keywords = re.compile(
            r"\b(?:consumer|customer|grievance|feedback|complaint|toll\s*free|care\s*cell|care\s*contact|care\s*manager)\b",
            re.IGNORECASE,
        )
        phone_regex = re.compile(r"(?:1800[\s-]?\d{3}[\s-]?\d{3,4}|\b\d{3,5}[\s-]?\d{6,8}\b|\+91[\s-]?\d{10})")
        email_regex = re.compile(r"(?:[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|@amulcoop|@itcin|@tataconsumer|@adaniwilmar)", re.IGNORECASE)

        matched_blocks = []
        found_phone = None
        found_email = None

        # Pass 1: Find indicator block
        start_idx = -1
        for i, block in enumerate(blocks):
            if care_keywords.search(block["text"]):
                start_idx = i
                matched_blocks.append(block)
                break

        # Scan nearby blocks (within 3 blocks of indicator) or all blocks for email/phone
        search_range = range(start_idx, min(start_idx + 4, len(blocks))) if start_idx != -1 else range(len(blocks))

        for i in search_range:
            blk = blocks[i]
            p_match = phone_regex.search(blk["text"])
            if p_match and not found_phone:
                found_phone = p_match.group(0)
                if blk not in matched_blocks:
                    matched_blocks.append(blk)

            e_match = email_regex.search(blk["text"])
            if e_match and not found_email:
                found_email = e_match.group(0)
                if blk not in matched_blocks:
                    matched_blocks.append(blk)

        if matched_blocks:
            full_val = " | ".join(b["text"] for b in matched_blocks)
            return {
                "value": full_val,
                "found": True,
                "source_text": full_val,
                "bounding_box": self._merge_bounding_boxes([b["bounding_box"] for b in matched_blocks]),
                "confidence": self._avg_confidence(matched_blocks),
                "details": {
                    "phone": found_phone,
                    "email": found_email,
                    "has_phone": bool(found_phone),
                    "has_email": bool(found_email),
                },
            }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {"phone": None, "email": None, "has_phone": False, "has_email": False},
        }

    # =========================================================================
    # 6. COUNTRY OF ORIGIN
    # =========================================================================
    def _extract_country_of_origin(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        origin_keywords = re.compile(
            r"\b(?:country\s*of\s*origin|origin|made\s*in|product\s*of)\b",
            re.IGNORECASE,
        )

        for i, block in enumerate(blocks):
            text = block["text"]
            if origin_keywords.search(text):
                matched_blocks = [block]
                val = origin_keywords.sub("", text).strip(" :-,")
                # If value not in same block, check next block
                if not val and i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    val = next_block["text"].strip()
                    matched_blocks.append(next_block)

                if not val:
                    val = "India"  # standard fallback if keyword indicated

                return {
                    "value": val,
                    "found": True,
                    "source_text": " | ".join(b["text"] for b in matched_blocks),
                    "bounding_box": self._merge_bounding_boxes([b["bounding_box"] for b in matched_blocks]),
                    "confidence": self._avg_confidence(matched_blocks),
                    "details": {"country": val},
                }

        # Check if India mentioned in manufacturer block
        for block in blocks:
            if "india" in block["text"].lower() and not ("itc" in block["text"].lower() or "ltd" in block["text"].lower()):
                return {
                    "value": "India",
                    "found": True,
                    "source_text": block["text"],
                    "bounding_box": block["bounding_box"],
                    "confidence": block["confidence"],
                    "details": {"country": "India", "inferred": True},
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {},
        }

    # =========================================================================
    # 7. UNIT SALE PRICE (USP)
    # =========================================================================
    def _extract_unit_sale_price(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        usp_keywords = re.compile(r"\b(?:unit\s*sale\s*(?:price)?|usp)\b", re.IGNORECASE)
        usp_format = re.compile(
            r"(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d{1,2})?)\s*(?:/|per)\s*(g|gm|kg|ml|l|ltr|litre|piece|item|unit)",
            re.IGNORECASE,
        )

        for i, block in enumerate(blocks):
            text = block["text"]
            if usp_keywords.search(text):
                matched_blocks = [block]
                val = text
                # If number and unit are in next block
                match = usp_format.search(text)
                if not match and i + 1 < len(blocks):
                    # Check next 1-2 blocks (sometimes "UNIT SALE" is one block, "PRICE" is next, "Rs. 0.55 /g" is third)
                    for offset in range(1, 3):
                        if i + offset < len(blocks):
                            cand_block = blocks[i + offset]
                            cand_match = usp_format.search(cand_block["text"])
                            matched_blocks.append(cand_block)
                            val = f"{val} {cand_block['text']}"
                            if cand_match:
                                match = cand_match
                                break

                rate = float(match.group(1)) if match else None
                unit = match.group(2).lower() if match else None

                return {
                    "value": val.strip(),
                    "found": True,
                    "source_text": val.strip(),
                    "bounding_box": self._merge_bounding_boxes([b["bounding_box"] for b in matched_blocks]),
                    "confidence": self._avg_confidence(matched_blocks),
                    "details": {"unit_rate": rate, "unit": unit},
                }

        # Fallback: check pattern with Rs X /g or Rs X per kg
        for block in blocks:
            match = usp_format.search(block["text"])
            if match and ("/" in block["text"] or "per" in block["text"]):
                return {
                    "value": block["text"].strip(),
                    "found": True,
                    "source_text": block["text"],
                    "bounding_box": block["bounding_box"],
                    "confidence": block["confidence"],
                    "details": {"unit_rate": float(match.group(1)), "unit": match.group(2).lower(), "fallback": True},
                }

        return {
            "value": None,
            "found": False,
            "source_text": None,
            "bounding_box": None,
            "confidence": 0.0,
            "details": {},
        }

    # =========================================================================
    # Helpers
    # =========================================================================
    def _merge_bounding_boxes(self, bboxes: List[List[List[float]]]) -> Optional[List[List[float]]]:
        """Merges multiple 4-point polygon bounding boxes into an enveloping 4-point bounding box."""
        if not bboxes:
            return None
        all_x = []
        all_y = []
        for box in bboxes:
            if box and len(box) == 4:
                for pt in box:
                    all_x.append(pt[0])
                    all_y.append(pt[1])
        if not all_x or not all_y:
            return None

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        return [
            [round(min_x, 2), round(min_y, 2)],
            [round(max_x, 2), round(min_y, 2)],
            [round(max_x, 2), round(max_y, 2)],
            [round(min_x, 2), round(max_y, 2)],
        ]

    def _avg_confidence(self, blocks: List[Dict[str, Any]]) -> float:
        if not blocks:
            return 0.0
        scores = [b.get("confidence", 0.0) for b in blocks if "confidence" in b]
        return round(sum(scores) / len(scores), 4) if scores else 0.0
