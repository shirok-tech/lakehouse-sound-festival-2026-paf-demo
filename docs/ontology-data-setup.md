# Ontology記事用データの追加・更新

前回記事の環境に、GitHubで配布する完成済みデータとSQLを適用します。
利用者がCSVを編集したり、Parquetへ変換したりする必要はありません。
pandas、PyArrow、DuckDBのインストールも不要です。

## 更新内容

| 対象 | 処理 |
|---|---|
| `incidents.parquet` | `INC-2026-091`の`document_id`を`WX-2026-009`からNULLへ修正。24行・13列を維持し、他の値は変更しない |
| `incidents.csv` | 確認用CSVの同じ欄を空欄にしてParquetと内容をそろえる |
| `LSF_KG_LOT_PATCH` | 2機材を合成Relationとして`NW-2603`へ関連付ける |
| `LSF_IMPROVEMENT_TASKS` | デモ専用Taskを2件追加・更新。Task IDはIdentityで採番する |
| Task／LotとDocumentのRelation | Task–Equipment 2件、Task–Document 4件、Lot–Document 2件を追加・更新 |
| Scope監査View | 確認済みのGate・物販エリアを`OUT_OF_SCOPE`として定義する |

`WX-2026-009`は配布Catalog・確認した気象観測データに参照先が見つからないため、今回のデモでは未解決の文書参照を外します。Incident自体と悪天候の記述は残します。気象情報をDocumentとして作り足したり、例外表でエラーを隠したりしません。

Lotの追加Relationは検証用の合成データです。Equipment Master自体のLotは書き換えません。

## 1. 配布データを取得

この変更をGitHubへ反映した後、新しい作業ディレクトリで取得します。

```bash
git clone https://github.com/shirok-tech/lakehouse-sound-festival-2026-paf-demo.git lakehouse-sound-festival-ontology
cd lakehouse-sound-festival-ontology
git rev-parse HEAD
```

GitHubの「Code → Download ZIP」でも取得できます。
更新前のCommit `5c1858428f311b31adbff5aa0c646f780f81594d`には今回のSQLがないため、そこへcheckoutし直さないでください。

## 2. 完成済みファイルをObject Storageへアップロード

前回と同じOCI CLIの認証設定を使用します。前回設定済みなら環境変数はその値を再利用します。

```bash
export OCI_NAMESPACE='自分のnamespace'
export OCI_BUCKET='lakehouse_sound_festival'
export OCI_REGION='ap-tokyo-1'
bash scripts/upload_ontology_data.sh
```

このスクリプトは、既存Objectの次の2ファイルを上書きします。他の配布データとPDFはアップロードしません。

```text
lakehouse_sound_festival_2026/data/csv/transactions/incidents.csv
lakehouse_sound_festival_2026/data/parquet/incidents/incidents.parquet
```

前回のPrefixを変更している場合だけ、`OCI_OBJECT_PREFIX`へ実際のPrefixを設定します。
`bash scripts/upload_ontology_data.sh --dry-run`でアップロード先だけを表示できます。
OCI Consoleを使う場合も、ダウンロードした同じParquetを同じObject名へ上書きし、CSVもそろえれば完了です。

`EXT_INCIDENTS`を所有するUserで次を確認します。

```sql
SELECT TABLE_NAME, LOCATION
FROM USER_EXTERNAL_LOCATIONS
WHERE TABLE_NAME = 'EXT_INCIDENTS';

SELECT INCIDENT_ID, DOCUMENT_ID
FROM EXT_INCIDENTS
WHERE INCIDENT_ID = 'INC-2026-091';
```

`DOCUMENT_ID`がNULLになることを確認します。同じURI・互換性のある列型を使うため、既存External TableをDROPして作り直す手順は不要です。まだ旧IDが返る場合は、実際のLOCATIONとアップロード先Object名を照合してください。

## 3. 今回用の補足データをSQLで追加

前回記事のExternal Table、`V_GATE_CONGESTION_ANALYSIS`、`LSF_IMPROVEMENT_TASKS`を作成済みで、今回記事の`EXT_DOCUMENT_CATALOG`が参照できることを前提とします。
SQLclまたはSQL*PlusをRepositoryのRootから起動し、データ所有者（記事では`ADB_USER`）の専用セッションで実行します。

```sql
@sql/ontology/00_apply_demo_data.sql
```

このSQLは、元データ確認→不足する補足Tableの作成→データ登録→Scope View作成→件数確認の順に実行します。既存の同名Tableは再利用しますが、別定義のTableを自動移行する機能はありません。

期待する確認結果は次のとおりです。

| 検査 | 件数 |
|---|---:|
| `SCOPE_UNKNOWN_OR_MISSING` | 0 |
| `EQUIPMENT_STAGE_SOURCE` | 0 |
| `INCIDENT_DOCUMENT_SOURCE` | 0 |
| `DEMO_LOT_PATCH` | 2 |
| `DEMO_OPEN_TASKS` | 2 |
| `DEMO_TASK_EQUIPMENT` | 2 |
| `DEMO_TASK_DOCUMENT` | 4 |
| `DEMO_LOT_DOCUMENT` | 2 |

Taskの再実行では、この2件のデモ専用Taskを`OPEN`へ戻します。登録済みTask IDは維持します。
DDLは暗黙Commitを伴い、データ登録はそのBlockでCommitするため、スクリプト全体を1つのRollbackで戻すことはできません。途中失敗時は原因を直して再実行します。

ここまでがデータ準備です。続いて記事のGraph用View、全Source／Edge検査、Property Graph、API、PAF設定を実施します。このスクリプトだけではGraphやPAF Agentは作成しません。

## 配布元の管理者向け

今回の配布ZIPは、既存Repositoryへ重ねる更新ファイルです。ZIP直下の`data`、`sql`、`scripts`、`generator`、`docs`を同名ディレクトリへ配置し、差分を確認してCommit／Pushします。

```bash
git status --short
git diff --stat
python3 scripts/validate_dataset.py
git add data/csv/transactions/incidents.csv \
  data/parquet/incidents/incidents.parquet \
  data/parquet/incidents/incidents.parquet.schema.json \
  generator/generate_data.py scripts/validate_dataset.py \
  scripts/upload_ontology_data.sh sql/ontology docs/ontology-data-setup.md
git commit -m "Add ontology demo data setup and fix incident document reference"
git push
```

記事の公開前に、反映後のCommit IDを記録し、デモ環境でアップロードとSQLを実行して期待件数を確認してください。古いCommit IDを新しい配布ファイルの取得先として案内しないでください。

完成済みParquetは、`document_id`の文字列型を維持してNULLを格納できる列へ変更しています。他12列の型・NULL許可属性は元ファイルと同じです。CSV生成元の該当値も修正済みです。

## 参照

- [前回記事](https://qiita.com/shirok/items/ad6a82f1cfe0ebc72f43)
- [公開Repository](https://github.com/shirok-tech/lakehouse-sound-festival-2026-paf-demo)
- [OCI CLI: object put](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/os/object/put.html)
