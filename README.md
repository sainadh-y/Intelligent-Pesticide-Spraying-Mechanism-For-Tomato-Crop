# Tomato Plant Belt Spray Pipeline

This repository contains a completed 7-phase demo pipeline for automated tomato plant inspection and pesticide spray recommendation using a Raspberry Pi, camera, belt movement, and a relay-controlled pump.

The project supports two practical ways to run:

- Raspberry Pi with GPIO and camera hardware
- A normal computer using the provided test plant images without camera hardware

## Final Demo Scope

- 3 demo plants
- movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- manual leaf extraction from 3 fixed plant images for no-camera testing
- phase 2 disease detection using a tomato-only U-Net model when `torch` and weights are available
- safe fallback when phase 2 dependencies are missing
- logic-based visible damage estimation in phase 3
- spray amount calculation in milliliters
- spray execution time derived from spray amount

## Hardware Configuration

- Raspberry Pi 4B
- Raspberry Pi Camera via CSI
- L298N motor driver
- DC motor for carriage or belt movement
- 5V relay module for pump switching
- pump and misting nozzle
- external power supply for motor and pump side

### GPIO Mapping

- `GPIO 17` -> `L298N IN1`
- `GPIO 27` -> `L298N IN2`
- `GPIO 22` -> `L298N ENA`
- `GPIO 23` -> relay input

### Active Project Defaults

- relay behavior: `active-high`
- movement timing:
  - start to plant 1 = `5.0 s`
  - start to plant 2 = `5.0 s`
  - start to plant 3 = `5.0 s`
- belt speed = `1.0`
- spray pulse calibration = `1.0 s`
- base spray calibration = `1.0 ml`
- phase 5 references:
  - `P_ref = 4.0 ml`
  - `I_ref = 0.40`
  - `D_current = 2.5`
  - `D_ref = 2.5`

With those references, `10%` infection gives `1 ml` when `D_current = D_ref`.

## Repository Structure

- [start](start)
  - pipeline runner and test runner
- [phase_1_image_acquisition](phase_1_image_acquisition)
  - movement to plant, image loading or capture, selected leaf generation
- [phase_2_disease_detection](phase_2_disease_detection)
  - U-Net tomato disease inference
- [phase_3_leaf_damage_detection](phase_3_leaf_damage_detection)
  - logic-based visible leaf damage estimation
- [phase_4_aggregation](phase_4_aggregation)
  - infection averaging
- [phase_5_spray_calculation](phase_5_spray_calculation)
  - spray amount formula
- [phase_6_spray_model_selection](phase_6_spray_model_selection)
  - mode selection
- [phase_7_execute_spray_and_move](phase_7_execute_spray_and_move)
  - spray execution for current plant
- [captures/test_inputs](captures/test_inputs)
  - fixed 3-plant test images and manual leaf-box manifest
- [mock_outputs](mock_outputs)
  - wiring and setup diagrams

## Phase Summary

1. Phase 1 moves to the target plant and prepares leaf images.
2. Phase 2 predicts disease percentages from selected leaves.
3. Phase 3 estimates visible damage percentage from selected leaves.
4. Phase 4 combines disease and damage into one infection average.
5. Phase 5 converts infection average into spray amount in `ml`.
6. Phase 6 maps that amount into a spray action.
7. Phase 7 executes the spray for the current plant.

## Test Inputs

The repository includes fixed no-camera test inputs:

- [plant_001_BLK_3_1002_PL009_NH.JPG](captures/test_inputs/plant_001_BLK_3_1002_PL009_NH.JPG)
- [plant_002_BLK_3_1002_PL039_H.JPG](captures/test_inputs/plant_002_BLK_3_1002_PL039_H.JPG)
- [plant_003_BLK_3_1002_PL031_H.JPG](captures/test_inputs/plant_003_BLK_3_1002_PL031_H.JPG)
- [leaf_boxes_manifest.json](captures/test_inputs/leaf_boxes_manifest.json)

These let you run the full project without using the camera.

## Setup On Raspberry Pi

Install:

```bash
cd ~/plant
chmod +x install_pi.sh run_all_phases.sh run_three_plants.sh
./install_pi.sh
source .venv/bin/activate
```

If you want real phase 2 inference on the Pi, you also need:

- `torch`
- `torchvision`
- `phase_2_disease_detection/models/phase_2_tomato_unet.pt`

If they are missing, the pipeline still runs with a safe phase-2 fallback.

## Run On Raspberry Pi

### Single plant using fixed test images

```bash
cd ~/plant
source .venv/bin/activate
python3 start/run_pipeline.py --plant-id plant_001 --plant-index 1 --input-image-dir /home/sai/plant/captures/test_inputs --save-json /home/sai/plant/output/plant_001_result.json
```

### All 3 plants using fixed test images

```bash
cd ~/plant
source .venv/bin/activate
bash run_three_plants.sh
```

### One-command single plant launcher

```bash
cd ~/plant
source .venv/bin/activate
./run_all_phases.sh plant_001 1 /home/sai/plant/captures/test_inputs
```

### Camera-based run on Raspberry Pi

```bash
cd ~/plant
source .venv/bin/activate
python3 start/run_pipeline.py --plant-id plant_001 --plant-index 1 --save-json /home/sai/plant/output/plant_001_camera_result.json
```

## Run On A Normal Computer

This is the recommended path on a Windows or Linux computer when you are not using Raspberry Pi hardware.

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you are using Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Single plant on a normal computer

Linux or macOS:

```bash
python start/run_pipeline.py --dry-run --plant-id plant_001 --plant-index 1 --input-image-dir captures/test_inputs --save-json output/plant_001_result.json
```

Windows PowerShell:

```powershell
python start/run_pipeline.py --dry-run --plant-id plant_001 --plant-index 1 --input-image-dir captures/test_inputs --save-json output/plant_001_result.json
```

### All 3 plants on a normal computer

Linux or macOS:

```bash
python start/run_pipeline.py --dry-run --plant-id plant_001 --plant-index 1 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_001_result.json
python start/run_pipeline.py --dry-run --plant-id plant_002 --plant-index 2 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_002_result.json
python start/run_pipeline.py --dry-run --plant-id plant_003 --plant-index 3 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_003_result.json
```

Windows PowerShell:

```powershell
python start/run_pipeline.py --dry-run --plant-id plant_001 --plant-index 1 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_001_result.json
python start/run_pipeline.py --dry-run --plant-id plant_002 --plant-index 2 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_002_result.json
python start/run_pipeline.py --dry-run --plant-id plant_003 --plant-index 3 --input-image-dir captures/test_inputs --save-json output/three_plants/plant_003_result.json
```

Or use the Windows launchers:

```powershell
run_all_phases.bat plant_001 1
run_three_plants.bat
```

## Output Locations

Generated runtime outputs are written outside git tracking:

- `output/`
- `selected_leaves/`
- `captures/` for live camera captures

Important saved outputs include:

- selected leaf crops
- selected leaf box overlay images
- final JSON pipeline results

## Notes About Phase 2

Phase 2 has two valid run modes:

- full inference mode:
  - requires `torch`, `torchvision`, and model weights
- fallback mode:
  - returns zero disease percentages and keeps the remaining phases running

This makes the project usable on systems where phase 2 dependencies are not available.

## Diagrams

Useful diagrams are kept in [mock_outputs](mock_outputs):

- [architecture_connection_diagram.svg](mock_outputs/architecture_connection_diagram.svg)
- [hardware_3plant_setup.svg](mock_outputs/hardware_3plant_setup.svg)
- [relay_pin_layout_exact.svg](mock_outputs/relay_pin_layout_exact.svg)
- [wiring_connections_3plant_demo.svg](mock_outputs/wiring_connections_3plant_demo.svg)
- [wiring_connections_simple.svg](mock_outputs/wiring_connections_simple.svg)
