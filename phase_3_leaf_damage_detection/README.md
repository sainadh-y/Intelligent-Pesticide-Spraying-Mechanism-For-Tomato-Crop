# Phase 3: Leaf Damage Detection

## Goal

Estimate the average visible damage percentage for the plant using only the `5-10` selected leaf images from phase 1.

## Completion status

Completed.

## Final decision used

- the current implementation is a rule-based visible-damage algorithm
- the logic-based workflow is now the accepted final direction for this project
- oral farmer validation from Telangana is the recorded validation basis

## Current implementation

- preprocessing is implemented
- visible leaf masking is implemented
- visible damage region estimation is implemented
- per-leaf and plant-level averaging are implemented

## Current output

- per-leaf damage percentages
- average leaf damage percentage for the plant

## Latest project decision update

This section is the current active project direction and should be treated as the latest interpretation.

- phase 3 is now being kept as a logic-based phase
- phase 3 is not being continued as an ML-model phase for the current version
- the existing rule-based visible-damage workflow is the intended implementation direction for now

## Validation

Current practical validation recorded for this phase:

- oral validation from tomato farmers in Telangana state, India

This means the current phase-3 logic is being retained based on practical farmer feedback rather than a trained dataset/model workflow.

## Current active logic for phase 3

The current logic-based phase-3 workflow is:

1. take the selected clear tomato leaf images from phase 1
2. preprocess each image
3. isolate the visible leaf region
4. estimate visible damage regions using image-processing logic
5. compute per-leaf damage percentage
6. average the damage percentage across the selected leaves
7. use that average as the plant-level damage output

## Active status under the latest decision

Under the latest decision to use logic rather than ML for this phase:

- phase 3 can be treated as completed in implementation terms
