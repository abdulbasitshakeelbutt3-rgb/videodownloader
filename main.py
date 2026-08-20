@app.post("/download")
async def download_video(request: DownloadRequest):
    url = request.url
    quality = request.quality
    
    if quality == "best":
        format_str = 'best'
    else:
        format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'

    ydl_opts = {
        'format': format_str,
        'noplaylist': True,
        'extractor_args': {
            'facebook': {
                'comment_sort': ['top'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
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