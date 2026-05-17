from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

import os
import uuid
import shutil
import subprocess
import base64
import re
import unicodedata


app = FastAPI()

BASE_DIR = "/tmp/reglas_invisibles_render"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

FPS = 24
OUTPUT_WIDTH = 720
OUTPUT_HEIGHT = 1280

RI_RED_HEX = "0xFF1E1E"
RI_WHITE_HEX = "0xFFFFFF"
RI_BLACK_HEX = "black"

# ASS colors use BGR format.
ASS_WHITE = r"\c&HFFFFFF&"
ASS_RED = r"\c&H1E1EFF&"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

APP_FONTS_DIR = "/app/fonts"

APP_FONT_CANDIDATES = [
    os.path.join(APP_FONTS_DIR, "BebasNeue-Regular.ttf"),
    os.path.join(APP_FONTS_DIR, "BebasNeue.ttf"),
    os.path.join(APP_FONTS_DIR, "ArchivoBlack-Regular.ttf"),
    os.path.join(APP_FONTS_DIR, "ArchivoBlack.ttf"),
    os.path.join(APP_FONTS_DIR, "SpaceGrotesk.ttf"),
]

RUNTIME_FONT_FILE = os.path.join(FONTS_DIR, "BebasNeue-Regular.ttf")

if not os.path.exists(RUNTIME_FONT_FILE):
    for candidate in APP_FONT_CANDIDATES:
        if os.path.exists(candidate):
            shutil.copy(candidate, RUNTIME_FONT_FILE)
            break

app.mount("/video", StaticFiles(directory=VIDEO_DIR), name="video")


class RenderRequest(BaseModel):
    numero_regla: str = ""
    guion: str
    audio_base64: str
    normalized_alignment: dict
    subtitles_mode: str = "dynamic"


def escape_ffmpeg_path(path: str) -> str:
    return (
        path.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def escape_drawtext_value(value: str) -> str:
    if not value:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("'", "’")
        .replace("%", "\\%")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("=", "\\=")
        .replace(";", "\\;")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def seconds_to_ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def escape_ass_text(text: str) -> str:
    return (
        str(text)
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def normalize_token(value: str) -> str:
    text = str(value or "").upper()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[^A-ZÑ0-9]+", "", text)
    return text


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    raw = (result.stdout or "").strip()

    try:
        value = float(raw)
        if value > 0:
            return value
    except Exception:
        pass

    return 30.0


def speed_up_alignment(alignment: dict, speed: float) -> dict:
    return {
        "characters": alignment.get("characters", []),
        "character_start_times_seconds": [
            float(x) / speed for x in alignment.get("character_start_times_seconds", [])
        ],
        "character_end_times_seconds": [
            float(x) / speed for x in alignment.get("character_end_times_seconds", [])
        ],
    }


def build_words_from_alignment(alignment: dict) -> list:
    characters = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    if not characters or not starts or not ends:
        return []

    words = []
    current_chars = []
    current_start = None
    current_end = None

    for ch, st, en in zip(characters, starts, ends):
        try:
            st = float(st)
            en = float(en)
        except Exception:
            continue

        if str(ch).isspace():
            if current_chars:
                word = "".join(current_chars).strip()
                if word:
                    words.append({
                        "word": word,
                        "start": float(current_start),
                        "end": float(current_end),
                    })
                current_chars = []
                current_start = None
                current_end = None
            continue

        if current_start is None:
            current_start = st

        current_chars.append(str(ch))
        current_end = en

    if current_chars:
        word = "".join(current_chars).strip()
        if word:
            words.append({
                "word": word,
                "start": float(current_start),
                "end": float(current_end),
            })

    return words


def group_words_into_cues(words: list, max_words: int = 5, max_chars: int = 30) -> list:
    cues = []
    bucket = []

    def flush_bucket():
        nonlocal bucket
        if not bucket:
            return

        raw_text = " ".join(str(item["word"]) for item in bucket).strip()
        if raw_text:
            start_value = float(bucket[0]["start"])
            end_value = float(bucket[-1]["end"])

            cues.append({
                "text": raw_text.upper(),
                "start": start_value,
                "end": end_value,
                "words": [
                    {
                        "word": str(item["word"]).upper(),
                        "start": float(item["start"]),
                        "end": float(item["end"]),
                    }
                    for item in bucket
                ],
            })

        bucket = []

    for item in words:
        candidate_words = bucket + [item]
        candidate_text = " ".join(str(x["word"]) for x in candidate_words)

        punctuation_break = bool(re.search(r"[.!?,;:]$", str(item["word"])))
        too_many_words = len(candidate_words) > max_words
        too_many_chars = len(candidate_text) > max_chars

        if bucket and (too_many_words or too_many_chars):
            flush_bucket()

        bucket.append(item)

        if punctuation_break:
            flush_bucket()

    flush_bucket()

    for cue in cues:
        cue["start"] = float(cue["start"])
        cue["end"] = float(cue["end"])

        if cue["end"] - cue["start"] < 0.35:
            cue["end"] = cue["start"] + 0.35

    return cues


def split_word_items_two_lines(word_items: list, max_line_chars: int = 16) -> list:
    if not word_items:
        return []

    words = [str(item["word"]) for item in word_items]

    if len(words) <= 1:
        return [word_items]

    best_split_index = None
    best_score = None

    for i in range(1, len(words)):
        line1 = " ".join(words[:i])
        line2 = " ".join(words[i:])

        if len(line1) > max_line_chars or len(line2) > max_line_chars:
            continue

        score = abs(len(line1) - len(line2))
        if best_score is None or score < best_score:
            best_score = score
            best_split_index = i

    if best_split_index is None:
        midpoint = max(1, len(words) // 2)
        return [word_items[:midpoint], word_items[midpoint:]]

    return [word_items[:best_split_index], word_items[best_split_index:]]


def build_line_groups(word_items: list, max_line_chars: int = 15) -> list:
    split_lines = split_word_items_two_lines(word_items, max_line_chars=max_line_chars)
    groups = []
    flat_index = 0

    for line_items in split_lines:
        group = []
        for item in line_items:
            group.append({
                "index": flat_index,
                "word": str(item["word"]).upper(),
                "start": float(item["start"]),
                "end": float(item["end"]),
            })
            flat_index += 1
        groups.append(group)

    return groups


def build_ass_dialogue_text(groups: list, active_index: int | None = None) -> str:
    line_texts = []

    for line in groups:
        parts = []

        for item in line:
            word_text = escape_ass_text(item["word"])
            is_active = active_index is not None and item["index"] == active_index

            if is_active:
                parts.append(r"{" + ASS_RED + r"}" + word_text + r"{" + ASS_WHITE + r"}")
            else:
                parts.append(word_text)

        line_texts.append(" ".join(parts))

    prefix = r"{\an2\fs68\bord3\shad0\fscx100\fscy100\fsp0" + ASS_WHITE + r"}"
    return prefix + r"\N".join(line_texts)


def write_ass_subtitles(subtitles_path: str, cues: list):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Bebas Neue,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,0,2,82,82,390,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(subtitles_path, "w", encoding="utf-8") as f:
        f.write(header)

        for cue in cues:
            cue_start = float(cue["start"])
            cue_end = float(cue["end"])

            groups = build_line_groups(
                cue.get("words", []),
                max_line_chars=15,
            )

            if not groups:
                continue

            flat_words = [item for line in groups for item in line]
            if not flat_words:
                continue

            segments = []
            cursor = cue_start
            eps = 0.01

            for item in flat_words:
                word_start = max(cue_start, float(item["start"]))
                word_end = min(cue_end, float(item["end"]))

                if word_start > cursor + eps:
                    segments.append({
                        "start": cursor,
                        "end": word_start,
                        "active_index": None,
                    })

                if word_end > word_start + eps:
                    segments.append({
                        "start": word_start,
                        "end": word_end,
                        "active_index": item["index"],
                    })

                cursor = max(cursor, word_end)

            if cue_end > cursor + eps:
                segments.append({
                    "start": cursor,
                    "end": cue_end,
                    "active_index": None,
                })

            for seg in segments:
                if seg["end"] <= seg["start"] + eps:
                    continue

                start = seconds_to_ass_time(seg["start"])
                end = seconds_to_ass_time(seg["end"])
                text = build_ass_dialogue_text(groups, active_index=seg["active_index"])

                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")


def build_title_filter(numero_regla: str) -> str:
    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)

    numero = str(numero_regla or "").strip()
    numero = re.sub(r"[^0-9A-Za-zÁÉÍÓÚáéíóúÑñ#\- ]+", "", numero).strip()

    if not numero:
        numero = "000"

    if not numero.startswith("#"):
        numero = f"#{numero}"

    safe_title = escape_drawtext_value("REGLA INVISIBLE")
    safe_number = escape_drawtext_value(numero)

    title_filter = (
        f"drawtext="
        f"fontfile={safe_font_path}:"
        f"text={safe_title}:"
        f"fontsize=58:"
        f"fontcolor={RI_WHITE_HEX}:"
        f"borderw=2:"
        f"bordercolor=black:"
        f"shadowx=0:"
        f"shadowy=0:"
        f"x=(w-text_w)/2:"
        f"y=245"
    )

    number_filter = (
        f"drawtext="
        f"fontfile={safe_font_path}:"
        f"text={safe_number}:"
        f"fontsize=58:"
        f"fontcolor={RI_RED_HEX}:"
        f"borderw=2:"
        f"bordercolor=black:"
        f"shadowx=0:"
        f"shadowy=0:"
        f"x=(w-text_w)/2:"
        f"y=315"
    )

    return f"{title_filter},{number_filter}"


@app.get("/")
def health():
    return {
        "status": "running",
        "project": "Reglas Invisibles",
        "render_style": "minimal_black_background",
        "font_exists": os.path.exists(RUNTIME_FONT_FILE),
        "font_path": RUNTIME_FONT_FILE,
        "video_output": "720x1280",
        "features": [
            "black_background",
            "top_title_regla_invisible",
            "red_rule_number",
            "dynamic_subtitles",
            "active_word_red",
            "safe_margins",
            "no_hook_card",
            "no_truth_punch",
            "no_cta_card",
            "no_music",
            "no_images",
            "no_external_video",
        ],
    }


@app.post("/render")
async def render_video(data: RenderRequest):
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No existe fuente en runtime: {RUNTIME_FONT_FILE}. Sube BebasNeue-Regular.ttf, ArchivoBlack-Regular.ttf o SpaceGrotesk.ttf a /app/fonts."
        )

    job_id = str(uuid.uuid4())

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_input.mp3")
    voice_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_voice.mp3")
    subtitles_path = os.path.join(BASE_DIR, f"{job_id}.ass")
    video_path = os.path.join(VIDEO_DIR, f"{job_id}.mp4")

    try:
        audio_bytes = base64.b64decode(data.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="audio_base64 inválido")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_base64 llegó vacío")

    with open(input_audio_path, "wb") as f:
        f.write(audio_bytes)

    # Mantiene ritmo más rápido para Shorts/Reels.
    speed_factor = 1.18

    normalize_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_audio_path,
        "-vn",
        "-filter:a", f"atempo={speed_factor}",
        "-acodec", "libmp3lame",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        voice_audio_path,
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
            },
        )

    voice_duration = round(get_audio_duration(voice_audio_path), 3)
    final_duration = voice_duration

    adjusted_alignment = speed_up_alignment(data.normalized_alignment, speed_factor)
    words = build_words_from_alignment(adjusted_alignment)
    cues = group_words_into_cues(words, max_words=5, max_chars=30)

    write_ass_subtitles(subtitles_path, cues)

    safe_subtitles_path = escape_ffmpeg_path(subtitles_path)
    safe_fonts_dir = escape_ffmpeg_path(FONTS_DIR)

    title_filter = build_title_filter(data.numero_regla)

    video_filter = (
        f"{title_filter},"
        f"subtitles={safe_subtitles_path}:fontsdir={safe_fonts_dir}"
    )

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s={OUTPUT_WIDTH}x{OUTPUT_HEIGHT}:r={FPS}:d={final_duration:.2f}",
        "-i", voice_audio_path,
        "-vf", video_filter,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", f"{final_duration:.2f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        video_path,
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
                "video_filter_excerpt": video_filter[:2500],
            },
        )

    if not os.path.exists(video_path):
        raise HTTPException(status_code=500, detail="El video no se generó")

    base_url = os.environ.get(
        "BASE_URL",
        "https://ffmpeg-render-api-production-1143.up.railway.app",
    ).rstrip("/")

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "video_url_full": f"{base_url}/video/{job_id}.mp4",
        "voice_duration": voice_duration,
        "final_duration": final_duration,
        "render_mode": "reglas_invisibles_minimal_black_background",
        "numero_regla": data.numero_regla,
        "cues_count": len(cues),
        "speed_factor": speed_factor,
        "subtitles_mode_received": data.subtitles_mode,
    }
