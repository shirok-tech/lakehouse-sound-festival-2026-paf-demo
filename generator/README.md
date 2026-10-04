# Generator

Lakehouse Sound Festival 2026の完全合成データ、RAG原稿、ブログMarkdownを再生成します。

## 1. 依存パッケージ

```bash
python -m pip install -r requirements.txt
```

## 2. データ生成

```bash
python generate_data.py
```

乱数シードは`20260807`で固定されています。再生成後も、公開前に必ず`../scripts/validate_dataset.py`を実行して固定シナリオ値が維持されていることを確認してください。
Document Catalogは日本語PDF名を保持し、同時に生成する`metadata/document_pdf_mapping.csv`がDocument IDごとのRAG用ASCII名を記録します。Ontology続編の検証には`../scripts/validate_ontology.py`も実行してください。

## 3. PDF原稿生成

```bash
python generate_documents.py
```

`documents/source/`へHTML原稿を作成します。

## 4. PDF変換

プロジェクトRootで実行します。

```bash
for html in documents/source/*.html; do
  base=$(basename "$html" .html)
  weasyprint "$html" "documents/pdf/$base.pdf"
done
```

## 5. ASCII名のRAG PDFを準備

```bash
python prepare_public_release.py
```

`documents/pdf_ascii/` に公開用の10 PDFを作成します。Object StorageとRAGへ投入するのはこのディレクトリだけです。

## 6. Blog Markdown生成（任意・公開リポジトリへは含めない）

```bash
python generate_blog.py
```

## 7. 検証

`generate_data.py`はCSV、JSONL、Parquetの基本構造を検証します。最後に `python ../scripts/validate_dataset.py` を実行し、非0終了なら公開用データとして使わないでください。
