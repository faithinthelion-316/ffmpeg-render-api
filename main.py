from pydantic import BaseModel

import os
import uuid
import shutil
import subprocess
import base64
import re

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = "/tmp/ffmpeg_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

MUSIC_FILE = "/app/music/backgroundRi.mp3"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

APP_FONTS_DIR = "/app/fonts"
APP_FONT_FILE = os.path.join(APP_FONTS_DIR, "BebasNeue-Regular.ttf")
RUNTIME_FONT_FILE = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

if os.path.exists(APP_FONT_FILE) and not os.path.exists(RUNTIME_FONT_FILE):
    shutil.copy(APP_FONT_FILE, RUNTIME_FONT_FILE)

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


def escape_ffmpeg_path(path: str) -> str:
    return (
        path.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def escape_drawtext_text(text: str) -> str:
    return (
        str(text)
        .replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace("%", r"\%")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("\n", r"\n")
    )


# 🔥 NUEVO: wrap inteligente para evitar cortes laterales
def wrap_text(text: str, max_line_chars: int = 14, max_lines: int = 3) -> str:
    words = str(text).split()
    if not words:
        return str(text)

    lines = []
    current = []

    for word in words:
        candidate = " ".join(current + [word]).strip()
        if len(candidate) <= max_line_chars or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    if len(lines) <= max_lines:
        return "\n".join(lines)

    compact = lines[:max_lines - 1]
    rest = " ".join(lines[max_lines - 1:])
    compact.append(rest)
    return "\n".join(compact)


def get_audio_duration(audio_path: str) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ], capture_output=True, text=True)

    try:
        return float(result.stdout.strip())
    except:
        return 8.0


def build_title_only_filter(numero_regla: str, hook: str) -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(status_code=500, detail="Fuente no encontrada")

    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)

    # 🔥 hook con wrap + uppercase
    hook_text = wrap_text(str(hook).upper(), max_line_chars=14, max_lines=3)
    safe_hook = escape_drawtext_text(hook_text)

    return ",".join([
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='REGLA INVISIBLE':"
            f"fontsize=56:"
            f"fontcolor=white:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.17"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='#{numero_regla}':"
            f"fontsize=56:"
            f"fontcolor=red:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.22"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='{safe_hook}':"
            f"fontsize=66:"
            f"fontcolor=red:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"line_spacing=12:"
            f"x=(w-text_w)/2:"
            f"y=h*0.44"
        )
    ])


class RenderRequest(BaseModel):
    numero_regla: str
    hook: str
    guion: str
    subtitles_mode: str = "dynamic"
    audio_base64: str
    normalized_alignment: dict


@app.post("/render")
async def render_video(data: RenderRequest):
    job_id = str(uuid.uuid4())

    audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = base64.b64decode(data.audio_base64)

    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    duration = get_audio_duration(audio_path)

    title_filter = build_title_only_filter(data.numero_regla, data.hook)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=720x1280:d={duration}",
        "-i", audio_path,
        "-vf", title_filter,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        video_path
    ]

    subprocess.run(ffmpeg_cmd)

    return {
        "video_url": f"/video/{job_id}.mp4"
    }
