import os
import uuid
import shutil
import subprocess
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = "/tmp/ffmpeg_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

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


def get_audio_duration(audio_path: str) -> float:
    probes = [
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "stream=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
    ]

    for cmd in probes:
        result = subprocess.run(cmd, capture_output=True, text=True)
        raw = (result.stdout or "").strip()
        if raw:
            for line in raw.splitlines():
                try:
                    value = float(line.strip())
                    if value > 0.2:
                        return value
                except Exception:
                    pass

    return 8.0


def build_title_only_filter(numero_regla: str) -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {RUNTIME_FONT_FILE}"
        )

    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)

    return ",".join([
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='REGLAS INVISIBLES':"
            f"fontsize=57:"
            f"fontcolor=white:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.10"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='#{numero_regla}':"
            f"fontsize=57:"
            f"fontcolor=0x8B0000:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.17"
        )
    ])

@app.get("/")
def health():
    return {
        "status": "running",
        "font_exists": os.path.exists(RUNTIME_FONT_FILE),
        "font_path": RUNTIME_FONT_FILE
    }


@app.post("/render")
async def render_video(
    numero_regla: str = Form(...),
    guion: str = Form(...),
    subtitles_mode: str = Form("dynamic"),
    audio_file: UploadFile = File(...)
):
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"La fuente no existe en runtime: {RUNTIME_FONT_FILE}"
        )

    job_id = str(uuid.uuid4())

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    normalized_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_normalized.mp3")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_file llegó vacío")

    with open(input_audio_path, "wb") as f:
        f.write(audio_bytes)

    normalize_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_audio_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        normalized_audio_path
    ]

    normalize_result = subprocess.run(normalize_cmd, capture_output=True, text=True)

    if normalize_result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error normalizando audio",
                "returncode": normalize_result.returncode,
                "stdout": normalize_result.stdout,
                "stderr": normalize_result.stderr,
            }
        )

    audio_duration = round(get_audio_duration(normalized_audio_path), 3)

    video_filter = build_title_only_filter(numero_regla)
    render_mode = "title_only"

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=720x1280:r=24:d={audio_duration}",
        "-i", normalized_audio_path,
        "-vf", video_filter,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        video_path
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error renderizando video",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "video_path": video_path,
                "font_exists": os.path.exists(RUNTIME_FONT_FILE),
                "font_path": RUNTIME_FONT_FILE,
                "audio_exists": os.path.exists(normalized_audio_path),
                "audio_path": normalized_audio_path,
                "filter_length": len(video_filter),
                "render_mode": render_mode,
            }
        )

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=500,
            detail={
                "message": "El video no se generó",
                "video_path": video_path,
                "audio_path": normalized_audio_path,
                "font_path": RUNTIME_FONT_FILE,
                "render_mode": render_mode,
            }
        )

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "video_url_full": f"https://ffmpeg-render-api-production-1143.up.railway.app/video/{job_id}.mp4",
        "audio_duration": audio_duration,
        "subtitles_mode_received": subtitles_mode,
        "render_mode": render_mode
    }


@app.post("/align")
async def align(
    id: str = Form(...),
    guion: str = Form(...),
    audio_file: UploadFile = File(...)
):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_bytes = await audio_file.read()
    tmp_file.write(audio_bytes)
    tmp_file.close()

    return {
        "status": "audio_received",
        "id": id,
        "guion_length": len(guion),
        "audio_file": tmp_file.name
    }
