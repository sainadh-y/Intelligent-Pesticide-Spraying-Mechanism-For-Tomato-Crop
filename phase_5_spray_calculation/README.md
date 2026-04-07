# Phase 5: Spray Calculation

## Goal

Calculate the plant spray value using the infection average from phase 4 and your provided formula.

## Completion status

Completed.

## Remaining practical gaps

- the formula is implemented in code
- the variables are documented
- the assumptions behind the formula are documented
- oral farmer validation is documented
- real experimental calibration on the final setup is still pending
- exact confirmation that the formula gives the correct spray quantity in practice is still pending
- phase-6 threshold alignment with the current phase-5 output scale may still need re-checking

## Implemented formula

```text
P_plant = P_ref x (I_avg / I_ref) x (D_current / D_ref)
```

## Current implementation

- uses your provided formula directly
- keeps the inputs configurable through pipeline arguments
- outputs `P_plant` as `spray_ml_per_plant` in the current code path

## Inputs

- `I_avg`
- `P_ref`
- `I_ref`
- `D_current`
- `D_ref`

## Output

- calculated `P_plant`

## Assumptions for this formula to work properly

This formula works properly only when the following conditions are kept constant or intentionally neglected:

- tomato crop type is constant
- pesticide type is constant
- pesticide concentration or mixing ratio is constant
- nozzle type is constant
- spray pressure is constant
- belt speed or travel speed is constant
- distance from sprayer to plant is constant
- plant row spacing and setup are approximately constant
- the image acquisition and leaf-selection method from phase 1 is constant
- environmental effects such as wind, temperature, and humidity are neglected or treated as constant
- sprayer hardware flow response is constant

In this setup, the main changing factors are assumed to be:

- `I_avg`
- `D_current / D_ref`

## Practical interpretation

This means the formula is being used as a proportional control rule where:

- `P_ref` is the calibrated base spray quantity
- `I_ref` is the reference infection level
- `D_current / D_ref` is an additional adjustment factor

So the formula is most valid when all other spray-delivery conditions remain unchanged.

## Additional greenhouse tomato reference notes

The current code still uses the project formula already implemented. The points below are added as literature-backed reference guidance only. The code is not changed here.

### Greenhouse tomato factors that published work shows are important

Published greenhouse tomato spraying studies indicate that spray amount and spray effectiveness depend strongly on:

- disease severity or disease-risk level
- canopy size or canopy volume
- plant growth stage
- leaf area index
- spray pressure
- canopy penetration and deposition quality
- nozzle arrangement
- travel/application pattern

### Reference papers

- Greenhouse tomato canopy-size adapted spraying:
  [Volume application rate adapted to the canopy size in greenhouse tomato crops](https://revistas.usp.br/sa/article/view/78522)

- Greenhouse tomato deposition versus crop growth:
  [Deposition analysis of several application volumes of pesticides adapted to the growth of a greenhouse tomato crop](https://www.actahort.org/books/691/691_20.htm)

- Greenhouse tomato pressure and deposition:
  [Evaluation of the effect of spray pressure in hand-held sprayers in a greenhouse tomato crop](https://www.sciencedirect.com/science/article/abs/pii/S0261219413002056)

- Variable-rate spraying using disease plus canopy information:
  [A variable-rate spraying method fusing canopy volume and disease detection to reduce pesticide dosage](https://www.sciencedirect.com/science/article/abs/pii/S0168169925007124)

### Numeric values that can be taken from published greenhouse tomato studies

These are literature-backed reference values or ranges that can guide future formula refinement:

- canopy height tested in greenhouse tomato studies:
  - `0.75 m`
  - `2.25 m`
  - `2.80 m`

- leaf area index range reported:
  - `0.68` to `3.16 m^2/m^2`

- greenhouse tomato spray volume ranges reported:
  - `500 to 1500 L/ha` for early or smaller crop stages
  - `1000 to 3000 L/ha` for later or taller crop stages

- spray pressure values tested in greenhouse tomato studies:
  - `2.5`, `5`, `10`, `15 bar`
  - or `1000`, `1500`, `2000 kPa`

### How these values relate to formula constants

If the formula is later refined using only greenhouse tomato literature, the most defensible interpretation would be:

- `C_ref` = a reference canopy condition
  - for example a mid-stage greenhouse tomato canopy
  - canopy height around `2.25 m`
  - or LAI around `2.0 m^2/m^2`

- `S_ref` = a reference spray amount under that reference canopy condition
  - literature supports using a reference area-based value such as `1000 L/ha` for a mid-stage greenhouse tomato canopy
  - this is stronger from literature than assigning a universal `ml/plant` value directly

- `I_ref` = intervention threshold
  - literature does not give one universal greenhouse tomato infection-percent threshold
  - this still remains a project-defined intervention value unless a disease-specific threshold source is chosen

### Important interpretation note

From the literature, `S_ref` and `C_ref` can be supported more strongly than `I_ref`.

So the best literature-aligned formula structure is:

```text
S = S_ref x (I / I_ref) x (C / C_ref)
```

Where:

- `S_ref` is the calibrated or reference spray amount
- `I_ref` is the chosen intervention threshold
- `C_ref` is the reference canopy condition

This section is added as documentation support only and does not change the currently implemented code formula.

## Latest project decision update

This section records the current active project direction without changing the implemented code.

- the current project keeps the existing code formula
- the reference constants are now taken from the handbook measurements already used in the project discussions
- the practical validation basis is oral validation from tomato farmers in Telangana state, India

## Handbook-based active reference constants

For the current project interpretation, the reference constants are:

- `P_ref` or `S_ref` = `4 ml per plant`
- `I_ref` = `40%`
- `D_ref` = `2.5 plants/m^2`

These are based on the handbook-style calculation already discussed:

- field area = `40,000 m^2`
- total plants = `10,000`
- total spray mixture = `40 liters`

Derived values:

```text
S_ref = (40 x 1000) / 10000 = 4 ml
D_ref = 10000 / 40000 = 2.5 plants/m^2
I_ref = 40%
```

So the active handbook-interpreted form is:

```text
S = 4 x (I / 40) x (D / 2.5)
```

Worked example for the current project:

```text
If I = 10% and D = 2.5,
S = 4 x (10 / 40) x (2.5 / 2.5) = 1 ml
```

## Validation note

Current practical validation recorded for this phase:

- oral validation from tomato farmers in Telangana state, India

This validation note is included as a practical local validation basis for the current logic and handbook-derived constants. It is not a formal experimental or peer-reviewed validation of the exact formula.

## Coexistence of handbook values and paper references

The documentation now intentionally keeps both:

1. handbook-based operational constants used in the current project
2. published-paper references for future refinement of greenhouse tomato spray logic

So at present:

- handbook values provide the active constants for `P_ref/S_ref`, `I_ref`, and `D_ref`
- published papers provide contextual guidance about canopy, pressure, LAI, growth stage, and deposition for future refinement
