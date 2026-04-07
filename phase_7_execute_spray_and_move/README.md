# Phase 7: Execute Spray And Move

## Goal

Execute the spray for the current plant.

## Completion status

Completed.

## Final demo assumptions used

- 3-plant demo row
- movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- 12V diaphragm pump plus misting nozzle
- 5V single-channel optocoupler relay module
- relay behavior assumed in this project: `active-high`
- camera distance from the plant target: `2 to 6 inches`
- selected GPIO mapping:
  - `GPIO 17` -> `IN1`
  - `GPIO 27` -> `IN2`
  - `GPIO 22` -> `ENA`
  - `GPIO 23` -> pump relay

## Demo hardware target

- Raspberry Pi 4B
- relay-controlled 12V spray solenoid

## Current implementation

- supports dry-run mode
- can activate the pump relay
- records execution summary
- supports pesticide spray or color-marking action based on phase 6
- does not physically execute color spray; that case is recorded in output only as a removal/marking instruction
- explicitly forces the pump relay OFF before phase 7 ends

## Current defaults

- spray pulse = `1.0 s`
- base spray-time calibration = `1.0 ml`

## Current output fields

- next step after the current plant
- execution status
- execution note
- applied spray amount in `ml`
- estimated spray duration in seconds for that amount

## Current spray-time interpretation

For pesticide spray actions, the project now reports:

- `applied_output`: how much spray is intended in `ml`
- `spray_duration_seconds`: how long the pump is activated for that amount

The duration is derived from the current calibration values:

```text
spray_flow_rate_ml_per_sec = base_spray_ml / spray_pulse
spray_duration_seconds = applied_output / spray_flow_rate_ml_per_sec
```
