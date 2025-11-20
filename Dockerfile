# Use Python 3.11 (Stable for ML/OpenCV)
FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Install System Dependencies
# 'build-essential' is REQUIRED for pillow-heif
# 'libgl1' & 'libglib2.0-0' are REQUIRED for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Virtual Environment
ENV VIRTUAL_ENV=/opt/receiptocr
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 3. Install Python Libraries
# Added 'python-multipart' to the list below
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    httpx \
    numpy \
    Pillow \
    pillow-heif \
    pydantic \
    pytest \
    uvicorn \
    python-multipart \
    opencv-python-headless

# 4. Application Setup
WORKDIR /app
COPY . .

EXPOSE 8000

# NOTE: If your main.py is inside a folder named 'app', keep "app.main:app"
# If main.py is in the root, use "main:app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]