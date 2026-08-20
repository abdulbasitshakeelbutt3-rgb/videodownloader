import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("<h3>index.html not found</h3>", status_code=404)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class DownloadRequest(BaseModel):
    url: str

@app.post("/download")
async def download_video(request: DownloadRequest):
    url = request.url
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise HTTPException(status_code=400, detail="Could not extract video details.")
            
            return {
                "success": True,
                "download_url": info.get('url'),
                "filename": f"{info.get('title', 'video').replace('/', '_')}.mp4"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))