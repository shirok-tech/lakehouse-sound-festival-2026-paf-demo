# Ontologyデモ再現手順

Blog v1.3の本編を、完成済みデータと実行用SQLから再現します。SQL実行ログはSQLファイルに混ぜていません。SQLclまたはSQL*PlusをRepositoryのRootで起動し、接続Userを切り替えて実行します。

## Userと前提

| User | 用途 |
|---|---|
| ADMIN | LSF_AGENT作成、Graph・Directory・Procedure権限の直接付与 |
| ADB_USER | External Table、Relation Table、View、Graph、LSF_KG_APIの所有者 |
| LSF_AGENT | PAF Runtime User。3つのread-only Wrapperを所有 |

SQL Property Graph対応のAutonomous AI Database、Object Storage、OCI CLI、SQLclまたはSQL*Plus、PAFが必要です。ADB_USERのResource Principalに対象Bucket/Prefixの読取りを設定します。`sql/00_variables.sql` の `<OBJECT_STORAGE_NAMESPACE>`、`<BUCKET_NAME>` はローカルで置換します。認証情報や実環境URIをCommitしません。

## 完成済みデータとUpload

`EXT_INCIDENTS` は `data/parquet/incidents/incidents.parquet` を参照します。`INC-2026-091` の `DOCUMENT_ID` はNULLです。参照先が見つからない `WX-2026-009` の文書・気象観測行は追加していません。CSVは確認用に同じ値へそろえています。CSV編集やParquet変換は不要です。

`metadata/document_catalog.csv` はBlogの実行結果に合わせて日本語PDF名を保持します。RAG用PDFは `documents/pdf_ascii/` のASCII名です。`metadata/document_pdf_mapping.csv` がDocument IDで両者を対応付けます。日本語名の出所は `documents/source/document_build_manifest.json` です。

前回環境の追加Upload:

```bash
export OCI_NAMESPACE='<namespace>'
export OCI_BUCKET='<bucket>'
export OCI_REGION='ap-tokyo-1'
# 前回とPrefixが異なる場合のみ:
# export OCI_OBJECT_PREFIX='<existing-prefix>'
bash scripts/upload_ontology_data.sh --dry-run
bash scripts/upload_ontology_data.sh
```

既定Prefixは `lakehouse_sound_festival_2026`。上書きするObjectは次の3件です。

- `<prefix>/data/csv/transactions/incidents.csv`
- `<prefix>/data/parquet/incidents/incidents.parquet`
- `<prefix>/metadata/document_catalog.csv`

初回構築は `scripts/upload_to_object_storage.sh` で `data/`、`documents/pdf_ascii/`、Catalog、Business Termsを配置します。Validation・Generator・Blog原稿はアップロードしません。ADB_USERで参照先と値を確認します。

```sql
SELECT TABLE_NAME, LOCATION FROM USER_EXTERNAL_LOCATIONS
WHERE TABLE_NAME IN ('EXT_INCIDENTS', 'EXT_DOCUMENT_CATALOG');
SELECT INCIDENT_ID, DOCUMENT_ID FROM EXT_INCIDENTS
WHERE INCIDENT_ID = 'INC-2026-091';
```

`DOCUMENT_ID` がNULLにならない場合は旧Parquetを参照しています。LOCATIONとUpload先Object名を照合します。既存External Tableは同じObject名を参照するため再作成不要です。

## 初回構築の順序

前回記事に沿ってADB、Object Storage、PAF、Select AIを準備します。RepoのSQLは接続User別に実行します。

1. ADB_USER: `@sql/00_variables.sql`、`@sql/02_create_parquet_external_tables.sql`、`@sql/03_create_csv_external_tables.sql`、`@sql/04_create_agent_views.sql`。`sql/run_all.sql` はこのOwner側の初期Viewまでを実行する補助スクリプトです。
2. ADMIN: `@sql/00_variables.sql`、`@sql/05_create_agent_readonly_user.sql`。User作成は初回のみです。
3. ADB_USER: `@sql/05_grant_agent_readonly.sql`、`@sql/06_create_action_procedure.sql`。後者は `LSF_IMPROVEMENT_TASKS` を新規作成するので既存環境では再実行しません。
4. 前回の書込みActionデモも使う場合のみ、ADMINからLSF_AGENTへCREATE PROCEDUREを直接付与し、LSF_AGENTで `@sql/06_create_action_wrapper.sql` を実行します。Ontology FlowにはこのActionを登録しません。
5. 既存Select AI RAG Profile `LSF2026_RAG_PROFILE_PAF` と10 PDFのVector Indexを確認します。本編では再取り込み不要です。
6. 下のOntology手順へ進みます。

前回環境がある場合は初回用External Table・User・Action表作成を省略し、3 Objectを上書きして次へ進みます。必要な既存Objectは `EXT_INCIDENTS`、`EXT_STAGES`、`EXT_EQUIPMENT_MASTER`、`EXT_EQUIPMENT_MAINTENANCE`、`V_GATE_CONGESTION_ANALYSIS`、`V_STAGE_DELAY_ANALYSIS`、`V_EQUIPMENT_HEALTH_SUMMARY`、`LSF_IMPROVEMENT_TASKS` です。

## Ontology本編のSQL順序

表内の短い名前も `sql/ontology/` 配下です。Rootから `@sql/ontology/<file>.sql` の形で実行します。

| 順 | User | ファイル・確認 |
|---:|---|---|
| 1 | ADMIN | `00_admin_prerequisites.sql`。LSF_AGENT作成後。CREATE PROPERTY GRAPH、DATA_PUMP_DIR READ/WRITE、CREATE PROCEDUREを直接付与 |
| 2 | ADB_USER | `@sql/00_variables.sql` → `06_create_document_catalog.sql`。未作成時のみExternal Tableを作り、LOCATIONと10行を確認 |
| 3 | ADB_USER | `00_apply_demo_data.sql`。Source確認 → Relation Table → 合成Lot/Task/Document関係 → Location Scope → 件数確認 |
| 4 | ADB_USER | `07_create_node_views.sql` → `08_create_edge_views.sql` → `09_comment_views.sql` |
| 5 | ADB_USER | `10_check_graph_sources_keys_endpoints.sql`。Source、Key、Endpointの3検査がすべて0行 |
| 6 | ADB_USER | `11_create_property_graph.sql`。Vertex 6種類、Edge 8種類 |
| 7 | ADB_USER | `12_lsf_kg_api_spec.sql` → `13_lsf_kg_api_body.sql` → `14_grant_owner_access.sql` → `16_create_v_kg_incident_facts.sql` |
| 8 | LSF_AGENT | `15_create_agent_wrappers.sql` → `17_verify_agent_wrappers.sql` |
| 8a | ADB_USER | `18_check_existing_rag.sql`。既存Profile・Vector Index・10 PDF/22 ChunkとDocument ID対応を確認。`19_test_existing_rag.sql` はRAG応答を再確認する場合のみ |
| 9 | ADB_USER | `20_graph_queries.sql` → `21_api_smoke.sql` → `22_postconditions.sql` → `23_join_comparison.sql` → `24_error_cases.sql` → `25_condition_change_rollback.sql` |
| 任意 | ADB_USER | `26_graph_studio_query.sql` をGraph StudioのSQL Query Editorへ入力 |

実際のOwner名がADB_USERと異なる場合、GRANT、Wrapperの `ADB_USER.`、Graph StudioのSchema修飾子を同じ名前に置き換えます。`EXT_DOCUMENT_CATALOG` が既存なら作成SQLは再利用し、LOCATIONを表示します。異なるLOCATIONやTable定義は自動移行しません。

## 期待結果と再実行

`INC-2026-081` の障害機材は `EQ-NET-WA-01`、Lotは `NW-2603`。同Lotの別機材は `EQ-NET-OM-01` と `EQ-NET-NG-01`。この追加Lot関係は `SYNTHETIC_DEMO`、`BLOG-DEMO-LOT-001` を出所とする合成Relationで、元のEquipment Masterを書き換えません。専用Task2件は `ONTOLOGY_DEMO_SEED` で識別し、Task IDは自動採番です。

Graph APIの期待件数は影響機材2、未完了Task2、文書経路7、Distinct Document 3です。文書IDは `IR-2026-081`、`SB-NW-2603`、`OPS-NET-2.1`。`V_KG_INCIDENT_FACTS` の期待値は最大温度91.755、最大Packet Loss 19.167%、最低Fan RPM 120、期限超過保守1件・最早予定日2026-07-25、影響公演3件・最大遅延29分です。センサー値はIncident当日の機材日次集計です。

`00_apply_demo_data.sql` の再実行は合成Task2件をOPENに戻してCommitします。DDLは暗黙Commitを伴います。Node/Edge View、Graph、Package、Wrapper、Facts Viewの `CREATE OR REPLACE` はObjectを再作成・更新します。`20`～`24` は読み取り検証です。`25_condition_change_rollback.sql` は合成Taskの `CLOSED` をテスト専用値として一時使用し、3ケースをSavepointへRollbackして復元します。実行前に別の未Commit変更を終えてください。

## PAF手動設定と確認質問

1. Data Analysis AgentはLSF_AGENTで接続し、Object Listへ `ADB_USER.V_KG_INCIDENT_FACTS` を追加して強制します。「INC-2026-081の障害機材、最大温度、最大Packet Loss、最低Fan RPM、期限超過保守件数・予定日、影響公演数・最大遅延は？」を単独確認します。
2. Oracle PL/SQL ExecutorのData SourceをLSF_AGENTにし、`LSF_GET_INCIDENT_IMPACT`、`LSF_GET_OPEN_TASKS`、`LSF_GET_RELATED_DOCUMENTS` の3 Wrapperのみ選びます。Auto-commitはOFF。前回のTask書込みActionは選びません。
3. Select AI Bridgeで既存 `LSF2026_RAG_PROFILE_PAF` のNarrateを使います。RAG単独で「SB-NW-2603の交換条件と交換後の確認基準は？」を確認します。
4. Chat Input → Agent Prompt、3 Tool → Agent Tools、Agent Message → Chat Outputを接続します。数値はFacts View、関係はGraph API、手順はRAGで確認するInstructionsを設定します。Graph候補のDocument IDを `metadata/document_pdf_mapping.csv` でASCII File Nameへ対応させ、RAG SourcesとVersionを照合します。
5. 複合質問: 「Waveform ArenaのINC-2026-081について、同じLotの機材はほかのStageにもあるか。未完了Task、関連文書の交換条件・切替手順、数値影響も確認してください」。各Tool返却結果と回答の数値・経路・Sourcesを照合します。

文書候補の指示はSoftで、Database側の厳密Filterではありません。Blog後半のHard KG-guided RAG、比較Flow、回答イメージは本編の完成済み実装と区別します。

## Graph Studio

必要ならADMINがGRAPH_DEVELOPERをADB_USERへ付与します。ADB_USERでGraph Explorer → SQL Property Graphs → ADB_USER → LSF_FESTIVAL_OPS_GRAPHを選び、DriverをSQLにします。Schema Visualizationで6 Vertex定義・8 Edge定義を確認します。`26_graph_studio_query.sql` のSELECTをQuery Editorに入れ、Query Visualizationで2経路・7 Vertex・6 Edgeを確認します。CaptionにIncident ID、Equipment ID、Lot、Stage名などを設定します。Blog掲載画面はADMINログインでADB_USERのGraphを参照したものです。

## 検証範囲と出所

`python3 scripts/validate_dataset.py` と `python3 scripts/validate_ontology.py` を実行します。後者はZIP由来ParquetのSHA-256と構造、CSV、Document ID対応、Graph SQL要素数をローカル確認します。Parquet全行の独立読取照合、OCI Upload、ADBでのコンパイル・実行、PAFのFlow/RAG、Graph Studio表示は実環境で確認します。Blogの過去ログを今回の実行結果として扱いません。

ZIPの14項目中13項目は前回Commit `bd643e6` に同一バイトで収録済みでした。今回のZIP新規取り込みは `ONTOLOGY_VALIDATION.json`。別添の `create_v_kg_incident_facts.sql` は `sql/ontology/16_create_v_kg_incident_facts.sql` へそのまま収録しました。提供された実行用ファイルと今回のDB実行は区別します。
