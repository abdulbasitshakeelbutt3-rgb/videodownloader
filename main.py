from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Video Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 450px; text-align: center; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #475569; background: #0f172a; color: #fff; border-radius: 6px; box-sizing: border-box; }
        button { background: #3b82f6; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background: #2563eb; }
        #result { margin-top: 20px; word-break: break-all; }
        .error { color: #ef4444; }
        .loading { color: #38bdf8; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Video Downloader</h2>
        <p style="color: #94a3b8; font-size: 0.9rem;">Paste YouTube or Instagram URL</p>
        <input type="text" id="urlInput" placeholder="https://www.youtube.com/watch?v=...">
        
        <select id="qualitySelect">
            <option value="best">Best Quality (Auto)</option>
            <option value="1080">1080p</option>
            <option value="720">720p</option>
            <option value="360">360p</option>
        </select>

        <button onclick="processDownload()">Download Video</button>
        <div id="result"></div>
    </div>

    <script>
        async function processDownload() {
            const url = document.getElementById('urlInput').value.trim();
            const quality = document.getElementById('qualitySelect').value;
            const resultDiv = document.getElementById('result');
            
            if (!url) {
                resultDiv.innerHTML = '<p class="error">Please enter a valid URL</p>';
                return;
            }
            resultDiv.innerHTML = '<p class="loading">Processing video, please wait...</p>';

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, quality: quality })
                });
                const data = await response.json();
                
                if (response.ok && data.success) {
                    resultDiv.innerHTML = `<p style="color: #22c55e;">Success!</p><a href="${data.download_url}" target="_blank"><button>Download File (.mp4)</button></a>`;
                } else {
                    resultDiv.innerHTML = `<p class="error">${data.detail || 'Failed to fetch video.'}</p>`;
                }
            } catch (err) {
                resultDiv.innerHTML = `<p class="error">Network error occurred.</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTML_CONTENT

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class DownloadRequest(BaseModel):
    url: str
    quality: str = "best"

@app.post("/download")
async def download_video(request: DownloadRequest):
    url = request.url
    quality = request.quality
    
    # Format selection logic based on user choice
    if quality == "best":
        format_str = 'best'
    else:
        format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'

    ydl_opts = {
        'format': format_str,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
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