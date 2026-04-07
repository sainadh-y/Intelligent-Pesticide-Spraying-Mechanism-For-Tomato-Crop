#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PLANT_ID="${1:-plant_001}"
PLANT_INDEX="${2:-1}"
INPUT_IMAGE_DIR="${3:-$ROOT_DIR/captures/test_inputs}"
OUTPUT_DIR="$ROOT_DIR/output/launcher_runs/$PLANT_ID"

mkdir -p "$OUTPUT_DIR"

python3 "$ROOT_DIR/start/run_pipeline.py" \
  --plant-id "$PLANT_ID" \
  --plant-index "$PLANT_INDEX" \
  --input-image-dir "$INPUT_IMAGE_DIR" \
  --save-json "$OUTPUT_DIR/result.json"
