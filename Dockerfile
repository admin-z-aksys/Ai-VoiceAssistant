# ── Dockerfile ──────────────────────────────────────────────────────────────
# Use a lightweight official Python base image
FROM python:3.11-slim

# Install system dependencies needed for Coqui TTS phonemizer
#  - espeak-ng provides the phoneme backend
#  - libsndfile1 is often required for audio I/O
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        espeak-ng \
        libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy only the requirements first (for better build caching)
COPY requirements.txt .

# Install Python deps (use --no-cache-dir to keep the image small)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your source code
COPY . .

# Expose the port that Uvicorn will listen on
EXPOSE 8000

# Start the FastAPI app (adjust path if app.py lives inside /api)
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
# ────────────────────────────────────────────────────────────────────────────
