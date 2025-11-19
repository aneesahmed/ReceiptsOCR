import cv2
import numpy as np
import os
from fastapi import UploadFile
from typing import Tuple, Dict, Any

# --- Configuration ---
STORAGE_DIR = "uploads"
RGB_LOWER_BOUND = np.array([190, 190, 190])
RGB_UPPER_BOUND = np.array([255, 255, 255])
CROP_SUFFIX = "_processed"


def get_unique_filenames(original_filename: str) -> Tuple[str, str, str]:
    """Generates unique names for original and cropped files."""
    name, ext = os.path.splitext(original_filename)
    unique_suffix = os.urandom(4).hex()  # 8-character unique hex

    # Filenames for saving
    original_save_name = f"{name}_{unique_suffix}{ext}"
    cropped_save_name = f"{name}{CROP_SUFFIX}_{unique_suffix}{ext}"

    return original_save_name, cropped_save_name, ext


def find_paper_and_crop(
        file_content: bytes,
        original_filename: str,
        cropped_filename: str
) -> Tuple[Dict[str, Any], bool]:
    """
    Core function: Saves original, finds bounding box, saves cropped,
    and returns coordinates.
    """
    # 1. Convert file content to OpenCV image
    nparr = np.frombuffer(file_content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "Error: Could not decode image.", "x": 0, "y": 0, "w": 0, "h": 0}, False

    # --- 2. Image Processing Logic (Same as your initial request) ---

    # Apply Color Thresholding (Masking)
    mask = cv2.inRange(img, RGB_LOWER_BOUND, RGB_UPPER_BOUND)

    # Noise reduction and gap closing
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find Contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return {"status": "Warning: No paper contours found.", "x": 0, "y": 0, "w": 0, "h": 0}, False

    # Select the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate the Bounding Box
    x, y, w, h = cv2.boundingRect(largest_contour)

    # 3. Crop and Save Logic

    # Save Original Image
    cv2.imwrite(os.path.join(STORAGE_DIR, original_filename), img)

    # Crop Image
    cropped_img = img[y:y + h, x:x + w]

    # Save Cropped Image
    cv2.imwrite(os.path.join(STORAGE_DIR, cropped_filename), cropped_img)

    # 4. Return Coordinates
    coordinates = {
        "status": "Success",
        "x": int(x),
        "y": int(y),
        "w": int(w),
        "h": int(h)
    }
    return coordinates, True