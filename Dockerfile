FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn yt-dlp pydantic

COPY . .

# Use python to run uvicorn directly with dynamic port
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}