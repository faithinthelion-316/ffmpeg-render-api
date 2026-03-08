from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import uuid
import os
import textwrap
import requests

app = FastAPI()

class RenderRequest(BaseModel):
    numero_regla: str
    guion: str
    audio_url: str

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/render")
def render_video(data: RenderRequest):
    job_id = str(uuid.uuid4())
    audio_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    text_path = os.path.join(OUTPUT_DIR, f"{job_id}.txt")

    r = requests.get(data.audio_url, timeout=60)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="No se pudo descargar el audio")

    with open(audio_path, "wb") as f:
        f.write(r.content)

    wrapped = textwrap.fill(data.guion, width=28)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(wrapped)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:r=30",
        "-i", audio_path,
        "-vf",
        (
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "text='REGLA INVISIBLE':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=220,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='#{data.numero_regla}':fontcolor=red:fontsize=72:x=(w-text_w)/2:y=310,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"textfile='{text_path}':fontcolor=white:fontsize=52:line_spacing=18:"
            "x=(w-text_w)/2:y=(h-text_h)/2"
        ),
        "-shortest",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    return {
        "ok": True,
        "video_url": f"/video/{job_id}"
    }

@app.get("/video/{job_id}")
def get_video(job_id: str):
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{job_id}.mp4")
