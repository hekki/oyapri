# ADR 0005: TiDBの初期スキーマ定義

## ステータス
- 採用

## コンテキスト
- TiDB（さくらのクラウドのエンハンスドDB）を用い、ベクトル検索を標準とする方針に変更した。
- 取り込み〜検索までの最小実装に必要なテーブル設計を確定する必要がある。
- object storage のキーは uuid から規則生成する前提とする。
- embedding モデルに `multilingual-e5-large` を採用するため、ベクトル次元は 1024 となる。

## 決定
- 全テーブルの主キーは `id BIGINT AUTO_INCREMENT` とする。
- 外部参照用に全テーブルに `uuid CHAR(36)` を持たせる。
- `created_at` / `updated_at` は `CURRENT_TIMESTAMP` と `ON UPDATE` を使用する。
- PDF原本やページテキストの object_key はDBに保持せず、uuid等から規則生成する。
- ページ数は `document_pages` の件数から算出し、`documents.page_count` は持たない。
- embedding モデルは `multilingual-e5-large` を採用する。
- チャンクのベクトル列は `VECTOR(1024)` とし、`VEC_COSINE_DISTANCE` の HNSW インデックスを作成する。
- 取得・回答で利用するテーブルは以下とする。
  - `documents`
  - `document_pages`
  - `chunks`
  - `ingest_jobs`

## 影響・結果
- スキーマは `backend/schema.sql` を正とする。
- object storage のキー設計はアプリケーション側で一元管理する。
- 追加の制約（statusのチェック等）はアプリケーション側のバリデーションを前提とする。
