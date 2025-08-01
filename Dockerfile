# マルチステージビルド
FROM python:3.12-slim as builder

# 作業ディレクトリ設定
WORKDIR /app

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番ステージ
FROM python:3.12-slim

# 作業ディレクトリ設定
WORKDIR /app

# 非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# ビルドステージから依存関係をコピー
COPY --from=builder /root/.local /home/appuser/.local

# アプリケーションコードをコピー
COPY . .

# 権限設定
RUN chown -R appuser:appuser /app
USER appuser

# PATHにローカルbinを追加
ENV PATH=/home/appuser/.local/bin:$PATH

# 環境変数設定
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# ポート設定
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=10)" || exit 1

# アプリケーション起動
CMD ["python", "-m", "uvicorn", "services.auth.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]