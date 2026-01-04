from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# CORS (importantísimo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/download")
async def get_download_url(req: Request):
    data = await req.json()
    youtube_url = data.get("url")

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": "best[ext=mp4]/best",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)

        # buscamos un formato con audio + video y URL válida
        for f in info["formats"]:
            if (
                f.get("url")
                and f.get("acodec") != "none"
                and f.get("vcodec") != "none"
                and f.get("ext") == "mp4"
            ):
                return {
                    "download_url": f["url"],
                    "title": info.get("title", "goclip_video")
                }

    return {"error": "No se pudo obtener el enlace"}
