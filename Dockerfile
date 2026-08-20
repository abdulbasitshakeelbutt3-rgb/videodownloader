FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Install python packages directly in Dockerfile to prevent any missing dependency errors
RUN pip install --no-cache-dir fastapi uvicorn yt-dlp pydantic

# Copy the rest of the application files
COPY . .

# Run uvicorn binding to Railway's dynamic PORT
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"