from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import os
import shutil

from app.services import image_processor as svc
from app.schemas.coordinate import CoordinateResponse

router = APIRouter()


@router.post(
    "/process-image",
    response_model=CoordinateResponse,
    status_code=status.HTTP_201_CREATED
)
async def process_image(file: UploadFile = File(...)):
    """
    Receives an image, saves original and cropped versions with unique names,
    and returns the bounding box coordinates.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only JPEG and PNG are allowed."
        )

    # 1. Get unique filenames
    original_save_name, cropped_save_name, _ = svc.get_unique_filenames(file.filename)

    # Read file content
    content = await file.read()

    # 2. Process image and save files
    coordinates, success = svc.find_paper_and_crop(
        content,
        original_save_name,
        cropped_save_name
    )

    # 3. Prepare response
    return CoordinateResponse(
        filename_original=original_save_name,
        filename_cropped=cropped_save_name,
        **coordinates  # Unpacks x, y, w, h, and status
    )