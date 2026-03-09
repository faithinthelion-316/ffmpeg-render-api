import os
import uuid
import shutil
import subprocess
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# =========================
# RUTAS
# =========================
BASE_DIR = "/tmp/ffmpeg_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
TEXTS_DIR = os.path.join(BASE_DIR, "texts")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(TEXTS_DIR, exist_ok=True)

APP_FONTS_DIR = "/app/fonts"
APP_FONT_FILE = os.path.join(APP_FONTS_DIR, "BebasNeue-Regular.ttf")
RUNTIME_FONT_FILE = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

if os.path.exists(APP_FONT_FILE) and not os.path.exists(RUNTIME_FONT_FILE):
    shutil.copy(APP_FONT_FILE, RUNTIME_FONT_FILE)

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


# =========================
# HELPERS
# =========================
def escape_ffmpeg_path(path: str) -> str:
    return (
        path.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
    )


def chunk_text(text: str, words_per_chunk: int = 4) -> List[str]:
    words = text.replace("\n", " ").replace("\r", " ").split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk]).strip()
        if chunk:
            chunks.append(chunk.upper())
    return chunks


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


def write_text_file(job_id: str, name: str, content: str) -> str:
    job_text_dir = os.path.join(TEXTS_DIR, job_id)
    os.makedirs(job_text_dir, exist_ok=True)

    file_path = os.path.join(job_text_dir, f"{name}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def build_drawtext_filters(chunks: List[str], audio_duration: float, numero_regla: str, job_id: str) -> str:
    font_path = RUNTIME_FONT_FILE

    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {font_path}"
        )

    safe_font_path = escape_ffmpeg_path(font_path)

    title_main_file = write_text_file(job_id, "title_main", "REGLAS INVISIBLES")
    title_num_file = write_text_file(job_id, "title_num", f"#{numero_regla}")

    filters = [
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(title_main_file)}':"
            f"fontsize=64:"
            f"fontcolor=white:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.08"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(title_num_file)}':"
            f"fontsize=58:"
            f"fontcolor=0x8B0000:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.13"
        )
    ]

    if not chunks:
        chunks = ["..."]

    duration_per_chunk = audio_duration / len(chunks)

    for i, chunk in enumerate(chunks):
        start = round(i * duration_per_chunk, 3)
        end = round((i + 1) * duration_per_chunk, 3)

        chunk_file = write_text_file(job_id, f"chunk_{i}", chunk)

        filters.append(
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(chunk_file)}':"
            f"fontsize=78:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"enable='between(t,{start},{end})'"
        )

    return ",".join(filters)


def build_static_drawtext_filter(guion: str, numero_regla: str, job_id: str) -> str:
    font_path = RUNTIME_FONT_FILE

    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {font_path}"
        )

    safe_font_path = escape_ffmpeg_path(font_path)

    title_main_file = write_text_file(job_id, "title_main", "REGLAS INVISIBLES")
    title_num_file = write_text_file(job_id, "title_num", f"#{numero_regla}")
    body_file = write_text_file(
        job_id,
        "body_text",
        guion.replace("\n", " ").replace("\r", " ").upper()
    )

    return ",".join([
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(title_main_file)}':"
            f"fontsize=64:"
            f"fontcolor=white:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.08"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(title_num_file)}':"
            f"fontsize=58:"
            f"fontcolor=0x8B0000:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.13"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(body_file)}':"
            f"fontsize=78:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2"
        )
    ])


# =========================
# ENDPOINTS
# =========================
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

    print("NORMALIZE CMD:", " ".join(normalize_cmd))
    normalize_result = subprocess.run(normalize_cmd, capture_output=True, text=True)

    if normalize_result.returncode != 0:
        print("NORMALIZE STDERR:\n", normalize_result.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Error normalizando audio:\n{normalize_result.stderr}"
        )

    audio_duration = round(get_audio_duration(normalized_audio_path), 3)

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion, words_per_chunk=4)
        drawtext_filters = build_drawtext_filters(chunks, audio_duration, numero_regla, job_id)
    else:
        drawtext_filters = build_static_drawtext_filter(guion, numero_regla, job_id)

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1080x1920:r=30:d={audio_duration}",
        "-i", normalized_audio_path,
        "-vf", drawtext_filters,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        video_path
    ]

        print("FFMPEG CMD:", " ".join(ffmpeg_cmd))
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    print("FFMPEG RETURN CODE:", result.returncode)
    print("FFMPEG STDOUT:\n", result.stdout)
    print("FFMPEG STDERR:\n", result.stderr)
    print("VIDEO PATH:", video_path)
    print("FONT EXISTS:", os.path.exists(RUNTIME_FONT_FILE), RUNTIME_FONT_FILE)
    print("NORMALIZED AUDIO EXISTS:", os.path.exists(normalized_audio_path), normalized_audio_path)
    print("DRAWTEXT LENGTH:", len(drawtext_filters))

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
                "drawtext_length": len(drawtext_filters),
            }
    )
