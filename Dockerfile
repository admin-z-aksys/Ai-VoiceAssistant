# Use a slim, production-ready Python base
FROM python:3.11-slim

# System deps for audio & builds (ffmpeg for pydub/processing, libsndfile for soundfile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    ffmpeg \
    libsndfile1 \
    git \
 && rm -rf /var/lib/apt/lists/*

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Workdir at repo root (which contains the api/ folder)
WORKDIR /app

# Leverage Docker layer caching for deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python -m nltk.downloader averaged_perceptron_tagger_eng punkt -d /usr/local/nltk_data

# Copy the rest of the code
COPY . .

# (Optional) quick sanity import to fail fast at build time
# RUN python -c "import importlib; importlib.import_module('api.app'); print('api.app import OK')"

# Use Render's PORT if present; default to 8000 locally
CMD ["bash", "-lc", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
