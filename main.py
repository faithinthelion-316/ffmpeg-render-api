from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import textwrap
import shutil

app = FastAPI()

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/render")
async def render_video(
    numero_regla: str = Form(...),
    guion: str = Form(...),
    subtitles_mode: str = Form("static"),
    audio_file: UploadFile = File(...)
):  
    job_id = str(uuid.uuid4())
    audio_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    text_path = os.path.join(OUTPUT_DIR, f"{job_id}.txt")

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    wrapped = textwrap.fill(guion, width=28)
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
            f"text='#{numero_regla}':fontcolor=red:fontsize=72:x=(w-text_w)/2:y=310,"
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
        "subtitles_mode_received": subtitles_mode
    }

@app.get("/video/{job_id}")
def get_video(job_id: str):
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{job_id}.mp4")
