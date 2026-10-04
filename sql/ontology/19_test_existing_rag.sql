-- Run as ADB_USER. Calls the existing Select AI RAG profile; does not ingest documents.
-- Extracted from blog v1.3; console output and SPOOL commands omitted.

SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => q'~Document ID IR-2026-081、
IR-2026-081_waveform_arena_delay_report.pdfに記載された、
INC-2026-081の障害機材と障害状況を説明してください。
使用した文書のFile Name、Sources、本文で確認できるVersionと
該当箇所を示し、取得できない情報は未確認としてください。~',
  profile_name => 'LSF2026_RAG_PROFILE_PAF',
  action => 'narrate'
) AS RESPONSE FROM DUAL;

SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => q'~Document ID SB-NW-2603、
SB-NW-2603_network_switch_cooling_fan_bulletin.pdfに記載された、
製造Lot NW-2603の交換条件、部品未着時の対応、交換後の確認基準を
説明してください。使用した文書のFile Name、Sources、本文で確認できる
Versionと該当箇所を示し、取得できない情報は未確認としてください。~',
  profile_name => 'LSF2026_RAG_PROFILE_PAF',
  action => 'narrate'
) AS RESPONSE FROM DUAL;

SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => q'~Document ID OPS-NET-2.1、
LSF2026_stage_audio_network_operations_v2.1.pdfに記載された、
Critical条件での予備Switchへの切替手順と復旧後の隔離方針を
説明してください。使用した文書のFile Name、Sources、本文で確認できる
Versionと該当箇所を示し、取得できない情報は未確認としてください。~',
  profile_name => 'LSF2026_RAG_PROFILE_PAF',
  action => 'narrate'
) AS RESPONSE FROM DUAL;
