# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Botコードをコピー
COPY . .

# Flask (keep_alive) 用ポート
EXPOSE 8080

# 起動コマンド
CMD ["python", "main.py"]
