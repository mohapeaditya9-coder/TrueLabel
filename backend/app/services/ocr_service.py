"""
OCR Service skeleton for LMPC Label Scanner.
Full implementation with EasyOCR / fallback will be built in Phase 2.
"""

from typing import Dict, Any, List


class OCRService:
    def __init__(self):
        self.reader = None

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text chunks with bounding boxes and confidence scores.
        Skeleton implementation returning placeholder structure.
        """
        return []
