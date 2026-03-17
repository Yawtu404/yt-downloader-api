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
    return {"status": "ok", "message": "Stable MP3 Downloader is ready!"}

@app.get("/download")
def download_audio(url: str):
    save_dir = "/tmp"
    file_id = str(uuid.uuid4())
    # ファイル保存名のテンプレート
    outtmpl = f"{save_dir}/{file_id}.%(ext)s"

ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'cookiefile': 'cookies.txt', 
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
                'skip': ['webpage', 'configs'],
                # 先ほど取得した visitor_data を貼り付け
                'visitor_data': 'CgtQNEVIUldXRVAtQSiXueTNBjIKCgJKUBIEGgAgC2LfAgrcAjE2LllUPUNGX1ZwRmlGbnhEMjI4VnN4VFFOVWlWX3RpeWVYSVJFM2tQaWdmSHhXdlVBYWFjaWlFRkVWV19zajkyZXI4a0p1bVphMlFRelo5ZmpTNjhCdkM2dlFSZTRHbUU0OENxZnZkeHVfVDkzX3UyOEhjc3ZhWktSNFBZd0pYaDhXQV92cDZQLVUyb0hTRUxGVW9EUjhGT3E4UlY1bXh6amlSMzU2X1g5RGZtbWZ1LTBzSnVQTHQzTkxLZVR4V3FTUVdiR3RMV3hNeXBOWVRvSlhXeDQ0WG5LdS1MNEhvRS1SWGY4RlhTQTRWVlJMaGlPaWJnS1l4dkhiWTl2TFg3eU5zSXM4czczdVp3X1Y2dzlqdEEyZUtEWl9BLTl3SXBnbHBGR18tZk5aQ2l4TUpjQVlyaVFINFp1TU50ck1WRFZVVFVXbnFrSk1icHFrdmZzYnVfQzIybmtWZw%3D%3D'
            }
        },
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 動画情報の取得とダウンロード実行
            info = ydl.extract_info(url, download=True)
            # 変換後のMP3ファイルパス
            abs_path = os.path.join(save_dir, f"{file_id}.mp3")
            # ダウンロード時のファイル名（動画タイトル.mp3）
            display_name = f"{info.get('title', 'audio')}.mp3"
            
            if os.path.exists(abs_path):
                return FileResponse(
                    path=abs_path, 
                    filename=display_name, 
                    media_type='audio/mpeg'
                )
            else:
                raise FileNotFoundError("MP3 conversion failed.")
                
    except Exception as e:
        error_msg = str(e)
        print(f"Download Error: {error_msg}")
        # 429エラー（IPブロック）の場合に原因を分かりやすく表示
        if "429" in error_msg:
            error_msg = "YouTube blocked the server IP. Please wait or update cookies."
        raise HTTPException(status_code=500, detail=error_msg)
