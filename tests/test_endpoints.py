import pytest
from httpx import Client
from app.main_old import app
from app.services.image_processor import STORAGE_DIR
import os
import shutil


# --- Setup Fixture ---
@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance for making requests."""
    # The TestClient automatically handles the 'lifespan' events (startup/shutdown)
    with Client(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def cleanup_storage():
    """Cleans up the storage directory before and after tests."""
    # Ensure directory exists before tests run
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    yield  # Run the test

    # Cleanup: Remove all files created during the test
    for filename in os.listdir(STORAGE_DIR):
        file_path = os.path.join(STORAGE_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


# --- Test Data (A simple 100x100 white square on black background) ---

# Create a small, valid JPEG file content in memory for testing file uploads
def create_test_image_content():
    """Creates dummy JPEG content (a minimal valid image)."""
    from PIL import Image
    from io import BytesIO

    img = Image.new('RGB', (100, 100), color='white')
    buffer = BytesIO()
    img.save(buffer, format="jpeg")
    buffer.seek(0)
    return buffer.read()


# --- Test Functions ---

def test_root_endpoint(client: Client):
    """Tests the basic health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Image Cropping API is running. Go to /docs for documentation."}


def test_successful_image_processing(client: Client):
    """Tests a successful file upload and processing."""

    # Generate test image data
    image_content = create_test_image_content()

    files = {'file': ('test_paper.jpeg', image_content, 'image/jpeg')}
    response = client.post("/api/v1/process-image", files=files)

    data = response.json()

    # 1. Check HTTP Status
    assert response.status_code == 201

    # 2. Check Coordinate Structure and Success Status
    assert data["status"] == "Success"
    assert all(k in data for k in ["x", "y", "w", "h"])

    # For a simple white square image, the coordinates should be roughly the whole image (x=0, y=0, w=100, h=100)
    # Since compression/padding might shift things slightly, we check for reasonable size.
    assert data["w"] > 90  # Width should be close to 100
    assert data["h"] > 90  # Height should be close to 100

    # 3. Check File Persistence (Both original and cropped should be saved)
    original_file_exists = os.path.exists(os.path.join(STORAGE_DIR, data["filename_original"]))
    cropped_file_exists = os.path.exists(os.path.join(STORAGE_DIR, data["filename_cropped"]))

    assert original_file_exists
    assert cropped_file_exists


def test_unsupported_file_type(client: Client):
    """Tests an upload with a file type that is not supported (e.g., text file)."""

    # Create dummy text file content
    text_content = b"This is not an image."

    files = {'file': ('test.txt', text_content, 'text/plain')}
    response = client.post("/api/v1/process-image", files=files)

    # Expect HTTP 415 Unsupported Media Type
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


def test_empty_file_upload(client: Client):
    """Tests an upload with an empty file."""

    empty_content = b""
    files = {'file': ('empty.jpeg', empty_content, 'image/jpeg')}
    response = client.post("/api/v1/process-image", files=files)

    # Expect failure due to OpenCV inability to decode
    assert response.status_code == 201
    assert response.json()["status"].startswith("Error: Could not decode image.")

# --- Command to Run Tests ---
# Execute from the project root:
# pytest