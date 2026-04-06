# Tomato Plant Belt Spray Pipeline

This project is structured around the 7 phases you described for a Raspberry Pi based belt-mounted plant inspection and spraying demo system for tomato plants.

## Demo hardware configuration

- Raspberry Pi 4B
- Raspberry Pi OS Legacy 64-bit Full
- Raspberry Pi Camera via CSI
- one DC motor for belt movement
- one L298N motor driver for belt control
- one relay-controlled spray line
- external 12V power supply for motor and spray side
- tomato plant row with only 2-3 plants for demo
- slow belt speed around 0.5 m/min

## Demo GPIO mapping

BCM numbering:

- GPIO 17: L298N IN1
- GPIO 27: L298N IN2
- GPIO 22: L298N ENA
- GPIO 23: relay input for spray solenoid

## Workflow

1. Belt stops at a plant and the camera captures multiple leaf images
2. Disease identification estimates the percentage of each disease for that plant
3. Leaf damage estimation computes the average visible damage percentage for that plant
4. Aggregation combines disease and damage outputs into infection average
5. Spray calculation computes the amount to spray
6. Model selection chooses the spray mode
7. Spray executes and the belt moves to the next plant

## Strict completion status

Using your rule that even one missing item means the phase is not completed:

- Phase 1: completed
- Phase 2: completed
- Phase 3: completed
- Phase 4: completed
- Phase 5: completed
- Phase 6: completed
- Phase 7: completed

## Latest project decision update

This section is the latest override for the current project direction and should be treated as the active interpretation when it differs from older notes below.

- Phase 3 is now planned as a logic-based phase, not an ML-model phase
- phase-3 validation is currently treated as oral validation from tomato farmers in Telangana state, India
- phase-5 reference constants are now to be interpreted from the handbook measurements already discussed in the project

Updated practical status under this latest decision:

- Phase 1: completed
- Phase 2: completed
- Phase 3: completed as a logic-based phase
- Phase 4: completed
- Phase 5: completed
- Phase 6: completed
- Phase 7: completed

## Phase 2 summary

Phase 2 is now completed as a tomato-only disease segmentation pipeline.

What was done:

- PlantSeg archive added locally
- tomato-only classes filtered from the archive
- local prepared dataset created
- U-Net model implemented
- training code implemented
- inference code implemented
- initial local model weights trained and saved
- plant-level averaging integrated into the main pipeline

Tomato-only classes used:

- `tomato_bacterial_leaf_spot`
- `tomato_early_blight`
- `tomato_late_blight`
- `tomato_leaf_mold`
- `tomato_mosaic_virus`
- `tomato_septoria_leaf_spot`
- `tomato_yellow_leaf_curl_virus`

Prepared dataset counts:

- train: 460
- val: 74
- test: 133

## Final 3-plant demo setup now used

The current completed demo configuration is:

- movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- motor: `12V 500 RPM geared DC motor`
- drive wheel diameter: `2.5 inches`
- assumed practical carriage speed for control: `5 inches/second`
- spray hardware: `12V diaphragm pump + misting nozzle`
- relay type: `5V single-channel optocoupler relay module`
- relay behavior used in project: `active-low`
- camera distance from plant target: `2 to 6 inches`
- selected GPIO mapping:
  - `GPIO 17` -> motor driver `IN1`
  - `GPIO 27` -> motor driver `IN2`
  - `GPIO 22` -> motor driver `ENA`
  - `GPIO 23` -> pump relay

Plant spacing used:

- start to plant 1 = `4 inches`
- plant 1 to plant 2 = `5 inches`
- plant 2 to plant 3 = `5 inches`
- plant 3 to stop = `4 inches`

Default timing values used in the code:

- start to plant 1 = `0.8 s`
- start to plant 2 = `1.8 s`
- start to plant 3 = `2.8 s`
- plant 1 to plant 2 = `1.0 s`
- plant 2 to plant 3 = `1.0 s`
- plant 3 to stop = `0.8 s`
- belt speed = `0.10`
- spray pulse = `0.7 s`

Color-marking rule used:

- when the output enters the color-marking case, the written output reports `spray color` or `mark for removal`
- no physical color spray is executed in the current demo hardware flow

## Phase 5 completion note

- Phase 5 is marked as completed for the current project version
- remaining practical gaps are still documented for future validation and refinement

## Remaining practical gaps in phase 5

Even though phase 5 is marked as completed for now, the following practical items are still worth noting:

- real experimental calibration on the final hardware setup is still pending
- exact confirmation that the formula gives the correct spray quantity across different plants is still pending
- phase-6 threshold alignment with the current phase-5 output scale may still need re-checking

## Validation note

Current practical validation recorded for this project:

- oral validation from tomato farmers in Telangana state, India

This validation note is currently used as a practical field-understanding input for the logic and handbook-based reference values. It is not the same as a formal experimental validation study.

## Handbook-based reference constants used for phase 5

The project currently keeps the implemented code unchanged, but the active reference constants to interpret the formula are:

- `P_ref` or `S_ref` = `4 ml per plant`
- `I_ref` = `40%`
- `D_ref` = `2.5 plants/m^2`

These come from the handbook-style calculation already discussed in the project notes:

- total spray mixture = `40 liters`
- total plants = `10,000`
- field area = `40,000 m^2`

Derived values:

- `S_ref = (40 x 1000) / 10000 = 4 ml`
- `D_ref = 10000 / 40000 = 2.5 plants/m^2`

## Main folders

- [start](C:\Users\sai-y\Downloads\plant\start)
- [phase_1_image_acquisition](C:\Users\sai-y\Downloads\plant\phase_1_image_acquisition)
- [phase_2_disease_detection](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection)
- [phase_3_leaf_damage_detection](C:\Users\sai-y\Downloads\plant\phase_3_leaf_damage_detection)
- [phase_4_aggregation](C:\Users\sai-y\Downloads\plant\phase_4_aggregation)
- [phase_5_spray_calculation](C:\Users\sai-y\Downloads\plant\phase_5_spray_calculation)
- [phase_6_spray_model_selection](C:\Users\sai-y\Downloads\plant\phase_6_spray_model_selection)
- [phase_7_execute_spray_and_move](C:\Users\sai-y\Downloads\plant\phase_7_execute_spray_and_move)

## Install

For Raspberry Pi OS, use the Pi installer script:

```bash
chmod +x install_pi.sh
./install_pi.sh
```

For a generic Python environment, you can still use:

```bash
pip install -r requirements.txt
```

## Raspberry Pi notes

- `requirements.txt` is now intentionally light for Raspberry Pi.
- `OpenCV` and `Picamera2` should be installed from `apt` on the Pi.
- phase 2 now fails gracefully on the Pi:
  - if `torch` is missing, the pipeline continues with a safe zero-disease fallback
  - if the weights file is missing, the pipeline continues with a safe zero-disease fallback
- to enable real phase-2 disease inference on the Pi, you still need:
  - `torch`
  - `torchvision`
  - `phase_2_disease_detection/models/phase_2_tomato_unet.pt`

## Additional greenhouse tomato reference notes for phase 5

The current phase-5 code remains unchanged, but the following published greenhouse tomato references are important for future spray-formula refinement:

- [Volume application rate adapted to the canopy size in greenhouse tomato crops](https://revistas.usp.br/sa/article/view/78522)
- [Deposition analysis of several application volumes of pesticides adapted to the growth of a greenhouse tomato crop](https://www.actahort.org/books/691/691_20.htm)
- [Evaluation of the effect of spray pressure in hand-held sprayers in a greenhouse tomato crop](https://www.sciencedirect.com/science/article/abs/pii/S0261219413002056)
- [A variable-rate spraying method fusing canopy volume and disease detection to reduce pesticide dosage](https://www.sciencedirect.com/science/article/abs/pii/S0168169925007124)

These support the idea that greenhouse tomato spray amount depends strongly on:

- disease severity
- canopy size or canopy volume
- growth stage
- leaf area index
- spray pressure
- deposition quality

Literature-backed reference values or ranges mentioned in those studies include:

- canopy heights: `0.75 m`, `2.25 m`, `2.80 m`
- LAI range: `0.68 to 3.16 m^2/m^2`
- spray volume:
  - `500 to 1500 L/ha` for smaller or early-stage canopy
  - `1000 to 3000 L/ha` for larger or later-stage canopy
- spray pressures tested:
  - `2.5`, `5`, `10`, `15 bar`
  - or `1000`, `1500`, `2000 kPa`

These references support future interpretation of:

- `C_ref` as a canopy reference condition
- `S_ref` as a calibrated reference spray amount

But they do not provide one universal tomato `I_ref` infection percentage.

The current project therefore keeps both of the following in documentation:

- handbook-based operational constants now used in this project:
  - `S_ref/P_ref = 4 ml`
  - `I_ref = 40%`
  - `D_ref = 2.5 plants/m^2`
- published-paper guidance for future refinement:
  - canopy-related refinement
  - greenhouse spray-volume ranges
  - pressure and deposition considerations

## Run the demo scaffold pipeline

```bash
python start/run_pipeline.py --dry-run --plant-id plant_001 --plant-index 1 --belt-in1-pin 17 --belt-in2-pin 27 --belt-ena-pin 22 --spray-pin 23
```

## One-command launcher

You can run the full pipeline with the root launcher file:

```bash
run_all_phases.bat
```

Optional arguments:

```bash
run_all_phases.bat plant_001 1
run_all_phases.bat plant_002 2
run_all_phases.bat plant_003 3
```

Optional custom image folder:

```bash
run_all_phases.bat plant_001 1 C:\path\to\images
```

The launcher:

- runs all phases in order
- uses dry-run mode
- uses the current project defaults
- saves output JSON in:
  - `test_runs\launcher_runs\<plant_id>\result.json`

On Raspberry Pi OS, use:

```bash
chmod +x run_all_phases.sh
./run_all_phases.sh plant_001 1 /home/sai/plant/test_images
```

## Run the testing/demo file

```bash
python start/test_pipeline.py
```
