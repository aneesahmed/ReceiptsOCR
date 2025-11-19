# tests/test_image_api.py

import pytest
from httpx import AsyncClient
import os
from typing import Dict, Any

# Imports must be relative to the project structure
from app.main import app
from app.services.image_service import ImageService


# --- Fixtures ---

@pytest.fixture
async def ac() -> AsyncClient:
    """Provides an asynchronous HTTP client for testing FastAPI routes."""
    # The 'with' block ensures the client is properly closed after tests
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_image_content() -> bytes:
    """Creates mock byte data simulating a small valid PNG file."""
    # Minimal PNG content (1x1 pixel)
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90w\x8b\x9a\x00\x00\x00\x00IEND\xaeB`\x82'


# =========================================================================
# I. Unit Tests for Business Logic (ImageService) - Isolation Check
# =========================================================================

class TestImageService:
    """Tests the core processing logic in ImageService."""

    @pytest.mark.asyncio
    async def test_save_and_process_image_success(self, mock_image_content: bytes):
        """
        Test that the service correctly saves the file and returns a success status.
        """

        # Mock the file structure expected by the service (UploadFile)
        class MockUploadFile:
            filename = "images/invoice1.jpeg"

            # Mock the file.read() method to return the bytes
            async def read(self):
                return mock_image_content

            # Add required attributes for the service to access
            @property
            def file(self):
                return None

        mock_file = MockUploadFile()

        # We call the asynchronous service method directly
        result = await ImageService.image_cropping(file=mock_file)

        assert isinstance(result, dict)
        assert result['status'] == 'Processed and Coordinates Found'
        assert 'saved_filename' in result
        assert result['w'] >= 0

    @pytest.mark.asyncio
    async def test_save_and_process_image_invalid_content(self):
        """Test how the service handles invalid image content."""

        class MockInvalidFile:
            filename = "bad_file.jpg"

            async def read(self):
                return b'junk data'

            @property
            def file(self):
                return None

        result = await ImageService.image_cropping(file=MockInvalidFile())

        assert 'Error: Could not decode image bytes' in result['status']
        assert result['w'] == 0


# =========================================================================
# II. Integration Tests for API Endpoint (HTTP Layer)
# =========================================================================

class TestImageAPI:
    """Tests the single consolidated FastAPI route."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("file_name, mime_type", [
        ("invoice.jpg", "image/jpeg"),
        ("receipt.png", "image/png"),
        ("document.JPEG", "image/jpeg"),
    ])
    async def test_process_image_success(self, ac: AsyncClient, mock_image_content: bytes, file_name: str,
                                         mime_type: str):
        """
        Test POST /api/process_image/ successful response across multiple formats.
        """

        # Create multipart form data payload
        files = {'file': (file_name, mock_image_content, mime_type)}

        response = await ac.post("/api/process_image/", files=files)

        assert response.status_code == 200
        data = response.json()

        # Check Pydantic response structure
        assert 'filename' in data
        assert 'output_filename' in data
        assert data['status'] == 'Processed and Coordinates Found'

        # Check that the output filename is correctly formatted
        base_name, original_ext = os.path.splitext(file_name)
        assert data['output_filename'] == f"{base_name}_cropped{original_ext}"

    @pytest.mark.asyncio
    async def test_process_image_no_file(self, ac: AsyncClient):
        """Test POST /api/process_image/ without the required file."""

        response = await ac.post("/api/process_image/")

        # FastAPI/Starlette returns 422 for validation errors (missing required 'file')
        assert response.status_code == 422
        data = response.json()
        assert 'field required' in data['detail'][0]['msg']