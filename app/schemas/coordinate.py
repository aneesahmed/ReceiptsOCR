from pydantic import BaseModel

class CoordinateResponse(BaseModel):
    """Schema for the coordinate response."""
    filename_original: str
    filename_cropped: str
    status: str
    # Bounding Box Coordinates (Top-Left corner + Width/Height)
    x: int
    y: int
    w: int
    h: int