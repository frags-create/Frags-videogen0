================================

FILE: app.py

================================

FRAGMENTS backend for Railway (FREE tier)

GitHub deploy-ready

from fastapi import FastAPI, UploadFile, Form from fastapi.responses import FileResponse, JSONResponse from fastapi.middleware.cors import CORSMiddleware import yt_dlp import uuid import os from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

app = FastAPI()

----------------

CORS (allow frontend to connect)

----------------

app.add_middleware( CORSMiddleware, allow_origins=[""],  # later restrict to your domain allow_methods=[""], allow_headers=["*"], )

----------------

Health check

----------------

@app.get("/") def root(): return {"status": "FRAGMENTS backend running"}

----------------

Main API endpoint

----------------

@app.post("/api/predict") async def predict( prompt: str = Form(...), voice_file: UploadFile = Form(...), videoLinks: list[str] = Form(...) ): session_id = str(uuid.uuid4()) workdir = f"/tmp/{session_id}" os.makedirs(workdir, exist_ok=True)

downloaded_videos = []

# ----------------
# Download YouTube videos
# ----------------
ydl_opts = {
    "format": "mp4",
    "outtmpl": f"{workdir}/%(id)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for link in videoLinks:
            info = ydl.extract_info(link, download=True)
            downloaded_videos.append(f"{workdir}/{info['id']}.mp4")
except Exception as e:
    return JSONResponse({"error": f"Video download failed: {str(e)}"}, status_code=400)

# ----------------
# Save uploaded voice file
# ----------------
voice_path = f"{workdir}/voice.mp3"
with open(voice_path, "wb") as f:
    f.write(await voice_file.read())

# ----------------
# Build final video
# ----------------
try:
    clips = []
    for video in downloaded_videos:
        clip = VideoFileClip(video).subclip(0, 15)
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(voice_path)
    final_video = final_video.set_audio(audio)

    output_path = f"{workdir}/final.mp4"
    final_video.write_videofile(
        output_path,
        fps=60,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )
except Exception as e:
    return JSONResponse({"error": f"Video processing failed: {str(e)}"}, status_code=500)

return FileResponse(
    output_path,
    media_type="video/mp4",
    filename="generated_video.mp4"
)

================================
