```python
import os
import re
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
def log_block(title: str, content: str) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    print(content)
    print(f"{'=' * 20} END {title} {'=' * 20}\n")


def ensure_font_available() -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en runtime: {RUNTIME_FONT_FILE}"
        )
    return RUNTIME_FONT_FILE


def sanitize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def to_upper_clean(text: str) -> str:
    return sanitize_text(text).upper()


def chunk_text(text: str, words_per_chunk: int = 4) -> List[str]:
    words = sanitize_text(text).split()
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
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        raw = result.stdout.strip()
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


def escape_filter_path(path: str) -> str:
    return path.replace("\\", "\\\\").replace(":", "\\:")


def build_drawtext_filters_dynamic(
    job_id: str,
    chunks: List[str],
    audio_duration: float,
    numero_regla: str
) -> str:
    font_path = ensure_font_available()
    escaped_font_path = escape_filter_path(font_path)

    duration_per_chunk = audio_duration / max(len(chunks), 1)

    title_main_path = write_text_file(job_id, "title_main", "REGLAS INVISIBLES")
    title_num_path = write_text_file(job_id, "title_num", f"#{sanitize_text(numero_regla)}")

    filters = [
        (
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(title_main_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=64:"
            "fontcolor=white:"
            "borderw=6:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h*0.08"
        ),
        (
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(title_num_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=58:"
            "fontcolor=0x8B0000:"
            "borderw=6:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h*0.13"
        ),
    ]

    for i, chunk in enumerate(chunks):
        start = round(i * duration_per_chunk, 3)
        end = round((i + 1) * duration_per_chunk, 3)

        chunk_path = write_text_file(job_id, f"chunk_{i}", chunk)

        filters.append(
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(chunk_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=78:"
            "fontcolor=white:"
            "borderw=8:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2:"
            f"enable='between(t,{start},{end})'"
        )

    return ",".join(filters)


def build_drawtext_filters_static(
    job_id: str,
    body_text: str,
    numero_regla: str
) -> str:
    font_path = ensure_font_available()
    escaped_font_path = escape_filter_path(font_path)

    title_main_path = write_text_file(job_id, "title_main", "REGLAS INVISIBLES")
    title_num_path = write_text_file(job_id, "title_num", f"#{sanitize_text(numero_regla)}")
    body_text_path = write_text_file(job_id, "body_text", to_upper_clean(body_text))

    return ",".join([
        (
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(title_main_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=64:"
            "fontcolor=white:"
            "borderw=6:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h*0.08"
        ),
        (
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(title_num_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=58:"
            "fontcolor=0x8B0000:"
            "borderw=6:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h*0.13"
        ),
        (
            "drawtext="
            f"fontfile='{escaped_font_path}':"
            f"textfile='{escape_filter_path(body_text_path)}':"
            "reload=0:"
            "expansion=none:"
            "fontsize=78:"
            "fontcolor=white:"
            "borderw=8:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2"
        )
    ])


def run_subprocess(cmd: List[str], error_prefix: str, timeout_seconds: int = 180) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail=f"{error_prefix}\nTimeout al ejecutar subprocess tras {timeout_seconds} segundos."
        )

    log_block("COMMAND", " ".join(cmd))
    log_block("STDOUT", result.stdout or "(vacío)")
    log_block("STDERR", result.stderr or "(vacío)")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"{error_prefix}\n{result.stderr}"
        )

    return result


def check_ffmpeg_drawtext_available() -> None:
    cmd = ["ffmpeg", "-hide_banner", "-filters"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    if "drawtext" not in output:
        raise HTTPException(
            status_code=500,
            detail="La build de FFmpeg no incluye el filtro drawtext."
        )


# =========================
# ENDPOINTS
# =========================
@app.get("/")
def health():
    print("HEALTHCHECK OK")
    return {
        "status": "running",
        "font_exists": os.path.exists(RUNTIME_FONT_FILE),
        "font_path": RUNTIME_FONT_FILE
    }


@app.get("/ping")
def ping():
    print("PING OK")
    return {"ok": True, "message": "pong"}


@app.post("/render")
async def render_video(
    numero_regla: str = Form(...),
    guion: str = Form(...),
    subtitles_mode: str = Form("dynamic"),
    audio_file: UploadFile = File(...)
):
    print("===== REQUEST /render RECIBIDA =====")
    print(f"numero_regla={numero_regla}")
    print(f"subtitles_mode={subtitles_mode}")
    print(f"audio_file.filename={audio_file.filename}")
    print(f"audio_file.content_type={audio_file.content_type}")

    check_ffmpeg_drawtext_available()
    ensure_font_available()

    job_id = str(uuid.uuid4())

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    normalized_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_normalized.mp3")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = await audio_file.read()
    print(f"audio_bytes_length={len(audio_bytes) if audio_bytes else 0}")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_file llegó vacío")

    with open(input_audio_path, "wb") as f:
        f.write(audio_bytes)

    print(f"input_audio_path={input_audio_path}")
    print(f"normalized_audio_path={normalized_audio_path}")
    print(f"video_path={video_path}")

    normalize_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i", input_audio_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        normalized_audio_path
    ]
    run_subprocess(normalize_cmd, "Error normalizando audio:", timeout_seconds=120)

    audio_duration = round(get_audio_duration(normalized_audio_path), 3)
    print(f"audio_duration={audio_duration}")

    if audio_duration <= 0:
        raise HTTPException(status_code=500, detail="No se pudo obtener la duración del audio")

    guion_limpio = sanitize_text(guion)
    print(f"guion_original_len={len(guion) if guion else 0}")
    print(f"guion_limpio_len={len(guion_limpio)}")

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion_limpio, words_per_chunk=4)
        print(f"chunks_count={len(chunks)}")
        print(f"chunks_preview={chunks[:5]}")

        if not chunks:
            raise HTTPException(status_code=400, detail="El guion quedó vacío tras sanitización")

        drawtext_filters = build_drawtext_filters_dynamic(
            job_id=job_id,
            chunks=chunks,
            audio_duration=audio_duration,
            numero_regla=numero_regla
        )
    else:
        drawtext_filters = build_drawtext_filters_static(
            job_id=job_id,
            body_text=guion_limpio,
            numero_regla=numero_regla
        )

    log_block("DRAWTEXT FILTERS", drawtext_filters)

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1080x1920:r=30:d={audio_duration}",
        "-i", normalized_audio_path,
        "-vf", drawtext_filters,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-threads", "1",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        video_path
    ]

    run_subprocess(ffmpeg_cmd, "Error renderizando video:", timeout_seconds=180)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=500, detail="El video no se generó")

    print(f"VIDEO GENERADO OK: {video_path}")

    chunks_count = len(chunk_text(guion_limpio, words_per_chunk=4)) if subtitles_mode == "dynamic" else None

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "video_url_full": f"https://ffmpeg-render-api-production-1143.up.railway.app/video/{job_id}.mp4",
        "audio_duration": audio_duration,
        "subtitles_mode_received": subtitles_mode,
        "chunks_count": chunks_count
    }
```
