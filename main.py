import os
import uuid
import subprocess
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


def escape_ffmpeg_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace("%", r"\%")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace(";", r"\;")
        .replace("\n", " ")
        .replace("\r", " ")
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
        raw = result.stdout.strip()
        if raw:
            for line in raw.splitlines():
                try:
                    value = float(line.strip())
                    if value > 0.5:
                        return value
                except Exception:
                    pass

    return 8.0


def build_drawtext_filters(chunks: List[str], audio_duration: float, numero_regla: str) -> str:
    font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail="No se encontró la fuente BebasNeue-Regular.ttf en fonts"
        )

    duration_per_chunk = audio_duration / max(len(chunks), 1)

    title_main = escape_ffmpeg_text("REGLAS INVISIBLES")
    title_num = escape_ffmpeg_text(f"#{numero_regla}")

    filters = [
        (
            f"drawtext="
            f"fontfile='{font_path}':"
            f"text='{title_main}':"
            f"fontsize=64:"
            f"fontcolor=white:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.09"
        ),
        (
            f"drawtext="
            f"fontfile='{font_path}':"
            f"text='{title_num}':"
            f"fontsize=58:"
            f"fontcolor=0x8B0000:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.15"
        )
    ]

    for i, chunk in enumerate(chunks):
        start = round(i * duration_per_chunk, 3)
        end = round(start + duration_per_chunk, 3)
        txt = escape_ffmpeg_text(chunk)

        filters.append(
            f"drawtext="
            f"fontfile='{font_path}':"
            f"text='{txt}':"
            f"fontsize=78:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"enable='between(t,{start},{end})'"
        )

    return ",".join(filters)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/render")
async def render_video(
    numero_regla: str = Form(...),
    guion: str = Form(...),
    subtitles_mode: str = Form("dynamic"),
    audio_file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())

    original_name = audio_file.filename or "audio.mp3"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in [".mp3", ".mpeg", ".wav", ".m4a", ".aac", ".ogg"]:
        ext = ".mp3"

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}{ext}")
    normalized_audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_file llegó vacío")

    with open(input_audio_path, "wb") as f:
        f.write(audio_bytes)

    normalize_cmd = [
        "ffmpeg",
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
        raise HTTPException(status_code=500, detail=normalize_result.stderr)

    audio_duration = round(get_audio_duration(normalized_audio_path), 3)

    font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")
    if not os.path.exists(font_path):
        raise HTTPException(
            status_code=500,
            detail="No se encontró la fuente BebasNeue-Regular.ttf en fonts"
        )

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion, words_per_chunk=4)
        drawtext_filters = build_drawtext_filters(chunks, audio_duration, numero_regla)
    else:
        title_main = escape_ffmpeg_text("REGLAS INVISIBLES")
        title_num = escape_ffmpeg_text(f"#{numero_regla}")
        body_text = escape_ffmpeg_text(guion.upper())

        drawtext_filters = ",".join([
            (
                f"drawtext="
                f"fontfile='{font_path}':"
                f"text='{title_main}':"
                f"fontsize=64:"
                f"fontcolor=white:"
                f"borderw=6:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=h*0.09"
            ),
            (
                f"drawtext="
                f"fontfile='{font_path}':"
                f"text='{title_num}':"
                f"fontsize=58:"
                f"fontcolor=0x8B0000:"
                f"borderw=6:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=h*0.15"
            ),
            (
                f"drawtext="
                f"fontfile='{font_path}':"
                f"text='{body_text}':"
                f"fontsize=78:"
                f"fontcolor=white:"
                f"borderw=8:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2"
            )
        ])

    ffmpeg_cmd = [
        "ffmpeg",
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

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=500, detail="El video no se generó")

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "subtitles_mode_received": subtitles_mode,
        "audio_duration": audio_duration,
        "audio_bytes_received": len(audio_bytes),
        "original_filename": original_name
    }
