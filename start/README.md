# Start

This folder contains the project entrypoints.

## Files

- `run_pipeline.py`: runs the real scaffold pipeline on the demo setup
- `test_pipeline.py`: demonstrates each phase with sample inputs, outputs, and explanations

## Demo-oriented defaults

The runner is already aligned to the current demo hardware plan:

- `GPIO 17` for L298N IN1
- `GPIO 27` for L298N IN2
- `GPIO 22` for L298N ENA
- `GPIO 23` for pump relay
- default relay behavior = `active-low`
- 3-plant movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- default movement timings:
  - `0.8 s` start to plant 1
  - `1.8 s` start to plant 2
  - `2.8 s` start to plant 3
  - `1.0 s` plant 1 to plant 2
  - `1.0 s` plant 2 to plant 3
  - `0.8 s` plant 3 to stop
- default belt speed = `0.10`
- default spray pulse = `0.7 s`
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
