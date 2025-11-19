from pydantic import BaseModel
from typing import Optional

# 1. Response model for initial coordinate finding (API Response: /submit_image/)
# Note: Uses 'w' and 'h' as these match the OpenCV output names directly.
class CoordinatesResponse(BaseModel):
    """
    Schema for the response after initial image processing by OpenCV,
    containing the suggested bounding box coordinates.
    """
    filename: str
    output_filename: str
    x: int
    y: int
    w: int
    h: int
    status: str

# 2. Input model for final cropped data submission (API Request: /submit_cropped_data/)
# Note: Uses 'width' and 'height' as this matches the Cropper.js output property names.
class CropSubmission(BaseModel):
    """
    Schema for the request body sent by the frontend after user interaction
    with Cropper.js, containing the final crop box data.
    """
    x: float
    y: float
    width: float
    height: float
    rotate: float
    scaleX: float
    scaleY: float
    originalFileName: str
    targetEndpoint: str