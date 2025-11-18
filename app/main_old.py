# app/main_old.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints import router as api_router
import os
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
STORAGE_DIR = "images"


# 1. Define the lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Code before 'yield' runs on startup (e.g., creating storage directory).
    """

    # --- STARTUP EVENT: Create storage directory ---
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
        print(f"Created storage directory: {STORAGE_DIR}")

    yield  # Application yields control to start processing requests

    # --- SHUTDOWN EVENT (Code after yield runs on shutdown) ---
    print("Application shutting down.")


def create_app():
    application = FastAPI(
        title="Image Processing API",
        description="API for uploading, cropping, and generating paper coordinates.",
        version="1.0.0",
        # 2. Assign the lifespan handler
        lifespan=lifespan
    )
    # Renaming 'app' to 'application' avoids shadowing the module-level 'app'

    # Include the API routes
    application.include_router(api_router, prefix="/api/v1", tags=["Image Processing"])

    @application.get("/")
    def read_root():
        return {"message": "Image Cropping API is running. Go to /docs for documentation."}

    return application


# The module-level 'app' instance is required by Uvicorn (uvicorn app.main:app)
app = create_app()
origins = [
    "http://localhost:8080",  # Default Vue CLI development port
    "http://127.0.0.1:8080",
    # Add your production frontend domain here later
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # List of allowed origins
    allow_credentials=True,             # Allow cookies/authorization headers
    allow_methods=["*"],                # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],                # Allow all headers
)
