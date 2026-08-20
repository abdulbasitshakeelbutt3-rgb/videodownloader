from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import uvicorn

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
        <input type="text" id="urlInput" placeholder="Paste URL here...">
        <select id="qualitySelect">
            <option value="best">Best Quality</option>
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
            if (!url) { resultDiv.innerHTML = '<p class="error">Please enter a valid URL</p>'; return; }
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
                    resultDiv.innerHTML = `<p class="error">Failed to fetch video.</p>`;
                }
            } catch (err) { resultDiv.innerHTML = `<p class="error">Network error occurred.</p>`; }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTML_CONTENT

class DownloadRequest(BaseModel):
    url: str
    quality: str = "best"

@app.post("/download")
async def download_video(request: DownloadRequest):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('url'):
                        download_url = f.get('url')
                        break
                        
            if not download_url:
                raise Exception("Could not extract download link from the video.")
                
            return {"success": True, "download_url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)