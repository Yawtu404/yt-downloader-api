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
    return {"status": "ok", "message": "MP3 Downloader is ready!"}

@app.get("/download")
def download_audio(url: str):
    save_dir = "/tmp"
    file_id = str(uuid.uuid4())
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

    ydl_opts = {
        # 修正：最初から m4a (軽量) を指定して変換負荷を下げる
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128', # 192から128に下げて処理を高速化
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ダウンロード実行
            info = ydl.extract_info(url, download=True)
            abs_path = os.path.join(save_dir, f"{file_id}.mp3")
            display_name = f"{info.get('title', 'audio')}.mp3"
            
            if os.path.exists(abs_path):
                return FileResponse(
                    path=abs_path, 
                    filename=display_name, 
                    media_type='audio/mpeg'
                )
            else:
                raise FileNotFoundError("MP3 file not found after conversion.")
                
    except Exception as e:
        # エラー内容を詳しくログに出す
        error_msg = str(e)
        print(f"Download Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
