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
    # 出力テンプレート：拡張子は後で指定
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

    # musicplayerbot.py の設定をベースに MP3 出力用にカスタマイズ
    ydl_opts = {
        'format': 'bestaudio/best',  # 最高の音声品質を選択
        'outtmpl': outtmpl,
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        # MP3 に変換するためのポストプロセッサ設定
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 変換後のパスは必ず .mp3 になる
            abs_path = os.path.join(save_dir, f"{file_id}.mp3")
            # 日本語タイトルなどに対応したファイル名を作成
            display_name = f"{info.get('title', 'audio')}.mp3"
            
            if not os.path.exists(abs_path):
                 raise FileNotFoundError("MP3 conversion failed.")
            
            return FileResponse(
                path=abs_path, 
                filename=display_name, 
                media_type='audio/mpeg'
            )
    except Exception as e:
        print(f"Download Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
