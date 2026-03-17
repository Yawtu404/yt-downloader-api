from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid

app = FastAPI()

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
    # 拡張子は yt-dlp に任せるため指定しない
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

    ydl_opts = {
        # 修正ポイント1: 形式を「最高画質」に指定。合体は ffmpeg に任せる
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        # 修正ポイント2: ダウンロード後に強制的に mp4 に変換する
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 変換後のファイル名は必ず .mp4 になる
            abs_path = os.path.join(save_dir, f"{file_id}.mp4")
            display_name = f"{info.get('title', 'video')}.mp4"
            
            if not os.path.exists(abs_path):
                 # 万が一mp4がない場合、実際に保存されたファイルを探す
                 abs_path = ydl.prepare_filename(info)
            
            return FileResponse(
                path=abs_path, 
                filename=display_name, 
                media_type='video/mp4'
            )
    except Exception as e:
        print(f"Download Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
