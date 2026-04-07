# Start

This folder contains the project entrypoints.

## Files

- `run_pipeline.py`: runs the real scaffold pipeline on the demo setup
- `test_pipeline.py`: demonstrates each phase with sample inputs, outputs, and explanations
- `../run_all_phases.sh`: Raspberry Pi one-command launcher
- `../run_three_plants.sh`: Raspberry Pi one-command launcher for plant 1, 2, and 3 in sequence
- `../install_pi.sh`: Raspberry Pi setup helper

## Demo-oriented defaults

The runner is already aligned to the current demo hardware plan:

- `GPIO 17` for L298N IN1
- `GPIO 27` for L298N IN2
- `GPIO 22` for L298N ENA
- `GPIO 23` for pump relay
- default relay behavior = `active-low`
- 3-plant movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- default movement timings:
  - `5.0 s` start to plant 1
  - `5.0 s` start to plant 2
  - `5.0 s` start to plant 3
  - `5.0 s` plant 1 to plant 2
  - `5.0 s` plant 2 to plant 3
  - `5.0 s` plant 3 to stop
- default belt speed = `0.10`
- default spray pulse = `0.7 s`
- base spray-time calibration = `1.0 ml`
- camera distance target = `2 to 6 inches`
- color-marking case is reported in output only and does not trigger physical spray
- handbook defaults for phase 5:
  - `P_ref = 4.0`
  - `I_ref = 0.40`
  - `D_current = 2.5`
  - `D_ref = 2.5`

## Current use

- use `run_pipeline.py` for the actual scaffolded pipeline
- use `test_pipeline.py` to inspect the expected input and output of every phase before datasets are added
- on Raspberry Pi, `run_all_phases.sh` is the easiest launcher
- for no-camera 3-plant testing, the repo now includes fixed sample plant images in:
  - `captures/test_inputs/plant_001_BLK_3_1002_PL009_NH.JPG`
  - `captures/test_inputs/plant_002_BLK_3_1002_PL039_H.JPG`
  - `captures/test_inputs/plant_003_BLK_3_1002_PL031_H.JPG`
  - `captures/test_inputs/leaf_boxes_manifest.json`

When `--input-image-dir captures/test_inputs` is used with `--plant-id plant_001`, `plant_002`, or `plant_003`:

- phase 1 picks the matching plant image only
- fixed leaf boxes from `leaf_boxes_manifest.json` are cropped as the selected leaf images
- an annotated source image with the selected boxes is written into `selected_leaves/`

To run all 3 fixed test plants in one command on Raspberry Pi:

- `./run_three_plants.sh`
- optional custom input folder: `./run_three_plants.sh /home/sai/plant/captures/test_inputs`

## Raspberry Pi phase-2 behavior

If PyTorch or the phase-2 weights file are missing on the Raspberry Pi:

- phase 2 does not crash the pipeline anymore
- it falls back to a safe zero-disease output
- the remaining phases continue running
