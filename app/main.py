# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
import os
# FIX: Import Dict from typing along with Optional
from typing import Optional, Dict
from app.services.image_service import ImageService
from app.models.image_models import CoordinatesResponse

# --- Configuration: Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration: Environment Variable ---
API_BASE_URL = "http://localhost:8000"

# --- FastAPI App Instance ---
app = FastAPI(title="Vue-FastAPI Cropping App (Final)")
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Allow all origins
    allow_credentials=True,        # Allow cookies/auth headers (if needed)
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],           # Allow all headers
)

# --- Initialize Service Instance ---
image_service_instance = ImageService()
logger.info("ImageService instance created outside of routing.")


# Dependency function to provide the shared ImageService instance
def get_image_service() -> ImageService:
    """Provides the pre-instantiated ImageService instance."""
    return image_service_instance


# ====================================================================
# I. Endpoint Functions
# ====================================================================

@app.post("/api/process_image/", response_model=CoordinatesResponse)
async def process_image_and_get_coords(
        file: UploadFile = File(...),
        service: ImageService = Depends(get_image_service)
) -> CoordinatesResponse:
    logger.info(f"Received request to process and save initial image: {file.filename}")

    process_result = await service.image_cropping(file)

    original_filename = file.filename
    base_name, original_ext = os.path.splitext(original_filename)
    output_filename_display = f"{base_name}_cropped{original_ext}"

    logger.info(f"Processing complete. Status: {process_result.get('status', 'Failed')}")

    return CoordinatesResponse(
        filename=original_filename,
        output_filename=output_filename_display,
        x=process_result.get('x', 0),
        y=process_result.get('y', 0),
        w=process_result.get('w', 0),
        h=process_result.get('h', 0),
        status=process_result.get('status', 'Processing Failed')
    )


@app.post("/api/submit_cropped_image/")
async def submit_cropped_image(
        cropped_file: UploadFile = File(...),
        service: ImageService = Depends(get_image_service)
) -> Dict[str, str]:
    """
    New endpoint to receive the final cropped image file and save it uniquely.
    """
    logger.info(f"Received final cropped image file: {cropped_file.filename}")

    # Call the service method to save the file
    message = await service.save_cropped_file(cropped_file)

    logger.info(f"Cropped image submission result: {message}")

    return {"message": message}


# --- Static File Serving and Root Route ---

@app.get("/", response_class=HTMLResponse)
async def default():
    return "hello receiptocr , ip:8000/docs"
# --- Uvicorn Startup ---

if __name__ == "__main__":
    logger.info("Starting Uvicorn server.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)