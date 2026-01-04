from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import yt_dlp

app = FastAPI(title="GoClip Backend")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================
class DownloadRequest(BaseModel):
    url: str
    format: str    # solo "mp4"
    quality: str   # "max", "720", "480"

# =========================
# ENDPOINT
# =========================
@app.post("/download")
def download_video(data: DownloadRequest):
    try:
        os.makedirs("downloads", exist_ok=True)

        file_id = str(uuid.uuid4())
        output_template = f"downloads/{file_id}.%(ext)s"

        # 🎯 FORMATO PROGRESIVO (SIN FFMPEG)
        if data.quality == "720":
            video_format = "best[ext=mp4][height<=720]"
        elif data.quality == "480":
            video_format = "best[ext=mp4][height<=480]"
        else:
            video_format = "best[ext=mp4]"

        ydl_opts = {
            "outtmpl": output_template,
            "format": video_format,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            filename = ydl.prepare_filename(info)

        return FileResponse(
            path=filename,
            media_type="video/mp4",
            filename=os.path.basename(filename)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"status": "GoClip backend ONLINE 🚀"}
