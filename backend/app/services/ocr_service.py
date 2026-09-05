"""
OCR Service for LMPC Label Scanner using EasyOCR.
Extracts text chunks, 4-point polygon bounding boxes, and confidence scores.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Singleton EasyOCR reader instance to avoid expensive reloading
_READER_INSTANCE = None


def get_ocr_reader():
    """
    Initializes or returns singleton EasyOCR Reader.
    Checks for CUDA GPU availability and falls back to CPU.
    """
    global _READER_INSTANCE
    if _READER_INSTANCE is None:
        try:
            import easyocr
            import torch
            use_gpu = torch.cuda.is_available()
            logger.info(f"Initializing EasyOCR Reader (GPU={use_gpu})...")
            # Initialize with English
            _READER_INSTANCE = easyocr.Reader(["en"], gpu=use_gpu)
            logger.info("EasyOCR Reader successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise e
    return _READER_INSTANCE


class OCRService:
    def __init__(self):
        self.reader = None

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Runs EasyOCR on the specified image file.

        Args:
            image_path: Absolute or relative path to the image on disk.

        Returns:
            List of detected text blocks, each with format:
            {
                "text": str,
                "bounding_box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
                "confidence": float
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        reader = get_ocr_reader()

        # EasyOCR readtext returns: [(bbox, text, prob), ...]
        raw_results = reader.readtext(image_path)

        text_blocks: List[Dict[str, Any]] = []
        for bbox, text, prob in raw_results:
            # Normalize bounding box coordinates to native python floats
            normalized_bbox = [[round(float(coord[0]), 2), round(float(coord[1]), 2)] for coord in bbox]
            
            cleaned_text = text.strip()
            if cleaned_text:
                text_blocks.append({
                    "text": cleaned_text,
                    "bounding_box": normalized_bbox,
                    "confidence": round(float(prob), 4),
                })

        return text_blocks
