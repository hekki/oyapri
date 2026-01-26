# OYAPRI

- 学校などで配布されるPDFプリントをアップロードし、内容を抽出(OCR含む)してembedding化し、ブラウザから日本語で質問すると根拠付きで回答できるようにする。

## Non-negotiable rules
- プリントの内容・質問・返答・UI文言・コードコメントは日本語（技術用語は必要に応じて併記OK）
- 回答は「根拠(ドキュメントID/ページ/引用)」を必ず付ける
- 根拠にない推測はしない。足りない場合は「不明」と書き、追加情報を求める
- PDFがテキスト抽出できない場合はOCRにフォールバックする（スキャンPDF想定）
- 12factor.net を尊重する

## Architecture
- Storage:
  - さくらのオブジェクトストレージを使用する
  - 原本PDFを保存する
  - PDFから抽出したテキスト（ページ単位の中間成果物）も保存する
- Database:
  - Phase 1:
    - SQLite を使用する
    - 検索は SQLite FTS5（全文検索）を用いる
    - 正本データ（documents / chunks）と検索用FTSテーブルを分離する
  - Phase 2+ (future):
    - PostgreSQL + pgvector への移行を前提とする
    - 検索処理は `retrieve()` インターフェースで抽象化し、実装差し替え可能にする
- Worker / Queue:
  - PDFの取り込み（ingest）は非同期ジョブとして実行する
  - キューは「さくらのシンプルMQ」を使用する
  - 可視性タイムアウト/再配信を考慮し、ジョブは冪等にする
  - 処理内容
    - PDF取得 → テキスト抽出
    - テキスト抽出できない場合はOCRにフォールバック
    - テキストのチャンク化
    - SQLite（chunks + FTS）への登録

## Retrieval / Answering policy
- Phase 1では embedding / vector search は使わず、FTS5で候補チャンクを取得してRAGする
- LLMへの入力は「検索で得られた根拠チャンク」に限定し、根拠外の推測を禁止する
- レスポンスは JSON で `answer` と `citations`（doc/page/quote）を返せる形にする

## Architecture Decision Records (ADR)
- 本プロジェクトの設計判断・方針変更は `adr/` ディレクトリに ADR として都度追加する
- ADR は時系列で管理し、過去の決定を上書きせず履歴として残す
- 実装・変更を行う際は、必ず関連する ADR を参照し、それに反しないことを確認する
- 新たな重要な設計判断（例：検索方式変更、データモデル変更、外部サービス採用）は、実装前に ADR を追加する

## Coding style
- 変更は小さく、既存構造に合わせる
- 依存追加は最小限。新規依存を入れる前に理由を説明して確認する
- I/O（Object Storage / MQ / OCR / LLM）はインターフェース化し、テストで差し替え可能にする

## Testing
- 全てのビジネスロジックに対してユニットテストを実装する
- `make test` で実行可能とする
