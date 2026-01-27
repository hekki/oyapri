# oyapri

## 概要

学校などで配布されるPDFプリントをアップロードし、内容を抽出(OCR含む)して検索/質問に根拠付きで回答できるようにするためのプロジェクトです。
Phase 1ではSQLite + FTS5による検索でRAGを行い、Phase 2以降でembedding/pgvectorへの移行を想定しています。

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

3. 起動

```bash
uv run --env-file backend/.env uvicorn app.main:app --reload --app-dir backend
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

ブラウザで `http://localhost:5173` を開き、PDFをアップロードしてください。

### テスト

```bash
make test
```
