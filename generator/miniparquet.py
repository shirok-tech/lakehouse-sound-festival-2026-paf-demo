"""A tiny, dependency-light Parquet writer/reader for flat required columns.

This module writes Parquet 1.0 files with one row group, one uncompressed
PLAIN-encoded data page per column. It supports UTF-8 strings, int32, int64,
and double. It is intended for deterministic demo data generation.
"""
from __future__ import annotations

import io
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from thrift.Thrift import TType
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport

PARQUET_MAGIC = b"PAR1"

# parquet-format enum values
TYPE_BOOLEAN = 0
TYPE_INT32 = 1
TYPE_INT64 = 2
TYPE_INT96 = 3
TYPE_FLOAT = 4
TYPE_DOUBLE = 5
TYPE_BYTE_ARRAY = 6
TYPE_FIXED_LEN_BYTE_ARRAY = 7

REQUIRED = 0
OPTIONAL = 1
REPEATED = 2

ENCODING_PLAIN = 0
ENCODING_RLE = 3
CODEC_UNCOMPRESSED = 0
PAGE_DATA = 0
CONVERTED_UTF8 = 0

SUPPORTED_TYPES = {"string", "int32", "int64", "double"}


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type_name: str

    @property
    def parquet_type(self) -> int:
        return {
            "string": TYPE_BYTE_ARRAY,
            "int32": TYPE_INT32,
            "int64": TYPE_INT64,
            "double": TYPE_DOUBLE,
        }[self.type_name]


def _serialize(write_fn) -> bytes:
    transport = TTransport.TMemoryBuffer()
    protocol = TCompactProtocol.TCompactProtocol(transport)
    write_fn(protocol)
    return transport.getvalue()


def _write_schema_element(protocol, spec: ColumnSpec | None, num_children: int | None = None) -> None:
    protocol.writeStructBegin("SchemaElement")
    if spec is not None:
        protocol.writeFieldBegin("type", TType.I32, 1)
        protocol.writeI32(spec.parquet_type)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("repetition_type", TType.I32, 3)
        protocol.writeI32(REQUIRED)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("name", TType.STRING, 4)
        protocol.writeString(spec.name)
        protocol.writeFieldEnd()
        if spec.type_name == "string":
            protocol.writeFieldBegin("converted_type", TType.I32, 6)
            protocol.writeI32(CONVERTED_UTF8)
            protocol.writeFieldEnd()
    else:
        protocol.writeFieldBegin("name", TType.STRING, 4)
        protocol.writeString("schema")
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("num_children", TType.I32, 5)
        protocol.writeI32(int(num_children or 0))
        protocol.writeFieldEnd()
    protocol.writeFieldStop()
    protocol.writeStructEnd()


def _write_data_page_header(protocol, num_values: int) -> None:
    protocol.writeStructBegin("DataPageHeader")
    protocol.writeFieldBegin("num_values", TType.I32, 1)
    protocol.writeI32(num_values)
    protocol.writeFieldEnd()
    protocol.writeFieldBegin("encoding", TType.I32, 2)
    protocol.writeI32(ENCODING_PLAIN)
    protocol.writeFieldEnd()
    protocol.writeFieldBegin("definition_level_encoding", TType.I32, 3)
    protocol.writeI32(ENCODING_RLE)
    protocol.writeFieldEnd()
    protocol.writeFieldBegin("repetition_level_encoding", TType.I32, 4)
    protocol.writeI32(ENCODING_RLE)
    protocol.writeFieldEnd()
    protocol.writeFieldStop()
    protocol.writeStructEnd()


def _page_header_bytes(num_values: int, payload_size: int) -> bytes:
    def _write(protocol) -> None:
        protocol.writeStructBegin("PageHeader")
        protocol.writeFieldBegin("type", TType.I32, 1)
        protocol.writeI32(PAGE_DATA)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("uncompressed_page_size", TType.I32, 2)
        protocol.writeI32(payload_size)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("compressed_page_size", TType.I32, 3)
        protocol.writeI32(payload_size)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("data_page_header", TType.STRUCT, 5)
        _write_data_page_header(protocol, num_values)
        protocol.writeFieldEnd()
        protocol.writeFieldStop()
        protocol.writeStructEnd()

    return _serialize(_write)


def _encode_values(spec: ColumnSpec, values: Sequence[Any]) -> bytes:
    out = io.BytesIO()
    if spec.type_name == "string":
        for value in values:
            if value is None:
                value = ""
            data = str(value).encode("utf-8")
            out.write(struct.pack("<I", len(data)))
            out.write(data)
    elif spec.type_name == "int32":
        for value in values:
            out.write(struct.pack("<i", int(value)))
    elif spec.type_name == "int64":
        for value in values:
            out.write(struct.pack("<q", int(value)))
    elif spec.type_name == "double":
        for value in values:
            out.write(struct.pack("<d", float(value)))
    else:
        raise ValueError(f"Unsupported Parquet type: {spec.type_name}")
    return out.getvalue()


def _write_column_metadata(protocol, column: Mapping[str, Any]) -> None:
    protocol.writeStructBegin("ColumnMetaData")
    protocol.writeFieldBegin("type", TType.I32, 1)
    protocol.writeI32(column["parquet_type"])
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("encodings", TType.LIST, 2)
    protocol.writeListBegin(TType.I32, 2)
    protocol.writeI32(ENCODING_PLAIN)
    protocol.writeI32(ENCODING_RLE)
    protocol.writeListEnd()
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("path_in_schema", TType.LIST, 3)
    protocol.writeListBegin(TType.STRING, 1)
    protocol.writeString(column["name"])
    protocol.writeListEnd()
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("codec", TType.I32, 4)
    protocol.writeI32(CODEC_UNCOMPRESSED)
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("num_values", TType.I64, 5)
    protocol.writeI64(column["num_values"])
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("total_uncompressed_size", TType.I64, 6)
    protocol.writeI64(column["total_size"])
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("total_compressed_size", TType.I64, 7)
    protocol.writeI64(column["total_size"])
    protocol.writeFieldEnd()

    protocol.writeFieldBegin("data_page_offset", TType.I64, 9)
    protocol.writeI64(column["offset"])
    protocol.writeFieldEnd()

    protocol.writeFieldStop()
    protocol.writeStructEnd()


def _write_column_chunk(protocol, column: Mapping[str, Any]) -> None:
    protocol.writeStructBegin("ColumnChunk")
    protocol.writeFieldBegin("file_offset", TType.I64, 2)
    protocol.writeI64(column["offset"])
    protocol.writeFieldEnd()
    protocol.writeFieldBegin("meta_data", TType.STRUCT, 3)
    _write_column_metadata(protocol, column)
    protocol.writeFieldEnd()
    protocol.writeFieldStop()
    protocol.writeStructEnd()


def _footer_bytes(specs: Sequence[ColumnSpec], columns: Sequence[Mapping[str, Any]], num_rows: int) -> bytes:
    def _write(protocol) -> None:
        protocol.writeStructBegin("FileMetaData")
        protocol.writeFieldBegin("version", TType.I32, 1)
        protocol.writeI32(1)
        protocol.writeFieldEnd()

        protocol.writeFieldBegin("schema", TType.LIST, 2)
        protocol.writeListBegin(TType.STRUCT, len(specs) + 1)
        _write_schema_element(protocol, None, len(specs))
        for spec in specs:
            _write_schema_element(protocol, spec)
        protocol.writeListEnd()
        protocol.writeFieldEnd()

        protocol.writeFieldBegin("num_rows", TType.I64, 3)
        protocol.writeI64(num_rows)
        protocol.writeFieldEnd()

        protocol.writeFieldBegin("row_groups", TType.LIST, 4)
        protocol.writeListBegin(TType.STRUCT, 1)
        protocol.writeStructBegin("RowGroup")
        protocol.writeFieldBegin("columns", TType.LIST, 1)
        protocol.writeListBegin(TType.STRUCT, len(columns))
        for column in columns:
            _write_column_chunk(protocol, column)
        protocol.writeListEnd()
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("total_byte_size", TType.I64, 2)
        protocol.writeI64(sum(int(c["total_size"]) for c in columns))
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("num_rows", TType.I64, 3)
        protocol.writeI64(num_rows)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("file_offset", TType.I64, 5)
        protocol.writeI64(columns[0]["offset"] if columns else 4)
        protocol.writeFieldEnd()
        protocol.writeFieldBegin("total_compressed_size", TType.I64, 6)
        protocol.writeI64(sum(int(c["total_size"]) for c in columns))
        protocol.writeFieldEnd()
        protocol.writeFieldStop()
        protocol.writeStructEnd()
        protocol.writeListEnd()
        protocol.writeFieldEnd()

        protocol.writeFieldBegin("created_by", TType.STRING, 6)
        protocol.writeString("NeoTone MiniParquet Writer 1.0")
        protocol.writeFieldEnd()
        protocol.writeFieldStop()
        protocol.writeStructEnd()

    return _serialize(_write)


def infer_schema(rows: Sequence[Mapping[str, Any]], columns: Sequence[str] | None = None) -> list[ColumnSpec]:
    if not rows:
        raise ValueError("At least one row is required")
    names = list(columns or rows[0].keys())
    specs: list[ColumnSpec] = []
    for name in names:
        values = [row.get(name) for row in rows]
        non_null = next((v for v in values if v is not None), "")
        if isinstance(non_null, bool):
            type_name = "int32"
        elif isinstance(non_null, int):
            type_name = "int64"
        elif isinstance(non_null, float):
            type_name = "double"
        else:
            type_name = "string"
        specs.append(ColumnSpec(name=name, type_name=type_name))
    return specs


def write_parquet(path: str | Path, rows: Sequence[Mapping[str, Any]], schema: Sequence[ColumnSpec] | None = None) -> None:
    if not rows:
        raise ValueError("Cannot write an empty Parquet file")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    specs = list(schema or infer_schema(rows))
    for spec in specs:
        if spec.type_name not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported schema type: {spec.type_name}")

    columns_meta: list[dict[str, Any]] = []
    chunks: list[bytes] = []
    offset = len(PARQUET_MAGIC)
    for spec in specs:
        values = [row.get(spec.name) for row in rows]
        payload = _encode_values(spec, values)
        page_header = _page_header_bytes(len(values), len(payload))
        chunk = page_header + payload
        columns_meta.append(
            {
                "name": spec.name,
                "parquet_type": spec.parquet_type,
                "num_values": len(values),
                "offset": offset,
                "total_size": len(chunk),
                "payload_size": len(payload),
                "page_header_size": len(page_header),
                "type_name": spec.type_name,
            }
        )
        chunks.append(chunk)
        offset += len(chunk)

    footer = _footer_bytes(specs, columns_meta, len(rows))
    with path.open("wb") as f:
        f.write(PARQUET_MAGIC)
        for chunk in chunks:
            f.write(chunk)
        f.write(footer)
        f.write(struct.pack("<I", len(footer)))
        f.write(PARQUET_MAGIC)

    # Write a small sidecar schema for transparent, deterministic validation.
    sidecar = path.with_suffix(path.suffix + ".schema.json")
    sidecar.write_text(
        json.dumps(
            {
                "format": "parquet",
                "rows": len(rows),
                "columns": [spec.__dict__ for spec in specs],
                "writer": "NeoTone MiniParquet Writer 1.0",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def validate_parquet(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != PARQUET_MAGIC or data[-4:] != PARQUET_MAGIC:
        raise ValueError(f"Invalid Parquet magic: {path}")
    footer_len = struct.unpack("<I", data[-8:-4])[0]
    footer_start = len(data) - 8 - footer_len
    if footer_start <= 4:
        raise ValueError(f"Invalid Parquet footer length: {path}")
    sidecar = path.with_suffix(path.suffix + ".schema.json")
    info = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}
    return {
        "path": str(path),
        "size_bytes": len(data),
        "footer_length": footer_len,
        "footer_start": footer_start,
        "rows": info.get("rows"),
        "columns": info.get("columns"),
        "valid_magic": True,
    }
