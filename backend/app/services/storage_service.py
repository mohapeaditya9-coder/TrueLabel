import io
import os
import uuid
import hashlib
from typing import Tuple
from PIL import Image

# Maximum allowed file size in bytes (10MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Allowed MIME types and extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Uploads directory resolution (root /uploads or backend/uploads)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)
# Prioritize root /uploads
DEFAULT_UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", DEFAULT_UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class StorageService:
    @staticmethod
    def validate_and_save_image(file_bytes: bytes, original_filename: str) -> Tuple[str, str, str, str]:
        """
        Validates the uploaded file:
        1. Checks maximum file size (10MB)
        2. Validates extension
        3. Verifies image integrity with Pillow
        4. Calculates SHA-256 hash
        5. Saves file to /uploads/{uuid}.{ext} (normalizing jpg/png)

        Returns:
            (scan_id, saved_filename, full_file_path, file_hash)
        """
        # 1. Size check
        file_size = len(file_bytes)
        if file_size == 0:
            raise ValueError("Uploaded file is empty")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum limit of 10MB ({file_size / (1024 * 1024):.2f}MB)")

        # 2. Extension check
        ext = os.path.splitext(original_filename.lower())[1]
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension '{ext}'. Allowed: jpg, jpeg, png, webp")

        # 3. Verify image integrity with Pillow
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Validates image format and magic bytes
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image file: {str(e)}")

        # 4. Compute SHA-256 hash
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # 5. Generate UUID scan_id and save
        scan_id = str(uuid.uuid4())
        # Normalize extension: .jpeg -> .jpg
        norm_ext = ".jpg" if ext in {".jpg", ".jpeg"} else ext
        saved_filename = f"{scan_id}{norm_ext}"
        saved_path = os.path.join(UPLOAD_DIR, saved_filename)

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        return scan_id, saved_filename, saved_path, file_hash
