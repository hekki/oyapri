# ADR 0006: documentsに元ファイル名を保持する

## ステータス
- 採用

## コンテキスト
- `documents.title` はPDF内容から抽出する前提としている。
- ユーザーがアップロードした元ファイル名も保持したい。

## 決定
- `documents.original_filename` を追加し、アップロード時の元ファイル名を保存する。

## 影響・結果
- 追加カラムはマイグレーション `backend/migrations/0002_add_documents_original_filename.sql` で適用する。
