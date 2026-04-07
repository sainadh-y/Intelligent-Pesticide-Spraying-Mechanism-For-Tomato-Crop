# Phase 7: Execute Spray And Move

## Goal

Execute the spray for the current plant and move the belt to the next plant.

## Completion status

Completed.

## Final demo assumptions used

- 3-plant demo row
- movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- 12V diaphragm pump plus misting nozzle
- 5V single-channel optocoupler relay module
- relay behavior assumed in this project: `active-low`
- L298N-style movement control
- timed movement between plants
- camera distance from the plant target: `2 to 6 inches`
- selected GPIO mapping:
  - `GPIO 17` -> `IN1`
  - `GPIO 27` -> `IN2`
  - `GPIO 22` -> `ENA`
  - `GPIO 23` -> pump relay

## Demo hardware target

- Raspberry Pi 4B
- L298N motor driver for the belt motor
- relay-controlled 12V spray solenoid
- timed movement for demo positioning

## Current implementation

- supports dry-run mode
- can activate the pump relay
- can drive the belt motor through L298N direction/enable control
- moves from plant 1 to plant 2, plant 2 to plant 3, and stops after plant 3
- records execution summary
- supports pesticide spray or color-marking action based on phase 6
- does not physically execute color spray; that case is recorded in output only as a removal/marking instruction
- explicitly forces the pump relay OFF before any belt movement begins

## 3-plant timing defaults

- plant 1 to plant 2 = `5.0 s`
- plant 2 to plant 3 = `5.0 s`
- plant 3 to stop/end = `5.0 s`
- belt speed = `0.10`
- spray pulse = `0.7 s`
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
