# Phase 6: Model Selection

## Goal

Choose the spray action based on the calculated `P_plant` value from phase 5.

## Implemented rules

- `P_plant <= 10`: standard spray
- `10 < P_plant <= 75`: scaled spray
- `75 < P_plant`: spray color with `5 ml` for identification and removal, no pesticide spray

## Important rule

For plants at or below 10 percent infection, treat them as the minimum standard spray level.

That means the practical spray output is fixed to `10` in this range even if the formula gives a lower value.

## Output

- spray mode
- applied output
- final action:
  - pesticide spray
  - color marking for removal
