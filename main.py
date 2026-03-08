import os
import uuid
import subprocess
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(_file_))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


def chunk_text(text: str, words_per_chunk: int = 3) -> List[str]:
    words = text.replace("\n", " ").replace("\r", " ").split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk]).strip()
        if chunk:
            chunks.append(chunk.upper())
    return chunks


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-show_entries",
        "format=duration",
        "-of",
        "csv=p=0",
        audio_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        duration = float(result.stdout.strip())
        return max(duration, 1.0)
    except Exception:
        return 5.0


def build_drawtext_filters(chunks: List[str], audio_duration: float, numero_regla: str) -> str:
    font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail="No se encontró la fuente BebasNeue-Regular.ttf en la carpeta fonts"
        )

    duration_per_chunk = audio_duration / max(len(chunks), 1)

    title_text = f"REGLA INVISIBLE #{numero_regla}"
    title_text = title_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")

    filters = [
        (
            f"drawtext="
            f"fontfile='{font_path}':"
            f"text='{title_text}':"
            f"fontsize=64:"
            f"fontcolor=white:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.12"
        )
    ]

    for i, chunk in enumerate(chunks):
        start = round(i * duration_per_chunk, 3)
        end = round(start + duration_per_chunk, 3)

        txt = chunk.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")

        draw = (
            f"drawtext="
            f"fontfile='{font_path}':"
            f"text='{txt}':"
            f"fontsize=72:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.78:"
            f"enable='between(t,{start},{end})'"
        )
        filters.append(draw)

    return ",".join(filters)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/render")
async def render_video(
    numero_regla: str = Form(...),
    guion: str = Form(...),
    subtitles_mode: str = Form("static"),
    audio_file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())

    audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = await audio_file.read()
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    audio_duration = get_audio_duration(audio_path)
    base_video = f"color=c=black:s=1080x1920:d={audio_duration}"

    font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")
    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail="No se encontró la fuente BebasNeue-Regular.ttf en la carpeta fonts"
        )

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion, words_per_chunk=3)
        drawtext_filters = build_drawtext_filters(chunks, audio_duration, numero_regla)
    else:
        title_text = f"REGLA INVISIBLE #{numero_regla}"
        title_text = title_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")
        body_text = guion.replace("\n", " ").replace("\r", " ").upper()
        body_text = body_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")

        drawtext_filters = ",".join([
            (
                f"drawtext="
                f"fontfile='{font_path}':"
                f"text='{title_text}':"
                f"fontsize=64:"
                f"fontcolor=white:"
                f"borderw=6:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=h*0.12"
            ),
            (
                f"drawtext="
                f"fontfile='{font_path}':"
                f"text='{body_text}':"
                f"fontsize=72:"
                f"fontcolor=white:"
                f"borderw=8:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=h*0.78"
            )
        ])

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        base_video,
        "-i",
        audio_path,
        "-vf",
        drawtext_filters,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-shortest",
        video_path,
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=500, detail="El video no se generó")

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "subtitles_mode_received": subtitles_mode
    }    
