# oyapri

## 概要

学校などで配布されるプリント画像（PNG/JPEG）をアップロードし、内容をOCRで抽出して検索/質問に根拠付きで回答できるようにするためのプロジェクトです。

## 起動手順

### バックエンド

1. 依存関係のインストール

```bash
uv venv --python 3.14
source .venv/bin/activate
uv sync
```

2. 環境変数の設定

```bash
cp backend/.env.example backend/.env
```

`.env` を編集して、さくらのオブジェクトストレージ(S3互換)の情報を設定してください。
OCRとEmbeddingの設定もこのファイルで行います。
チャンク分割は `CHUNK_SIZE` と `CHUNK_OVERLAP` で調整できます。embeddingの上限に合わせて小さめに設定してください。
さらに上限対策として `EMBEDDING_MAX_TOKENS` と `EMBEDDING_CHARS_PER_TOKEN` に基づき、文字数の上限で再分割します。

### 検索API

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"1月の行事予定","top_k":5}'
```

### 質問API（RAG）

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"2月のイベントを教えて","top_k":5}'
```

3. 起動

```bash
uv run --env-file backend/.env uvicorn app.main:app --reload --app-dir backend
```

### ワーカー（SimpleMQ）

メッセージをポーリングして取り込み処理を実行します。

```bash
PYTHONPATH=backend uv run --env-file backend/.env python -m app.worker.simplemq_runner
```

単発で `job_id` を指定して処理する場合:

```bash
PYTHONPATH=backend uv run --env-file backend/.env python -m app.worker.ingest <job_id>
```

### マイグレーション（MySQL互換DB）

初回は `backend/migrations/0001_initial.sql` を適用します。

```bash
mysql \
  -h "$MYSQL_HOST" \
  -P "$MYSQL_PORT" \
  -u "$MYSQL_USER" \
  -p"$MYSQL_PASSWORD" \
  "$MYSQL_DATABASE" \
  < backend/migrations/0001_initial.sql
```

### フロントエンド

1. 依存関係のインストール

```bash
cd frontend
npm install
```

2. 起動

```bash
npm run dev
```

ブラウザで `http://localhost:5173/` を開き、画像をアップロードしてください。

### テスト

```bash
make test
```
