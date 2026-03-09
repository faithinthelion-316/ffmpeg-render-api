import os
import uuid
import shutil
import subprocess
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel

app = FastAPI()

BASE_DIR = "/tmp/ffmpeg_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
SUBS_DIR = os.path.join(BASE_DIR, "subs")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(SUBS_DIR, exist_ok=True)

APP_FONTS_DIR = "/app/fonts"
APP_FONT_FILE = os.path.join(APP_FONTS_DIR, "BebasNeue-Regular.ttf")
RUNTIME_FONT_FILE = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

if os.path.exists(APP_FONT_FILE) and not os.path.exists(RUNTIME_FONT_FILE):
    shutil.copy(APP_FONT_FILE, RUNTIME_FONT_FILE)

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")

WHISPER_MODEL: Optional[WhisperModel] = None


def get_whisper_model() -> WhisperModel:
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        WHISPER_MODEL = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )
    return WHISPER_MODEL


def escape_ffmpeg_path(path: str) -> str:
    return (
        path.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0

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
        .replace("\r", "")
        .replace("\n", r"\N")
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


def transcribe_words(audio_path: str) -> List[Dict[str, Any]]:
    model = get_whisper_model()

    segments, _ = model.transcribe(
        audio_path,
        language="es",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=350),
        beam_size=1
    )

    words: List[Dict[str, Any]] = []

    for segment in segments:
        segment_words = getattr(segment, "words", None) or []
        for word in segment_words:
            start = getattr(word, "start", None)
            end = getattr(word, "end", None)
            token = (getattr(word, "word", "") or "").strip()

            if start is None or end is None or not token:
                continue

            words.append({
                "start": float(start),
                "end": float(end),
                "word": token
            })

    return words


def group_words(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not words:
        return []

    groups: List[Dict[str, Any]] = []
    current_words: List[str] = []
    current_start: Optional[float] = None
    current_end: Optional[float] = None

    max_words = 3
    max_duration = 1.6

    for item in words:
        token = item["word"]
        start = item["start"]
        end = item["end"]

        clean_token = token.strip()
        if not clean_token:
            continue

        if current_start is None:
            current_start = start

        current_words.append(clean_token)
        current_end = end

        group_duration = (current_end - current_start) if current_end is not None else 0.0
        ends_sentence = clean_token.endswith((".", ",", ";", ":", "?", "!", "…"))

        should_close = (
            len(current_words) >= max_words
            or group_duration >= max_duration
            or ends_sentence
        )

        if should_close:
            groups.append({
                "start": current_start,
                "end": current_end,
                "text": " ".join(current_words).upper()
            })
            current_words = []
            current_start = None
            current_end = None

    if current_words and current_start is not None and current_end is not None:
        groups.append({
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_words).upper()
        })

    return groups


def wrap_group_text(text: str, max_words_per_line: int = 2) -> str:
    words = text.split()
    if len(words) <= max_words_per_line:
        return text

    lines = []
    for i in range(0, len(words), max_words_per_line):
        lines.append(" ".join(words[i:i + max_words_per_line]))
    return r"\N".join(lines)


def build_ass_from_words(job_id: str, words: List[Dict[str, Any]], audio_duration: float) -> str:
    ass_path = os.path.join(SUBS_DIR, f"{job_id}.ass")
    groups = group_words(words)

    if not groups:
        groups = [{
            "start": 0.0,
            "end": audio_duration,
            "text": "..."
        }]

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral, Bebas Neue, 42,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,0,5,36,36,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]

    for group in groups:
        text = wrap_group_text(group["text"], max_words_per_line=2)
        text = escape_ass_text(text)

        start = max(0.0, float(group["start"]))
        end = max(start + 0.08, float(group["end"]))

        line = (
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Viral,,0,0,0,,"
            f"{{\\an5\\fad(20,20)}}{text}\n"
        )
        lines.append(line)

    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return ass_path


def build_static_filter(numero_regla: str) -> str:
    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)
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
        )
    ])


def build_dynamic_filter(numero_regla: str, ass_path: str) -> str:
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

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_input.mp3")
    transcribe_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_stt.wav")
    render_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_render.wav")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_file llegó vacío")

    with open(input_audio_path, "wb") as f:
        f.write(audio_bytes)

    normalize_render_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_audio_path,
        "-ac", "2",
        "-ar", "44100",
        render_audio_path
    ]

    render_audio_result = subprocess.run(normalize_render_cmd, capture_output=True, text=True)
    if render_audio_result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error preparando audio para render",
                "returncode": render_audio_result.returncode,
                "stdout": render_audio_result.stdout,
                "stderr": render_audio_result.stderr,
            }
        )

    normalize_stt_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_audio_path,
        "-ac", "1",
        "-ar", "16000",
        transcribe_audio_path
    ]

    stt_audio_result = subprocess.run(normalize_stt_cmd, capture_output=True, text=True)
    if stt_audio_result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error preparando audio para transcripción",
                "returncode": stt_audio_result.returncode,
                "stdout": stt_audio_result.stdout,
                "stderr": stt_audio_result.stderr,
            }
        )

    audio_duration = round(get_audio_duration(render_audio_path), 3)

    ass_path = None
    detected_words = []

    if subtitles_mode == "dynamic":
        detected_words = transcribe_words(transcribe_audio_path)
        ass_path = build_ass_from_words(job_id, detected_words, audio_duration)
        video_filter = build_dynamic_filter(numero_regla, ass_path)
        render_mode = "dynamic_whisper_word_timestamps"
    else:
        video_filter = build_static_filter(numero_regla)
        render_mode = "static_safe"

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=720x1280:r=24:d={audio_duration}",
        "-i", render_audio_path,
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
                "audio_exists": os.path.exists(render_audio_path),
                "audio_path": render_audio_path,
                "stt_audio_exists": os.path.exists(transcribe_audio_path),
                "stt_audio_path": transcribe_audio_path,
                "font_exists": os.path.exists(RUNTIME_FONT_FILE),
                "font_path": RUNTIME_FONT_FILE,
                "ass_exists": os.path.exists(ass_path) if ass_path else False,
                "ass_path": ass_path,
                "filter_length": len(video_filter),
                "detected_words": len(detected_words),
                "render_mode": render_mode,
            }
        )

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=500,
            detail={
                "message": "El video no se generó",
                "video_path": video_path,
                "audio_path": render_audio_path,
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
        "render_mode": render_mode,
        "detected_words": len(detected_words),
    }
