from fastapi import FastAPI
import subprocess
import uuid

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/render")
def render():
    
    image = "image.jpg"
    audio = "audio.mp3"
    output = f"video_{uuid.uuid4()}.mp4"

    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image,
        "-i", audio,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output
    ]

    subprocess.run(command)
    return {"video": output}
