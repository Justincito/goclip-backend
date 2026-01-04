from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class DownloadRequest(BaseModel):
    url: str
    format: str
    quality: str

@app.post("/download")
def download_video(data: DownloadRequest):
    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, file_id)

    if data.format == "mp3":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": output_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        filename = f"{file_id}.mp3"
    else:
        format_map = {
            "best": "best",
            "720": "best[height<=720]",
            "480": "best[height<=480]"
        }

        ydl_opts = {
            "format": format_map.get(data.quality, "best"),
            "outtmpl": output_path + ".%(ext)s"
        }

        filename = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url)
            if not filename:
                filename = ydl.prepare_filename(info)

        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type="application/octet-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
