# oyapri

## 概要

学校などで配布されるPDFプリントをアップロードし、内容を抽出(OCR含む)して検索/質問に根拠付きで回答できるようにするためのプロジェクトです。

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

### マイグレーション（TiDB）

初回は `backend/migrations/0001_initial.sql` を適用します。

```bash
mysql \
  -h "$TIDB_HOST" \
  -P "$TIDB_PORT" \
  -u "$TIDB_USER" \
  -p"$TIDB_PASSWORD" \
  "$TIDB_DATABASE" \
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

ブラウザで `http://localhost:5173/uploads` を開き、PDFをアップロードしてください。

### テスト

```bash
make test
```
