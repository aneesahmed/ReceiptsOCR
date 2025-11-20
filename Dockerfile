# Use the official Python 3.13 slim image (lighter and secure)
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure logs are output immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------------
# 1. Install System Dependencies (Required for OpenCV)
# --------------------------------------------------------
# Even the headless version of OpenCV requires GLIB dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# 2. Create and "Activate" Virtual Environment
# --------------------------------------------------------
# We create the venv in /opt/receiptocr to keep it distinct from code.
ENV VIRTUAL_ENV=/opt/receiptocr
RUN python -m venv $VIRTUAL_ENV

# CRITICAL STEP: To "activate" the venv in Docker, we simply prepend
# its bin directory to the system PATH. All future commands will now
# use the pip and python executables inside 'receiptocr'.
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# --------------------------------------------------------
# 3. Install Python Libraries
# --------------------------------------------------------
# We upgrade pip first, then install the requested packages.
# Note: Using 'opencv-python-headless' is best practice for EC2/Servers.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    httpx \
    numpy \
    Pillow \
    pydantic \
    pytest \
    uvicorn \
    opencv-python-headless \
    pillow_heif

# --------------------------------------------------------
# 4. Application Setup
# --------------------------------------------------------
WORKDIR /app

# Copy your local code to the container
COPY . .

# Expose the port (standard for FastAPI)
EXPOSE 8000

# Default command to run the app
# Change 'main:app' to match your file name (e.g., if your file is api.py, use api:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]