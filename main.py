from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import yt_dlp

# =========================
# APP
# =========================
app = FastAPI(title="GoClip Backend")

# =========================
# CORS (CLAVE PARA EXTENSIONES)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para que funcione desde chrome-extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELO DE REQUEST
# =========================
class DownloadRequest(BaseModel):
    url: str
    format: str   # "mp4" o "mp3"
    quality: str  # "max", "720", "480"

# =========================
# ENDPOINT PRINCIPAL
# =========================
@app.post("/download")
def download_video(data: DownloadRequest):
    try:
        # carpeta temporal
        os.makedirs("downloads", exist_ok=True)

        file_id = str(uuid.uuid4())
        output_path = f"downloads/{file_id}.%(ext)s"

        # =========================
        # OPCIONES YTDLP
        # =========================
        ydl_opts = {
            "outtmpl": output_path,
            "quiet": True,
        }

        # ---- MP3 ----
        if data.format == "mp3":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })

        # ---- MP4 ----
        else:
            if data.quality == "720":
                ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
            elif data.quality == "480":
                ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"

            ydl_opts["merge_output_format"] = "mp4"

        # =========================
        # DESCARGA
        # =========================
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            ext = "mp3" if data.format == "mp3" else "mp4"
            filename = f"downloads/{file_id}.{ext}"

        # =========================
        # RESPUESTA
        # =========================
        return FileResponse(
            path=filename,
            media_type="application/octet-stream",
            filename=os.path.basename(filename)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ROOT (OPCIONAL)
# =========================
@app.get("/")
def root():
    return {"status": "GoClip backend ONLINE 🚀"}
