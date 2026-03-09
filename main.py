import os
import uuid
import shutil
import subprocess
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = "/tmp/ffmpeg_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
TEXTS_DIR = os.path.join(BASE_DIR, "texts")
SUBS_DIR = os.path.join(BASE_DIR, "subs")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(TEXTS_DIR, exist_ok=True)
os.makedirs(SUBS_DIR, exist_ok=True)

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


def chunk_text(text: str, words_per_chunk: int = 3) -> List[str]:
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


def ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis == 100:
        secs += 1
        centis = 0
    if secs == 60:
        minutes += 1
        secs = 0
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass_text(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
        .replace("\r", "")
    )


def wrap_chunk_for_ass(chunk: str, max_words_per_line: int = 2) -> str:
    words = chunk.split()
    if len(words) <= max_words_per_line:
        return chunk

    lines = []
    for i in range(0, len(words), max_words_per_line):
        lines.append(" ".join(words[i:i + max_words_per_line]))
    return r"\N".join(lines)


def build_ass_subtitles(job_id: str, chunks: List[str], audio_duration: float) -> str:
    if not chunks:
        chunks = ["..."]

    ass_path = os.path.join(SUBS_DIR, f"{job_id}.ass")
    duration_per_chunk = audio_duration / len(chunks)

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral, Bebas Neue, 40,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,0,5,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]

    for i, chunk in enumerate(chunks):
        start = round(i * duration_per_chunk, 2)
        end = round((i + 1) * duration_per_chunk, 2)

        if i == len(chunks) - 1:
            end = audio_duration

        visible_text = wrap_chunk_for_ass(chunk, max_words_per_line=2)
        visible_text = escape_ass_text(visible_text)

        line = (
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Viral,,0,0,0,,"
            f"{{\\an5\\fad(30,30)}}{visible_text}\n"
        )
        lines.append(line)

    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return ass_path


def build_static_drawtext_filter(guion: str, numero_regla: str, job_id: str) -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {RUNTIME_FONT_FILE}"
        )

    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)

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
            f"fontsize=52:"
            f"fontcolor=white:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.08"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(title_num_file)}':"
            f"fontsize=46:"
            f"fontcolor=0x8B0000:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.14"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"textfile='{escape_ffmpeg_path(body_file)}':"
            f"fontsize=54:"
            f"fontcolor=white:"
            f"borderw=5:"
            f"bordercolor=black:"
            f"line_spacing=12:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2"
        )
    ])


def build_dynamic_filter(numero_regla: str, ass_path: str) -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {RUNTIME_FONT_FILE}"
        )

    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)
    safe_ass_path = escape_ffmpeg_path(ass_path)
    safe_fonts_dir = escape_ffmpeg_path(FONTS_DIR)

    title_main = "REGLAS INVISIBLES"
    title_num = f"#{numero_regla}"

    return ",".join([
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='{title_main}':"
            f"fontsize=52:"
            f"fontcolor=white:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.08"
        ),
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='{title_num}':"
            f"fontsize=46:"
            f"fontcolor=0x8B0000:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.14"
        ),
        (
            f"subtitles='{safe_ass_path}':"
            f"fontsdir='{safe_fonts_dir}'"
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

    if subtitles_mode == "dynamic":
        chunks = chunk_text(guion, words_per_chunk=3)
        ass_path = build_ass_subtitles(job_id, chunks, audio_duration)
        video_filter = build_dynamic_filter(numero_regla, ass_path)
        render_mode = "dynamic_ass"
    else:
        video_filter = build_static_drawtext_filter(guion, numero_regla, job_id)
        ass_path = None
        render_mode = "static_safe"

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
                "ass_exists": os.path.exists(ass_path) if ass_path else False,
                "ass_path": ass_path,
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
                "ass_path": ass_path,
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
