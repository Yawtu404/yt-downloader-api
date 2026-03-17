FROM python:3.10-slim

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# 依存関係のインストール
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 全ファイルのコピー
COPY . .

# 一時フォルダの権限設定
RUN chmod -R 777 /tmp
# 0.0.0.0で待ち受け、ポートは環境変数PORT（デフォルト7860）を使用する
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
