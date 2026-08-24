#!/usr/bin/env python3
"""Create the ASCII-named RAG PDF set after regenerating the source PDFs."""
from __future__ import annotations

from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "documents" / "pdf"
TARGET = ROOT / "documents" / "pdf_ascii"
NAMES = {
    "IR-2026-081_Waveform_Arena遅延報告.pdf": "IR-2026-081_waveform_arena_delay_report.pdf",
    "IR-2026-084_Gate_C混雑報告.pdf": "IR-2026-084_gate_c_congestion_report.pdf",
    "LSF2026_入場ゲート障害対応手順_v1.2.pdf": "LSF2026_admission_gate_incident_response_v1.2.pdf",
    "LSF2026_改善タスク登録手順.pdf": "LSF2026_improvement_task_registration_procedure.pdf",
    "LSF2026_物販売上在庫計画会議議事録.pdf": "LSF2026_merchandise_inventory_planning_minutes.pdf",
    "LSF2026_運営統括マニュアル_v1.3.pdf": "LSF2026_operations_management_manual_v1.3.pdf",
    "LSF2026_悪天候対応計画_v1.4.pdf": "LSF2026_severe_weather_contingency_plan_v1.4.pdf",
    "LSF2026_ステージ音響ネットワーク運用手順_v2.1.pdf": "LSF2026_stage_audio_network_operations_v2.1.pdf",
    "LSF2026_チケット払戻ポリシー_v2.0.pdf": "LSF2026_ticket_refund_policy_v2.0.pdf",
    "SB-NW-2603_ネットワークスイッチ冷却ファン通知.pdf": "SB-NW-2603_network_switch_cooling_fan_bulletin.pdf",
}


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for source_name, target_name in NAMES.items():
        source = SOURCE / source_name
        if not source.exists():
            raise FileNotFoundError(f"Generate source PDF first: {source}")
        copy2(source, TARGET / target_name)
    print(f"Prepared {len(NAMES)} ASCII-named RAG PDFs in {TARGET}")


if __name__ == "__main__":
    main()
