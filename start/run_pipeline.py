from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEFAULT_PHASE_2_WEIGHTS = ROOT_DIR / "phase_2_disease_detection" / "models" / "phase_2_tomato_unet.pt"

from phase_1_image_acquisition.phase import run_phase as run_phase_1
from phase_2_disease_detection.phase import run_phase as run_phase_2
from phase_3_leaf_damage_detection.phase import run_phase as run_phase_3
from phase_4_aggregation.phase import run_phase as run_phase_4
from phase_5_spray_calculation.phase import run_phase as run_phase_5
from phase_6_spray_model_selection.phase import run_phase as run_phase_6
from phase_7_execute_spray_and_move.phase import run_phase as run_phase_7


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tomato plant belt spray pipeline")
    parser.add_argument("--plant-id", default="plant_001", help="Plant identifier for the current stop on the belt.")
    parser.add_argument("--plant-index", type=int, default=1, help="Plant position index in the 3-plant demo row.")
    parser.add_argument("--total-plants", type=int, default=3, help="Total plants in the current demo row.")
    parser.add_argument("--image-count", type=int, default=8, help="How many raw images to capture at each plant.")
    parser.add_argument("--selected-leaves", type=int, default=6, help="How many best leaf images to keep.")
    parser.add_argument("--capture-delay", type=float, default=1.5, help="Camera warm-up delay before capture.")
    parser.add_argument("--belt-move-time", type=float, default=0.8, help="Fallback time to move belt into position.")
    parser.add_argument("--start-to-plant1-time", type=float, default=0.8, help="Time from start position to plant 1.")
    parser.add_argument("--start-to-plant2-time", type=float, default=1.8, help="Time from start position to plant 2.")
    parser.add_argument("--start-to-plant3-time", type=float, default=2.8, help="Time from start position to plant 3.")
    parser.add_argument("--plant1-to-plant2-time", type=float, default=1.0, help="Time from plant 1 to plant 2.")
    parser.add_argument("--plant2-to-plant3-time", type=float, default=1.0, help="Time from plant 2 to plant 3.")
    parser.add_argument("--plant3-to-end-time", type=float, default=0.8, help="Time from plant 3 to end/stop.")
    parser.add_argument("--spray-pulse", type=float, default=0.7, help="Pump activation time in seconds.")
    parser.add_argument("--move-next-time", type=float, default=1.0, help="Fallback time to move to the next plant.")
    parser.add_argument("--base-spray-ml", type=float, default=5.0, help="Base spray amount.")
    parser.add_argument("--p-ref", type=float, default=4.0, help="Reference spray amount P_ref.")
    parser.add_argument("--i-ref", type=float, default=0.40, help="Reference infection average I_ref.")
    parser.add_argument("--d-current", type=float, default=2.5, help="Current dosage or density factor D_current.")
    parser.add_argument("--d-ref", type=float, default=2.5, help="Reference dosage or density factor D_ref.")
    parser.add_argument("--belt-in1-pin", type=int, default=17, help="GPIO pin for L298N IN1.")
    parser.add_argument("--belt-in2-pin", type=int, default=27, help="GPIO pin for L298N IN2.")
    parser.add_argument("--belt-ena-pin", type=int, default=22, help="GPIO pin for L298N ENA.")
    parser.add_argument("--belt-speed", type=float, default=0.10, help="Demo belt speed as 0.0 to 1.0.")
    parser.add_argument("--spray-pin", type=int, default=23, help="GPIO pin controlling spray relay.")
    parser.add_argument("--relay-active-high", action="store_true", help="Use active-high relay behavior instead of the default active-low behavior.")
    parser.add_argument("--yolo-weights", type=Path, help="Optional YOLO weights path for leaf detection.")
    parser.add_argument("--input-image-dir", type=Path, help="Optional folder of existing images for testing phase 1.")
    parser.add_argument("--captures-dir", type=Path, default=ROOT_DIR / "captures", help="Folder for raw captures.")
    parser.add_argument("--selected-dir", type=Path, default=ROOT_DIR / "selected_leaves", help="Folder for selected leaf images.")
    parser.add_argument("--phase-2-image-size", type=int, nargs=2, default=(256, 256), help="Phase 2 image size.")
    parser.add_argument(
        "--phase-2-weights",
        type=Path,
        default=DEFAULT_PHASE_2_WEIGHTS,
        help="Trained phase 2 weights file.",
    )
    parser.add_argument("--save-json", type=Path, help="Optional pipeline output JSON file.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate hardware operations.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = vars(args).copy()

    for runner in (
        run_phase_1,
        run_phase_2,
        run_phase_3,
        run_phase_4,
        run_phase_5,
        run_phase_6,
        run_phase_7,
    ):
        context = runner(context)

    print("\nPipeline complete")
    print(json.dumps(context, indent=2, default=str))

    if args.save_json:
        args.save_json.parent.mkdir(parents=True, exist_ok=True)
        args.save_json.write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")
        print(f"\nSaved pipeline result to {args.save_json}")


if __name__ == "__main__":
    main()
