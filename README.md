# Lakehouse Sound Festival 2026 PAF Demo

Autonomous AI Lakehouse、Autonomous AI Database、Select AI、Private Agent Factory (PAF) を使い、音楽フェス運営を分析する再現可能なハンズオンです。

## Ontology続編

今回の完成済みデータと本編SQLは [Ontology再現手順](docs/ontology-data-setup.md) にまとめました。前回環境がある場合は、`scripts/upload_ontology_data.sh` で修正済みIncident CSV・Parquetと日本語名Catalogを同じObject名へ上書きし、同手順のADMIN → ADB_USER → LSF_AGENTの順で実行します。初回構築の場合は、このREADMEの基盤手順を先に完了します。

`sql/ontology/` にRelation、Location Scope、Node/Edge View、Source/Key/Endpoint検査、SQL Property Graph、LSF_KG_API、3 Wrapper、分析用`V_KG_INCIDENT_FACTS`、APIと条件変更テスト、Graph Studio Queryを収録しています。`metadata/document_pdf_mapping.csv` は日本語名Catalogと`documents/pdf_ascii/`のASCII名をDocument IDで結びます。`INC-2026-091` の未解決な`WX-2026-009`参照は、完成済みParquet上でNULLです。

本編のPAFは既存Select AI RAGを再利用します。文書の再取り込みやHard KG-guided RAGは必須手順ではありません。Graph Studioでは6 Vertex定義・8 Edge定義と、`INC-2026-081`から同Lotの別機材へ至る2経路を可視化します。

## Overview

Lakehouse Sound Festival 2026 は、2026-08-07から2026-08-09に NeoTone Bay Park で開催された架空イベントです。すべてのデータ、人物、組織、製品、文書は完全合成であり、実在の人物・企業・イベントとは無関係です。乱数シードは `20260807`、すべての時刻は Asia/Tokyo です。

## Architecture

`data/parquet/` と必要なCSVを Object Storage に置き、Autonomous AI Database の External Table とAgent向けViewを作成します。SQL Tool はViewを集計し、RAG Tool は `documents/pdf_ascii/` の10 PDFだけを検索します。承認済みアクションは `LSF_AGENT.CREATE_LSF_IMPROVEMENT_TASK` だけを実行します。

## Requirements

- OCI CLI、Object Storage bucket、Autonomous AI Database、Private Agent Factory
- ADBのResource Principalを有効化できる権限
- SQLclまたはSQL*Plus
- Python 3.10+（ローカル検証・再生成用）

## Dataset

全137,535件の合成レコードのうち、ticket_sales 20,800件、admission_logs 37,625件、equipment_sensor_logs 36,975件、merchandise_sales 12,320件、refund_requests 1,500件、attendee_feedback 5,000件、staff_action_logs 196件を含みます。Parquetは21ファイル、RAG文書は10 PDFです。

## Directory Structure

```text
data/                 CSV、Parquet、JSONLの入力データ
documents/pdf_ascii/  RAG投入専用のASCII名Text PDF 10件
documents/source/     PDF原稿
sql/                  External Table、View、権限、Procedure
agent/                PAF設定、テスト質問、最終Custom Instructions
metadata/             文書カタログ、Document ID別PDF名対応、用語集
validation/           人間の正解照合用（アップロード・RAG投入禁止）
generator/            同一Seedでの再生成器
scripts/              uploadとローカル検証
```

`documents/pdf/` は原稿由来の非ASCII名PDFを保管する編集用コピーです。RAGには必ず `documents/pdf_ascii/` だけを使ってください。

## Test Scenarios / Expected Results

1. Waveform Arena (STG-WA) の `INC-2026-081` は PERF-0033/0034/0035の3公演に影響し、最大遅延29分、最大温度91.755 C、最大Packet Loss 19.167%、最低Fan RPM 120、保守予定日2026-07-25・14日超過です。
2. Gate C QR障害は失敗率61.4%、平均待ち時間29.6分、基準成立から切替まで16分です。Firmware 1.8.2の既知問題と基準はRAG文書で確認します。
3. Lunar Echo Hoodieは計画在庫420、関心調整予測690、2026-08-08 17:40 JSTに在庫切れ、Negative Feedbackは250件です。
4. Day 3悪天候に対する払戻は自動承認1,300件、合計5,126,000円です。

## 1. Clone Repository

```bash
git clone https://github.com/shirok-tech/lakehouse-sound-festival-2026-paf-demo.git
cd lakehouse-sound-festival-2026-paf-demo
python3 scripts/validate_dataset.py
python3 scripts/validate_ontology.py
```

## 2. Configure OCI Variables

`sql/00_variables.sql` の `<OBJECT_STORAGE_NAMESPACE>` と `<BUCKET_NAME>` だけを、ローカルコピーで置換します。Namespace、OCID、パスワード、Wallet、Auth TokenをCommitしてはいけません。

## 3. Upload Data to Object Storage

必要な入力だけをアップロードします。

```bash
export OCI_NAMESPACE='<OBJECT_STORAGE_NAMESPACE>'
export OCI_BUCKET='<BUCKET_NAME>'
export OCI_REGION='ap-tokyo-1'
scripts/upload_to_object_storage.sh
```

対象は `data/`、`documents/pdf_ascii/`、`metadata/document_catalog.csv`、`metadata/business_terms.csv` だけです。`validation/`、`generator/`、`blog/`、`.git/`、Wallet、Credential、秘密情報はアップロードしません。

## 4. Enable Autonomous AI Database Resource Principal

Autonomous AI DatabaseのResource Principalを有効化し、Object Storage bucket/prefixを読むDynamic Group/Policyを設定してください。Main Routeは `OCI$RESOURCE_PRINCIPAL` です。Auth Token方式のCredential作成SQLは公開版に含めません。

## 5. Create External Tables

ADB_USERとして `sql/00_variables.sql`、`02_create_parquet_external_tables.sql`、`03_create_csv_external_tables.sql` を順に実行します。Parquetを主データ、CSVをView用のマスタ・計画データに使います。

## 6. Create Agent Views

`sql/04_create_agent_views.sql` を実行します。公開対象は `V_STAGE_DELAY_ANALYSIS`、`V_EQUIPMENT_HEALTH_SUMMARY`、`V_GATE_CONGESTION_ANALYSIS`、`V_MERCH_STOCKOUT_ANALYSIS`、`V_REFUND_REQUEST_CONTEXT` です。

## 7. Create Runtime User and Action Procedure

ADMINで`sql/05_create_agent_readonly_user.sql`を実行し、ADB_USERで`sql/05_grant_agent_readonly.sql`と`sql/06_create_action_procedure.sql`を実行します。前回の書込みActionデモを使う場合だけ、LSF_AGENTで`sql/06_create_action_wrapper.sql`を実行します。Ontology FlowではこのActionを選択しません。

## 8. Create Select AI Profiles

SQL ProfileにはAgent向け5 Viewと必要な読み取り専用External Tableだけを登録し、Object Listを強制します。Main AgentのModel設定とSelect AIのModel設定は別々に構成・検証してください。

## 9. Create Vector Index

`agent/select_ai_settings.md` を参考に、`documents/pdf_ascii/` を唯一のRAG SourceとしてVector Indexを作成します。`validation/` はRAG対象にしてはいけません。

## 10. Configure Private Agent Factory

SQL Tool、RAG Tool、Oracle PL/SQL Executorを構成し、最終版 [LSF2026_Custom_Instructions_v9.txt](agent/LSF2026_Custom_Instructions_v9.txt) をCustom Instructionsへ設定します。PAF Repository UserをFestival用Data Sourceとして使わないでください。

## 11. Test SQL Tool

`agent/test_questions.md` の1-6を使い、`sql/07_validation_queries.sql` と `validation/expected_metrics.json` に一致することを確認します。

## 12. Test RAG Tool

同ファイルの7-11を使い、DJ Linkの復旧手順、Firmware 1.8.2、悪天候停止基準、Ticket Type別払戻条件をPDF根拠で確認します。

## 13. Test SQL + RAG

質問12-15で、数値はSQL、原因・手順・ポリシーはRAGで分離して回答できることを確認します。RAG結果の丸写しやCitation Tagの表示はしません。

## 14. Test Approved Action

質問19では登録案のみを出し、別Turnで利用者が明示承認した後に限り、固定6 IN引数で `LSF_AGENT.CREATE_LSF_IMPROVEMENT_TASK` を実行します。任意DMLは許可しません。DemoのHuman approvalはCustom Instructions中心です。Productionでは外部Approval Gate、監査ログ、職務分離を検討してください。

## Validation

```bash
python3 scripts/validate_dataset.py
```

失敗時は非0で終了します。`validation/` は人間が結果を照合するための正解データで、Object StorageのAgent検索対象やRAG対象に絶対にアップロードしません。

## Regeneration

`generator/README.md` の手順で同一Seed `20260807` を使い再生成し、最後に本検証を実行してください。CSV・JSONL・Parquetの検証値が変わらないことが再現性の条件です。

## Security Notes

- すべての環境固有値は `<OBJECT_STORAGE_NAMESPACE>`、`<BUCKET_NAME>`、`<GENAI_COMPARTMENT_OCID>`、`<ADB_OCID>`、`<ADB_NAME>`、`<ADB_USER_PASSWORD>`、`<LSF_AGENT_PASSWORD>`、`<PAF_PUBLIC_IP>`、`<LOCAL_USER>` 等のPlaceholderだけを使います。
- Password、Wallet、Auth Token、秘密鍵、実メールアドレス、実IP、OCID、実環境パスをCommitしません。
- GitHub公開前に `rg` によるSecurity Scanを実施してください。

## Cleanup

Object Storageの `lakehouse_sound_festival_2026/` prefix、External Table、View、Vector Index、Select AI Profile、LSF_AGENT、デモ用改善タスクを、組織の保持ポリシーに従って削除してください。

## Troubleshooting

- External Tableが読めない: Resource PrincipalのDynamic Group/Policy、URI、Object Storage prefixを確認します。
- RAGで文書が見つからない: `documents/pdf_ascii/` の10 PDFだけが索引対象か確認します。
- Actionが実行できない: 別Turnの明示承認、wrapper名、固定6 IN引数、EXECUTE権限を確認します。

## License

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
