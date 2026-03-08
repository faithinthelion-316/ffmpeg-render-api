import os
import uuid
import subprocess
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Carpetas
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Servir los videos
app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


def chunk_text(text: str, words_per_chunk: int = 5) -> List[str]:
    """
    Divide el texto en frases cortas de N palabras
    para subtítulos dinámicos.
    """
    words = text.replace("\n", " ").split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk.upper())
    return chunks


def build_drawtext_filters(chunks: List[str], audio_duration: float) -> str:
    """
    Genera los filtros drawtext con timing.
    """
    font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

    duration_per_chunk = audio_duration / max(len(chunks), 1)

    filters = []
    for i, chunk in enumerate(chunks):
        start = i * duration_per_chunk
        end = start + duration_per_chunk

        txt = chunk.replace(":", "\\:").replace("'", "\\'")

        draw = (
            f"drawtext=fontfile={font_path}:"
            f"text='{txt}':"
            f"fontsize=90:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.75:"
            f"enable='between(t,{start},{end})'"
        )

        filters.append(draw)

    return ",".join(filters)


def get_audio_duration(audio_path: str) -> float:
    """
    Obtiene duración del audio usando ffprobe.
    """
    cmd = [
        "ffprobe",
        "-i",
        audio_path,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "csv=p=0"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 5.0


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

    # guardar audio
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    audio_duration = get_audio_duration(audio_path)

    # fondo negro vertical
    base_video = f"color=c=black:s=1080x1920:d={audio_duration}"

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion)
        drawtext_filters = build_drawtext_filters(chunks, audio_duration)
    else:
        font_path = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")
        txt = guion.replace(":", "\\:").replace("'", "\\'")
        drawtext_filters = (
            f"drawtext=fontfile={font_path}:"
            f"text='{txt}':"
            f"fontsize=90:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.75"
        )

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
        "-shortest",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        video_path
    ]

    subprocess.run(ffmpeg_cmd)

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "subtitles_mode_received": subtitles_mode
    }


@app.get("/")
def health():
    return {"status": "running"}
