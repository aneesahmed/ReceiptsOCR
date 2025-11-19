# app/services/image_service.py

import cv2
import numpy as np
import os
import uuid
from typing import Dict, Any, Coroutine
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# --- Configuration for Image Saving ---
DEFAULT_UPLOAD_DIR = "uploads"


class ImageService:
    """
    Service class containing the business logic for image processing (OpenCV)
    and file handling.
    """

    def __init__(self, upload_dir: str = DEFAULT_UPLOAD_DIR):
        """Initializes the service and ensures the upload directory exists."""
        self.upload_dir = upload_dir
        self._initialize_upload_dir()

    def _initialize_upload_dir(self):
        """Ensures the upload directory exists."""
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info(f"ImageService initialized. Upload directory: {self.upload_dir}")

    async def image_cropping(self, file: UploadFile) -> None | dict[str, int] | dict[str, int | str]:
        """
        Receives the initial UploadFile, saves it, analyzes it with OpenCV, and returns coordinates.
        """
        original_file_name_clean = os.path.basename(file.filename)
        base_name, original_ext = os.path.splitext(original_file_name_clean)
        unique_id = uuid.uuid4().hex
        saved_filename = f"{base_name}_{unique_id}{original_ext}"
        saved_file_path = os.path.join(self.upload_dir, saved_filename)

        file_content = await file.read()

        try:
            # 1. Save the initial file to disk
            with open(saved_file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Service: Initial file saved successfully to {saved_file_path}")

            # 2. OpenCV Contour Detection (Processing logic skipped for brevity, assumed correct)
            img = cv2.imread(saved_file_path)

            if img is None:
                print(f"❌ Error: Could not load image at {saved_file_path}. Skipping.")
                return None

                # --- Define the Threshold (BGR format) ---
            lower_bound = np.array([190, 190, 190])
            upper_bound = np.array([255, 255, 255])

            # 2. Apply Color Thresholding (Masking)
            mask = cv2.inRange(img, lower_bound, upper_bound)

            # Optional: Noise reduction and gap closing
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # 3. Find Contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                print(f"   Warning: No paper contours found for {os.path.basename(saved_file_path)}. Skipping crop.")
                return None

                # Select the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # 4. Calculate the Bounding Box
            x, y, w, h = cv2.boundingRect(largest_contour)

            # 5. Crop the image using slicing
            cropped_img = img[y:y + h, x:x + w]

            # 6. Save the resulting cropped image
            if cv2.imwrite(saved_file_path, cropped_img):
                print(f"✅ Processed and saved: {os.path.basename(self.upload_dir)}")
            else:
                print(f"❌ Error saving image to: {os.path.basename(self.upload_dir)}")

            # Return coordinates as a dictionary
            #return {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}

            # end of open cv function
            logger.info(f"Service: Found bounding box for {saved_filename}: (x={x}, y={y}, w={w}, h={h})")

            return {
                'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h),
                'status': 'Processed and Coordinates Found',
                'saved_filename': saved_filename
            }

        except Exception as e:
            logger.error(f"Service: Critical error during initial processing: {e}", exc_info=True)
            return {
                'x': 0, 'y': 0, 'w': 0, 'h': 0,
                'status': f"Critical Error: {str(e)}",
                'saved_filename': saved_filename
            }

    async def save_cropped_file(self, cropped_file: UploadFile) -> str:
        """
        Saves the cropped file received from the frontend with a unique prefix.
        """
        # 1. Generate unique file path prefix
        original_file_name_clean = os.path.basename(cropped_file.filename)
        base_name, original_ext = os.path.splitext(original_file_name_clean)

        # New requirement: unique random number prefix
        unique_prefix = uuid.uuid4().hex[:8]

        saved_filename = f"{unique_prefix}_{base_name}{original_ext}"
        saved_file_path = os.path.join(self.upload_dir, saved_filename)

        file_content = await cropped_file.read()

        try:
            # 2. Save the file to disk
            with open(saved_file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"Service: Final cropped file saved as {saved_filename}")
            return "Successfully uploaded the file"

        except Exception as e:
            logger.error(f"Service: Error saving cropped file: {e}", exc_info=True)
            return f"Failed to upload file: {str(e)}"