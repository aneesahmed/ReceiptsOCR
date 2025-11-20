# app/services/image_service.py

import cv2
import numpy as np
import os
import uuid
import logging
from typing import Tuple, Optional, Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# --- Configuration ---
DEFAULT_UPLOAD_DIR = "uploads"


class ImageService:
    """
    Service class responsible for handling image uploads,
    processing (OpenCV), and file management.
    """

    def __init__(self, upload_dir: str = DEFAULT_UPLOAD_DIR):
        self.upload_dir = upload_dir
        self._initialize_upload_dir()

    def _initialize_upload_dir(self) -> None:
        """Ensures the upload directory exists."""
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info(f"ImageService initialized. Upload directory: {self.upload_dir}")

    # ==========================================
    # Public API Methods
    # ==========================================

    async def image_cropping(self, file: UploadFile) -> Dict[str, Any]:
        """
        Main Orchestrator: Receives file, saves it, crops it via OpenCV,
        overwrites the file, and returns coordinates.
        """
        try:
            # 1. Generate path and Save Initial File
            filename, file_path = await self._save_initial_upload(file)

            # 2. Load Image with OpenCV
            img = self._load_cv2_image(file_path)
            if img is None:
                return self._error_response("Could not load image", filename)

            # 3. Calculate Crop Coordinates (The Vision Logic)
            coordinates = self._get_crop_coordinates(img)
            if not coordinates:
                logger.warning(f"No contours found for {filename}")
                return self._error_response("No contours found", filename)

            # 4. Crop and Save (Overwrite)
            x, y, w, h = coordinates
            success = self._crop_and_overwrite(img, file_path, x, y, w, h)

            if not success:
                return self._error_response("Failed to save cropped image", filename)

            logger.info(f"Success: Processed {filename}. Coords: {coordinates}")

            return {
                'x': x, 'y': y, 'w': w, 'h': h,
                'status': 'Processed and Coordinates Found',
                'saved_filename': filename
            }

        except Exception as e:
            logger.error(f"Service: Critical error: {e}", exc_info=True)
            return self._error_response(str(e))

    async def save_cropped_file(self, cropped_file: UploadFile) -> str:
        """
        Saves a pre-cropped file received from frontend with a unique prefix.
        """
        try:
            unique_prefix = uuid.uuid4().hex[:8]
            clean_name = os.path.basename(cropped_file.filename)
            saved_filename = f"{unique_prefix}_{clean_name}"
            saved_file_path = os.path.join(self.upload_dir, saved_filename)

            await self._write_bytes_to_disk(cropped_file, saved_file_path)

            logger.info(f"Service: Final cropped file saved as {saved_filename}")
            return "Successfully uploaded the file"

        except Exception as e:
            logger.error(f"Service: Error saving final file: {e}", exc_info=True)
            return f"Failed to upload file: {str(e)}"

    # ==========================================
    # Internal Helper Methods (Private)
    # ==========================================

    async def _save_initial_upload(self, file: UploadFile) -> Tuple[str, str]:
        """Generates a unique name and saves the raw bytes to disk."""
        base_name, ext = os.path.splitext(os.path.basename(file.filename))
        unique_id = uuid.uuid4().hex
        saved_filename = f"{base_name}_{unique_id}{ext}"
        saved_file_path = os.path.join(self.upload_dir, saved_filename)

        await self._write_bytes_to_disk(file, saved_file_path)
        logger.info(f"Service: Initial file saved to {saved_file_path}")

        return saved_filename, saved_file_path

    async def _write_bytes_to_disk(self, file: UploadFile, path: str) -> None:
        """Low-level helper to write UploadFile bytes to disk."""
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)

    def _load_cv2_image(self, path: str) -> Optional[np.ndarray]:
        """Loads an image from disk using OpenCV."""
        return cv2.imread(path)

    def _get_crop_coordinates(self, img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Pure Business Logic: Applies masks and finds the largest contour.
        Returns (x, y, w, h) or None.
        """
        # Define Threshold (White paper detection)
        lower_bound = np.array([190, 190, 190])
        upper_bound = np.array([255, 255, 255])

        # Apply Mask
        mask = cv2.inRange(img, lower_bound, upper_bound)

        # Noise reduction
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        return int(x), int(y), int(w), int(h)

    def _crop_and_overwrite(self, img: np.ndarray, path: str, x: int, y: int, w: int, h: int) -> bool:
        """Crops the numpy array and overwrites the file on disk."""
        cropped_img = img[y:y + h, x:x + w]
        return cv2.imwrite(path, cropped_img)

    def _error_response(self, message: str, filename: str = "") -> Dict[str, Any]:
        """Standardized error return structure."""
        return {
            'x': 0, 'y': 0, 'w': 0, 'h': 0,
            'status': f"Error: {message}",
            'saved_filename': filename
        }