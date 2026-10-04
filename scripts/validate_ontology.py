#!/usr/bin/env python3
"""Check the shipped Ontology assets without OCI, Oracle, pandas, or PyArrow."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def require(ok: bool, label: str) -> None:
    print(("OK   " if ok else "FAIL ") + label)
    if not ok:
        raise SystemExit(1)


def main() -> None:
    package = json.loads((ROOT / "ONTOLOGY_VALIDATION.json").read_text())
    for relative_path, expected_hash in package["files"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        require(actual_hash == expected_hash, f"ZIP checksum: {relative_path}")

    parquet = (ROOT / "data/parquet/incidents/incidents.parquet").read_bytes()
    footer_length = struct.unpack("<I", parquet[-8:-4])[0]
    require(
        parquet[:4] == b"PAR1" and parquet[-4:] == b"PAR1"
        and 0 < footer_length < len(parquet) - 12,
        "Incident Parquet magic and footer bounds",
    )
    schema = json.loads((ROOT / "data/parquet/incidents/incidents.parquet.schema.json").read_text())
    require(schema["rows"] == 24 and len(schema["columns"]) == 13,
            "Incident Parquet sidecar: 24 rows, 13 columns")
    document_column = next(c for c in schema["columns"] if c["name"] == "document_id")
    require(document_column["nullable"] and document_column["type_name"] == "string",
            "Incident Parquet document_id nullable string")

    incidents = read_csv("data/csv/transactions/incidents.csv")
    catalog = read_csv("metadata/document_catalog.csv")
    mapping = read_csv("metadata/document_pdf_mapping.csv")
    manifest = json.loads((ROOT / "documents/source/document_build_manifest.json").read_text())
    ids = [row["document_id"] for row in catalog]
    require(len(incidents) == 24 and len(catalog) == 10 and len(set(ids)) == 10,
            "Incident and Catalog row counts / unique Document IDs")
    incident_091 = [row for row in incidents if row["incident_id"] == "INC-2026-091"]
    require(len(incident_091) == 1 and incident_091[0]["document_id"] == "",
            "INC-2026-091 unresolved Document reference removed")
    incident_081 = [row for row in incidents if row["incident_id"] == "INC-2026-081"]
    require(len(incident_081) == 1
            and incident_081[0]["related_equipment_id"] == "EQ-NET-WA-01"
            and incident_081[0]["document_id"] == "IR-2026-081",
            "INC-2026-081 source references")
    require(all(not row["document_id"] or row["document_id"] in ids for row in incidents),
            "All nonempty Incident Document IDs resolve")
    require("WX-2026-009" not in ids, "No fabricated WX-2026-009 Document")

    japanese_by_id = {row["document_id"]: row["pdf"] for row in manifest}
    ascii_by_id = {row["document_id"]: row["ascii_pdf_file_name"] for row in mapping}
    require(set(ids) == set(japanese_by_id) == set(ascii_by_id),
            "Catalog, Japanese PDF manifest, ASCII PDF mapping share Document IDs")
    require(all(row["file_name"] == japanese_by_id[row["document_id"]]
                and (ROOT / "documents/pdf" / row["file_name"]).is_file()
                and (ROOT / "documents/pdf_ascii" / ascii_by_id[row["document_id"]]).is_file()
                for row in catalog), "All 10 Japanese and ASCII PDFs resolve by Document ID")
    require(set(ascii_by_id.values())
            == {p.name for p in (ROOT / "documents/pdf_ascii").glob("*.pdf")},
            "ASCII mapping covers exactly the RAG PDF set")

    equipment = read_csv("data/csv/master/equipment_master.csv")
    base_lot = {row["equipment_id"]: row["manufacturing_lot"] for row in equipment}
    require(base_lot["EQ-NET-WA-01"] == "NW-2603"
            and base_lot["EQ-NET-OM-01"] != "NW-2603"
            and base_lot["EQ-NET-NG-01"] != "NW-2603",
            "Synthetic peer Lot is separate from Equipment Master")
    seed = (ROOT / "sql/ontology/03_seed_relations.sql").read_text()
    require(all(value in seed for value in
                ("EQ-NET-OM-01", "EQ-NET-NG-01", "BLOG-DEMO-LOT-001",
                 "ONTOLOGY_DEMO_SEED", "BLOG-DEMO-TASK-001")),
            "Seed SQL retains synthetic provenance")
    graph = (ROOT / "sql/ontology/11_create_property_graph.sql").read_text()
    vertex_part, edge_part = graph.split("EDGE TABLES (", 1)
    vertex_count = len(re.findall(r"^\s+V_KG_\w+ AS \w+\s*$", vertex_part, re.M))
    edge_count = len(re.findall(r"^\s+V_KG_\w+ AS \w+\s*$", edge_part, re.M))
    require((vertex_count, edge_count) == (6, 8), "Graph SQL: 6 Vertex and 8 Edge definitions")
    sql_files = list((ROOT / "sql/ontology").glob("*.sql"))
    require(len(sql_files) >= 25 and all(
        "SQL実行結果" not in path.read_text()
        and "TASK-121" not in path.read_text()
        and "TASK-122" not in path.read_text()
        for path in sql_files
    ), "Runnable SQL excludes console logs and fixed Task identity values")
    file_manifest = read_csv("metadata/file_manifest.csv")
    require(all(
        (ROOT / row["relative_path"]).is_file()
        and hashlib.sha256((ROOT / row["relative_path"]).read_bytes()).hexdigest()
        == row["sha256"]
        for row in file_manifest
    ), "File manifest checksums resolve")
    print("Local Ontology validation passed (database and PAF execution not performed).")


if __name__ == "__main__":
    main()
