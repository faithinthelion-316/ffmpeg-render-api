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
    )


def estimate_text_width(text: str, fontsize: int = 70) -> float:
    total = 0.0
    for ch in str(text):
        if ch == " ":
            total += 0.34
        elif ch in "IÍÌÏ1!¡|":
            total += 0.32
        elif ch in "MWÑQÓÒÖÚÙÜO0GDCÁÀÄ":
            total += 0.78
        elif ch in ".,;:¿?":
            total += 0.28
        else:
            total += 0.58
    return total * fontsize


def wrap_text_by_width(text: str, fontsize: int = 70, max_width_px: int = 560) -> list:
    words = str(text).split()
    if not words:
        return [str(text)]

    lines = []
    current = []

    for word in words:
        candidate = " ".join(current + [word]).strip()
        if not current or estimate_text_width(candidate, fontsize) <= max_width_px:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


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


def build_title_only_filter(numero_regla: str, hook: str) -> str:
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la fuente en {RUNTIME_FONT_FILE}"
        )

    safe_font_path = escape_ffmpeg_path(RUNTIME_FONT_FILE)

    hook_lines = wrap_text_by_width(str(hook).upper(), fontsize=70, max_width_px=560)
    if not hook_lines:
        hook_lines = [str(hook).upper()]

    filters = [
        (
            f"drawtext="
            f"fontfile='{safe_font_path}':"
            f"text='REGLA INVISIBLE':"
            f"fontsize=57:"
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
            f"fontsize=57:"
            f"fontcolor=red:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h*0.22"
        ),
    ]

    line_gap = 0.06
    block_center_y = 0.40
    base_y = block_center_y - ((len(hook_lines) - 1) * line_gap / 2)

    for i, line in enumerate(hook_lines):
        safe_line = escape_drawtext_text(line)
        start_time = round(i * 0.6, 2)
        end_time = 5.0
        fade_start = 4.6
        line_y = base_y + i * line_gap

        filters.append(
            (
                f"drawtext="
                f"fontfile='{safe_font_path}':"
                f"text='{safe_line}':"
                f"fontsize=70:"
                f"fontcolor=red:"
                f"borderw=4:"
                f"bordercolor=black:"
                f"enable='between(t,{start_time},{end_time})':"
                f"alpha='if(lt(t,{fade_start}),1,if(lt(t,{end_time}),({end_time}-t)/{end_time-fade_start},0))':"
                f"x=(w-text_w)/2:"
                f"y=h*{line_y}"
            )
        )

    return ",".join(filters)


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


def split_word_items_two_lines(word_items: list, max_line_chars: int = 26) -> list:
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
        midpoint = len(words) // 2
        return [word_items[:midpoint], word_items[midpoint:]]

    return [word_items[:best_split_index], word_items[best_split_index:]]


def group_words_into_cues(words: list, max_words: int = 8, max_chars: int = 52) -> list:
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

        if cue["end"] - cue["start"] < 0.45:
            cue["end"] = cue["start"] + 0.45

    return cues


def build_karaoke_ass_text(word_items: list, max_line_chars: int = 26) -> str:
    if not word_items:
        return ""

    lines = split_word_items_two_lines(word_items, max_line_chars=max_line_chars)
    line_texts = []

    for line in lines:
        segments = []
        for item in line:
            duration_cs = max(1, int(round((float(item["end"]) - float(item["start"])) * 100)))
            word_text = escape_ass_text(str(item["word"]).upper())
            segments.append(r"{\k" + str(duration_cs) + "}" + word_text)
        line_texts.append(" ".join(segments))

    return r"{\an2\bord3\shad0\fscx100\fscy100\fsp0}" + "".join(
        [line_texts[0]] + [r"\N" + text for text in line_texts[1:]]
    )


def write_ass_subtitles(subtitles_path: str, cues: list):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Bebas Neue,68,&H006B6BFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,0,2,50,50,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(subtitles_path, "w", encoding="utf-8") as f:
        f.write(header)
        for cue in cues:
            start = seconds_to_ass_time(cue["start"])
            end = seconds_to_ass_time(cue["end"])
            karaoke_text = build_karaoke_ass_text(cue.get("words", []), max_line_chars=26)
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{karaoke_text}\n")


@app.get("/")
def health():
    return {
        "status": "running",
        "font_exists": os.path.exists(RUNTIME_FONT_FILE),
        "font_path": RUNTIME_FONT_FILE,
        "music_exists": os.path.exists(MUSIC_FILE),
        "music_path": MUSIC_FILE
    }


class RenderRequest(BaseModel):
    numero_regla: str
    hook: str
    guion: str
    subtitles_mode: str = "dynamic"
    audio_base64: str
    normalized_alignment: dict


@app.post("/render")
async def render_video(data: RenderRequest):
    if not os.path.exists(RUNTIME_FONT_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"La fuente no existe en runtime: {RUNTIME_FONT_FILE}"
        )

    job_id = str(uuid.uuid4())

    input_audio_path = os.path.join(AUDIO_DIR, f"{job_id}.mp3")
    normalized_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_normalized.mp3")
    mixed_audio_path = os.path.join(AUDIO_DIR, f"{job_id}_mixed.mp3")
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

    speed_factor = 1.3

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

    if os.path.exists(MUSIC_FILE):
        mix_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-stream_loop", "-1",
            "-i", MUSIC_FILE,
            "-i", normalized_audio_path,
            "-filter_complex",
            "[0:a]volume=0.18[bg];[1:a]volume=1.4[voice];[bg][voice]amix=inputs=2:duration=shortest:dropout_transition=2",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            mixed_audio_path
        ]

        mix_result = subprocess.run(mix_cmd, capture_output=True, text=True)

        if mix_result.returncode == 0 and os.path.exists(mixed_audio_path):
            normalized_audio_path = mixed_audio_path

    audio_duration = round(get_audio_duration(normalized_audio_path), 3)

    adjusted_alignment = speed_up_alignment(data.normalized_alignment, speed_factor)
    words = build_words_from_alignment(adjusted_alignment)
    cues = group_words_into_cues(words, max_words=8, max_chars=52)
    write_ass_subtitles(subtitles_path, cues)

    title_filter = build_title_only_filter(data.numero_regla, data.hook)
    safe_subtitles_path = escape_ffmpeg_path(subtitles_path)
    safe_fonts_dir = escape_ffmpeg_path(FONTS_DIR)
    video_filter = f"{title_filter},subtitles='{safe_subtitles_path}':fontsdir='{safe_fonts_dir}'"
    render_mode = "title_plus_dynamic_subtitles"

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
                "subtitles_path": subtitles_path,
                "audio_path": normalized_audio_path,
                "render_mode": render_mode,
                "cues_count": len(cues),
            }
        )

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=500,
            detail={
                "message": "El video no se generó",
                "video_path": video_path,
                "subtitles_path": subtitles_path,
                "audio_path": normalized_audio_path,
                "render_mode": render_mode,
            }
        )

    return {
        "ok": True,
        "video_url": f"/video/{job_id}.mp4",
        "video_url_full": f"https://ffmpeg-render-api-production-1143.up.railway.app/video/{job_id}.mp4",
        "audio_duration": audio_duration,
        "subtitles_mode_received": data.subtitles_mode,
        "render_mode": render_mode,
        "cues_count": len(cues),
        "speed_factor": speed_factor,
        "music_used": os.path.exists(MUSIC_FILE)
    }
