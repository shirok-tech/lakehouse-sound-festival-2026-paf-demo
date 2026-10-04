#!/usr/bin/env bash
# Upload prepared files. No CSV-to-Parquet conversion or Python package needed.
set -euo pipefail

: "${OCI_NAMESPACE:?Set OCI_NAMESPACE}"
: "${OCI_BUCKET:?Set OCI_BUCKET}"
: "${OCI_REGION:?Set OCI_REGION}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OBJECT_PREFIX="${OCI_OBJECT_PREFIX:-lakehouse_sound_festival_2026}"
OBJECT_PREFIX="${OBJECT_PREFIX%/}"

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--dry-run" ) ]]; then
  echo "Usage: bash scripts/upload_ontology_data.sh [--dry-run]" >&2
  exit 2
fi

FILES=(
  "data/csv/transactions/incidents.csv"
  "data/parquet/incidents/incidents.parquet"
  "metadata/document_catalog.csv"
)
for relative_path in "${FILES[@]}"; do
  test -s "$ROOT_DIR/$relative_path"
done

for relative_path in "${FILES[@]}"; do
  object_name="$OBJECT_PREFIX/$relative_path"
  echo "Upload: $relative_path -> $OCI_BUCKET/$object_name"
  if [[ "${1:-}" != "--dry-run" ]]; then
    oci os object put \
      --namespace-name "$OCI_NAMESPACE" \
      --bucket-name "$OCI_BUCKET" \
      --region "$OCI_REGION" \
      --file "$ROOT_DIR/$relative_path" \
      --name "$object_name" \
      --force
  fi
done

echo "Completed. Check EXT_INCIDENTS and EXT_DOCUMENT_CATALOG before running ontology SQL."
