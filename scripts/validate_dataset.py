#!/usr/bin/env python3
"""Validate the public, synthetic Lakehouse Sound Festival 2026 dataset."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "csv" / "transactions"
PDF = ROOT / "documents" / "pdf_ascii"


def rows(name: str) -> list[dict[str, str]]:
    with (CSV / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def check(label: str, actual: object, expected: object, failures: list[str]) -> None:
    state = "OK" if actual == expected else "FAIL"
    print(f"{state:4} {label}: {actual!r} (expected {expected!r})")
    if state == "FAIL":
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    ticket_sales = rows("ticket_sales.csv")
    admission = rows("admission_logs.csv")
    sensors = rows("equipment_sensor_logs.csv")
    maintenance = rows("equipment_maintenance.csv")
    schedule = {r["performance_id"]: r for r in rows("performance_schedule.csv")}
    actual = rows("performance_actual.csv")
    inventory = rows("inventory_snapshots.csv")
    plans = rows("merch_inventory_plan.csv")
    refunds = rows("refund_requests.csv")
    feedback_path = ROOT / "data" / "jsonl" / "attendee_feedback.jsonl"
    feedback = [json.loads(line) for line in feedback_path.read_text(encoding="utf-8").splitlines()]

    check("ticket_sales", len(ticket_sales), 20800, failures)
    check("admission_logs", len(admission), 37625, failures)
    check("equipment_sensor_logs", len(sensors), 36975, failures)
    check("merchandise_sales", len(rows("merchandise_sales.csv")), 12320, failures)
    check("refund_requests", len(refunds), 1500, failures)
    check("RAG PDFs", len(list(PDF.glob("*.pdf"))), 10, failures)

    delayed = [r for r in actual if r["incident_id"] == "INC-2026-081"]
    check("Waveform affected performances", len(delayed), 3, failures)
    check("Waveform performance IDs", [r["performance_id"] for r in delayed], ["PERF-0033", "PERF-0034", "PERF-0035"], failures)
    check("Waveform artists", [schedule[r["performance_id"]]["artist_name"] for r in delayed], ["Circuit Bloom", "Fader Ghost", "Spectrum Taxi"], failures)
    check("Waveform max delay", max(int(r["delay_minutes"]) for r in delayed), 29, failures)

    wa_sensors = [r for r in sensors if r["equipment_id"] == "EQ-NET-WA-01"]
    metric = lambda name, fn: fn(float(r["metric_value"]) for r in wa_sensors if r["metric_name"] == name)
    check("Waveform max temperature", metric("temperature_c", max), 91.755, failures)
    check("Waveform max packet loss", metric("packet_loss_pct", max), 19.167, failures)
    check("Waveform min fan RPM", metric("fan_rpm", min), 120.0, failures)
    wa_maintenance = next(r for r in maintenance if r["equipment_id"] == "EQ-NET-WA-01")
    check("Waveform maintenance scheduled date", wa_maintenance["scheduled_date"], "2026-07-25", failures)
    check("Waveform maintenance overdue days", (date(2026, 8, 8) - date.fromisoformat(wa_maintenance["scheduled_date"])).days, 14, failures)

    gate_window = [r for r in admission if r["gate_id"] == "GATE-C" and "2026-08-08 10:18:00" <= r["event_ts"] <= "2026-08-08 10:51:00"]
    failed = [r for r in gate_window if r["result_code"] != "SUCCESS"]
    check("Gate C failure rate", round(100 * len(failed) / len(gate_window), 1), 61.4, failures)
    check("Gate C average wait", round(sum(float(r["queue_estimate_minutes"]) for r in gate_window) / len(gate_window), 1), 29.6, failures)

    plan = next(r for r in plans if r["product_id"] == "MER-LUN-HOOD-BLK-M" and r["festival_date"] == "2026-08-08")
    lunar_sales = [r for r in rows("merchandise_sales.csv") if r["product_id"] == "MER-LUN-HOOD-BLK-M"]
    check("Lunar planned stock", int(plan["planned_stock_units"]), 420, failures)
    check("Lunar interest forecast", int(plan["interest_adjusted_forecast_units"]), 690, failures)
    check("Lunar stockout", max(r["sale_ts"] for r in lunar_sales), "2026-08-08 17:40:00", failures)
    negative = [r for r in feedback if r.get("topic") == "MERCH_STOCKOUT" and r.get("sentiment") == "NEGATIVE"]
    check("Lunar negative feedback", len(negative), 250, failures)

    decisions = ROOT / "validation" / "expected_refund_decisions.csv"
    with decisions.open(encoding="utf-8-sig", newline="") as stream:
        refund_decisions = list(csv.DictReader(stream))
    approved = [r for r in refund_decisions if r["expected_decision"] == "APPROVED"]
    check("Auto approved refunds", len(approved), 1300, failures)
    check("Auto approved refund total", sum(int(r["expected_refund_amount_jpy"]) for r in approved), 5126000, failures)

    if failures:
        print(f"\nValidation failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
