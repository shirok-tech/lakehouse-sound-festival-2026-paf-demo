# Select AI / RAG設定メモ

## NL2SQL Profile

- Profile Name: `LSF2026_SQL_PROFILE`
- Database Object List:
  - V_STAGE_DELAY_ANALYSIS
  - V_EQUIPMENT_HEALTH_SUMMARY
  - V_GATE_CONGESTION_ANALYSIS
  - V_MERCH_STOCKOUT_ANALYSIS
  - V_REFUND_REQUEST_CONTEXT
  - EXT_INCIDENTS
  - EXT_WEATHER_OBSERVATIONS
- Enforce Object List: 有効

## Vector Index

- Vector Index Name: `LSF2026_DOC_VECTOR`
- Object Storage Location: `<OBJ_URI>/documents/pdf_ascii/`
- Vector DB Provider: Oracle
- Chunk Size: 1000
- Chunk Overlap: 140
- Match Limit: 6
- Distance Metric: Cosine
- Source Offsets: 有効

## Combined Profile

- Profile Name: `LSF2026_OPERATIONS_PROFILE`
- NL2SQL: 有効
- RAG: 有効
- Vector Index: `LSF2026_DOC_VECTOR`

モデル名、リージョン、Credential名は利用環境に合わせて設定します。
