#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y \
  python3-pip \
  python3-opencv \
  python3-picamera2

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

cat <<'EOF'

Pi installation complete.

Notes:
- OpenCV is installed from apt for better Raspberry Pi compatibility.
- Picamera2 is installed from apt.
- Phase 2 will still need:
  1. PyTorch installed separately on the Pi if you want real disease inference
  2. phase_2_tomato_unet.pt copied to phase_2_disease_detection/models/
- If PyTorch or weights are missing, the pipeline now falls back safely and keeps running.

EOF
