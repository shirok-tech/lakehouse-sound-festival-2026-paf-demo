# QA Report

検証日: 2026-08-16

## Data

- CSV: 23 files; UTF-8 with BOM; headers and row presence checked
- JSONL: 2 files; JSON parse checked
- Parquet: 21 files; `PAR1` magic, Thrift footer, schema, row group, data page header, row count checked
- Random seed: `20260807`

## Documents

- PDF: 10 files / 27 pages
- All pages rendered at 150 dpi without clipping or overlap
- Text extraction checked
- Key evidence checked: `91.8`, `19.2`, `NW-2603`, `61.4`, `690`, `MG_PREMIUM`

## Spreadsheet

- `metadata/data_dictionary.xlsx`: 6 sheets, 0 formula errors
- `validation/expected_results.xlsx`: 2 sheets, 0 formula errors
- All workbooks reopened successfully with openpyxl

## Blog

- 967 lines
- Markdown code fences balanced
- Heading style checked (`# ■`, `## ●`)
- No unresolved template placeholders

## Expected Findings

- Waveform Arena maximum delay: 29 minutes
- StageLink switch maximum temperature: 91.8 C
- StageLink switch maximum packet loss: 19.2%
- Gate C incident-window failure rate: 61.4%
- Lunar Echo Signal Hoodie stockout: 2026-08-08 17:40 JST
- Auto-approved refund requests: 1,300 / JPY 5,126,000
