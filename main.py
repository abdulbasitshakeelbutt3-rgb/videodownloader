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
    <title>Cinvibe - Professional Video Downloader</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.75);
            --primary-gold: #f59e0b;
            --accent-glow: rgba(245, 158, 11, 0.2);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: rgba(255, 255, 255, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 50% 0%, #1f2937 0%, var(--bg-color) 75%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 520px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            text-align: center;
        }

        .logo-area {
            margin-bottom: 25px;
        }

        .logo-area h1 {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, #fff 0%, var(--primary-gold) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .logo-area p {
            color: var(--text-muted);
            font-size: 14px;
        }

        .input-group {
            position: relative;
            margin-bottom: 20px;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        input[type="text"] {
            width: 100%;
            background: rgba(3, 7, 18, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px 110px 16px 45px;
            color: var(--text-main);
            font-size: 15px;
            outline: none;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: var(--primary-gold);
            box-shadow: 0 0 15px var(--accent-glow);
        }

        .input-icon {
            position: absolute;
            left: 16px;
            color: var(--text-muted);
            font-size: 16px;
        }

        .input-actions {
            position: absolute;
            right: 8px;
            display: flex;
            gap: 5px;
        }

        .icon-btn {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            color: var(--text-muted);
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .icon-btn:hover {
            background: rgba(245, 158, 11, 0.2);
            color: var(--primary-gold);
        }

        .btn-download {
            width: 100%;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: #000;
            font-weight: 600;
            font-size: 16px;
            padding: 16px;
            border: none;
            border-radius: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        }

        .loading-spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0,0,0,0.3);
            border-radius: 50%;
            border-top-color: #000;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .result-box {
            margin-top: 25px;
            display: none;
            animation: fadeIn 0.4s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .download-link-btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10b981;
            color: #34d399;
            padding: 14px 24px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }

        .download-link-btn:hover {
            background: rgba(16, 185, 129, 0.25);
        }

        .error-msg {
            color: #f87171;
            font-size: 13px;
            margin-top: 15px;
            display: none;
            word-break: break-all;
            text-align: left;
            background: rgba(248, 113, 113, 0.1);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(248, 113, 113, 0.2);
        }

        footer {
            margin-top: 30px;
            color: var(--text-muted);
            font-size: 13px;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="logo-area">
            <h1>Cinvibe Downloader</h1>
            <p>Download public videos from YouTube & Instagram instantly</p>
        </div>

        <div class="input-group">
            <div class="input-wrapper">
                <i class="fa-solid fa-link input-icon"></i>
                <input type="text" id="videoUrl" placeholder="Paste video link here...">
                <div class="input-actions">
                    <button class="icon-btn" onclick="pasteClipboard()" title="Paste">
                        <i class="fa-solid fa-clipboard"></i>
                    </button>
                    <button class="icon-btn" onclick="clearInput()" title="Clear">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            </div>
        </div>

        <button class="btn-download" id="submitBtn" onclick="processDownload()">
            <span id="btnText">Process & Download</span>
            <div class="loading-spinner" id="spinner"></div>
        </button>

        <div class="error-msg" id="errorMsg"></div>

        <div class="result-box" id="resultBox">
            <a id="downloadAnchor" href="#" target="_blank" class="download-link-btn">
                <i class="fa-solid fa-cloud-arrow-down"></i> Click Here to Download Video
            </a>
        </div>
    </div>

    <footer>
        Powered by Cinvibe Engine &bull; Fast & Secure
    </footer>

    <script>
        async function pasteClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('videoUrl').value = text;
            } catch (err) {
                alert('Clipboard permission denied or unavailable.');
            }
        }

        function clearInput() {
            document.getElementById('videoUrl').value = '';
            document.getElementById('resultBox').style.display = 'none';
            document.getElementById('errorMsg').style.display = 'none';
        }

        async function processDownload() {
            const urlInput = document.getElementById('videoUrl').value.trim();
            const errorMsg = document.getElementById('errorMsg');
            const resultBox = document.getElementById('resultBox');
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            const downloadAnchor = document.getElementById('downloadAnchor');

            errorMsg.style.display = 'none';
            resultBox.style.display = 'none';

            if (!urlInput) {
                errorMsg.innerText = "Please paste a valid video URL first!";
                errorMsg.style.display = 'block';
                return;
            }

            submitBtn.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'block';

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput })
                });

                const data = await response.json();

                if (response.ok && data.success && data.download_url) {
                    downloadAnchor.href = data.download_url;
                    resultBox.style.display = 'block';
                } else {
                    errorMsg.innerText = data.detail || "Could not process this video. Try another link.";
                    errorMsg.style.display = 'block';
                }
            } catch (err) {
                errorMsg.innerText = "Network error or server is waking up. Please try again.";
                errorMsg.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
            }
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

@app.post("/download")
async def download_video(request: DownloadRequest):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web_creator', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
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
                raise Exception("Could not extract direct download link.")
                
            return {"success": True, "download_url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)