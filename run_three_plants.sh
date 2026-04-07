#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_IMAGE_DIR="${1:-$ROOT_DIR/captures/test_inputs}"
OUTPUT_DIR="${2:-$ROOT_DIR/output/three_plants}"

mkdir -p "$OUTPUT_DIR"

python3 "$ROOT_DIR/start/run_pipeline.py" \
  --plant-id plant_001 \
  --plant-index 1 \
  --input-image-dir "$INPUT_IMAGE_DIR" \
  --save-json "$OUTPUT_DIR/plant_001_result.json"

python3 "$ROOT_DIR/start/run_pipeline.py" \
  --plant-id plant_002 \
  --plant-index 2 \
  --input-image-dir "$INPUT_IMAGE_DIR" \
  --save-json "$OUTPUT_DIR/plant_002_result.json"

python3 "$ROOT_DIR/start/run_pipeline.py" \
  --plant-id plant_003 \
  --plant-index 3 \
  --input-image-dir "$INPUT_IMAGE_DIR" \
  --save-json "$OUTPUT_DIR/plant_003_result.json"

echo
echo "Saved results to: $OUTPUT_DIR"
