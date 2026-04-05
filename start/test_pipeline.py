from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from phase_1_image_acquisition.phase import explain_phase as explain_phase_1
from phase_2_disease_detection.phase import explain_phase as explain_phase_2
from phase_3_leaf_damage_detection.phase import explain_phase as explain_phase_3
from phase_4_aggregation.phase import explain_phase as explain_phase_4
from phase_5_spray_calculation.phase import explain_phase as explain_phase_5
from phase_6_spray_model_selection.phase import explain_phase as explain_phase_6
from phase_7_execute_spray_and_move.phase import explain_phase as explain_phase_7


def main() -> None:
    print("Tomato Belt Spray Pipeline Test Walkthrough")
    print("==========================================")

    phase_data = [
        explain_phase_1(),
        explain_phase_2(),
        explain_phase_3(),
        explain_phase_4(),
        explain_phase_5(),
        explain_phase_6(),
        explain_phase_7(),
    ]

    for item in phase_data:
        print(f"\nPhase {item['phase']}: {item['title']}")
        print("-" * 40)
        print(item["description"])
        print("\nSample input:")
        print(json.dumps(item["sample_input"], indent=2))
        print("\nSample output:")
        print(json.dumps(item["sample_output"], indent=2))


if __name__ == "__main__":
    main()
