# Phase 6: Model Selection

## Goal

Choose the spray action based on the calculated `P_plant` value from phase 5.

## Implemented rules

- `P_plant <= 10`: standard spray
- `10 < P_plant <= 75`: scaled spray
- `75 < P_plant`: spray color with `5 ml` for identification and removal, no pesticide spray

## Important rule

For plants at or below the standard threshold, keep the spray mode as `standard_spray`.

The applied output now stays equal to the phase-5 calculated spray amount instead of being forced to `10`.

So:

- `standard_spray` means the standard action category
- `applied_output` still reflects the calculated amount from phase 5

## Output

- spray mode
- applied output
- final action:
  - pesticide spray
  - color marking for removal
