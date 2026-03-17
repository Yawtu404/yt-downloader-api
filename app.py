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
    return {"status": "ok", "message": "High-Stability MP3 Downloader is ready!"}

@app.get("/download")
def download_audio(url: str):
    save_dir = "/tmp"
    file_id = str(uuid.uuid4())
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        # --- ここからブロック回避のための重要設定 ---
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'], # 複数のクライアントを試行
                'skip': ['dash', 'hls']             # 重いストリーミング形式をスキップ
            }
        },
        # ------------------------------------------
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            abs_path = os.path.join(save_dir, f"{file_id}.mp3")
            display_name = f"{info.get('title', 'audio')}.mp3"
            
            return FileResponse(
                path=abs_path, 
                filename=display_name, 
                media_type='audio/mpeg'
            )
    except Exception as e:
        error_msg = str(e)
        print(f"Download Error: {error_msg}")
        # 429エラーが出た場合の分かりやすいメッセージ
        if "429" in error_msg:
            error_msg = "YouTube temporarily blocked this server (Error 429). Please try again in a few minutes."
        raise HTTPException(status_code=500, detail=error_msg)
