@app.post("/download")
async def download_video(request: DownloadRequest):
    # YouTube aur Instagram ke liye behtareen yt-dlp options aur headers
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
            
            # Direct url nikalne ka safe tareeqa (YouTube/Instagram dono ke liye)
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                # Agar direct url na mile toh formats mein se best select karein
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