# Keep using 3.11 (Stable for image processing libraries)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------------
# 1. Install System Dependencies
# --------------------------------------------------------
# We added 'build-essential' (gcc/make) to allow compiling C extensions
# We added 'libgl1' & 'libglib2.0-0' for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# 2. Setup Virtual Environment
# --------------------------------------------------------
ENV VIRTUAL_ENV=/opt/receiptocr
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# --------------------------------------------------------
# 3. Install Python Libraries
# --------------------------------------------------------
# Upgrade pip first (CRITICAL: helps find the correct binary wheels)
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
    opencv-python-headless

# --------------------------------------------------------
# 4. Application Setup
# --------------------------------------------------------
WORKDIR /app
COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]