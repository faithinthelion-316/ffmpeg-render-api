FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /tmp/ffmpeg_render/audio \
    /tmp/ffmpeg_render/video \
    /tmp/ffmpeg_render/fonts \
    /tmp/ffmpeg_render/texts

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
