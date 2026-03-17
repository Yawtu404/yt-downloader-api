from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "YouTube Downloader is ready!"}

@app.get("/download")
def download_video(url: str):
    save_dir = "/tmp"
    file_id = str(uuid.uuid4())
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

ydl_opts = {
        # 修正ポイント：より柔軟なフォーマット指定に変更
        'format': 'best[ext=mp4]/best', 
        'outtmpl': outtmpl,
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 動画のダウンロード実行
            info = ydl.extract_info(url, download=True)
            abs_path = ydl.prepare_filename(info)
            display_name = f"{info.get('title', 'video')}.mp4"
            
            return FileResponse(
                path=abs_path, 
                filename=display_name, 
                media_type='video/mp4'
            )
    except Exception as e:
        print(f"Download Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
