#!/usr/bin/env bash
set -eu

: "${OCI_NAMESPACE:?Set OCI_NAMESPACE}"
: "${OCI_BUCKET:?Set OCI_BUCKET}"
: "${OCI_REGION:?Set OCI_REGION}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PREFIX="lakehouse_sound_festival_2026"

upload_dir() {
  src_dir="$1"
  object_prefix="$2"
  oci os object bulk-upload \
    --namespace-name "$OCI_NAMESPACE" \
    --bucket-name "$OCI_BUCKET" \
    --src-dir "$src_dir" \
    --object-prefix "$object_prefix/" \
    --region "$OCI_REGION" \
    --overwrite
}

upload_file() {
  src_file="$1"
  object_name="$2"
  oci os object put \
    --namespace-name "$OCI_NAMESPACE" \
    --bucket-name "$OCI_BUCKET" \
    --file "$src_file" \
    --name "$object_name" \
    --region "$OCI_REGION" \
    --force
}

# Agentへ公開する入力データだけをアップロードします。
upload_dir "$ROOT_DIR/data" "$PREFIX/data"
upload_dir "$ROOT_DIR/documents/pdf_ascii" "$PREFIX/documents/pdf_ascii"
upload_file "$ROOT_DIR/metadata/document_catalog.csv" "$PREFIX/metadata/document_catalog.csv"
upload_file "$ROOT_DIR/metadata/business_terms.csv" "$PREFIX/metadata/business_terms.csv"

echo "Upload completed: $PREFIX/"
