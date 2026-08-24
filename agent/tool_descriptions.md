# Tool Descriptions

## Festival SQL Analysis Tool

Autonomous AI Lakehouse上のAgent向けViewを自然言語からSQLで分析します。公演遅延、機器センサー、入場ゲート、物販在庫、払戻コンテキスト、気象観測を扱います。

利用対象View:

- V_STAGE_DELAY_ANALYSIS
- V_EQUIPMENT_HEALTH_SUMMARY
- V_GATE_CONGESTION_ANALYSIS
- V_MERCH_STOCKOUT_ANALYSIS
- V_REFUND_REQUEST_CONTEXT
- EXT_INCIDENTS
- EXT_WEATHER_OBSERVATIONS

## Festival Operations RAG Tool

Object Storageの`documents/pdf_ascii/`に配置した運営文書、手順書、ポリシー、インシデント報告、サービス情報を検索します。回答ではDocument ID、Version、該当節を示してください。

## Improvement Task Tool

承認済みの`CREATE_LSF_IMPROVEMENT_TASK`だけを実行します。任意SQLや任意PL/SQLを実行してはいけません。実行前にIncident ID、Title、Description、Priority、Owner Teamを利用者へ提示し、承認を確認してください。
