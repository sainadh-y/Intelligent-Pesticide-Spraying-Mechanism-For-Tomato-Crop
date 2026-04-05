# Phase 4: Aggregation

## Goal

Combine the disease percentages from phase 2 and the leaf damage output from phase 3 into one infection average.

## Completion status

Completed.

## Final ranking order

The final disease priority order used in this project is:

1. `tomato_late_blight`
2. `tomato_early_blight`
3. `tomato_septoria_leaf_spot`
4. `tomato_bacterial_leaf_spot`
5. `tomato_leaf_mold`
6. `tomato_yellow_leaf_curl_virus`
7. `tomato_mosaic_virus`
8. `damage`

## Base reference used for the ranking direction

The exact numeric weights are project-defined, but the ranking direction is based on general tomato disease severity and management references:

- [MDPI review on important tomato diseases](https://www.mdpi.com/2037-0164/15/1/7)
- [Illinois IPM reference for tomato early blight and Septoria leaf spot](https://ipm.illinois.edu/diseases/series900/rpd908/)
- [Rutgers plant advisory reference for tomato late blight](https://plant-pest-advisory.rutgers.edu/vegetable-disease-of-the-week-72213-2-2-2/)
- [Horsfall-Barratt severity scale background](https://pubmed.ncbi.nlm.nih.gov/40934413/)

These references support the idea of relative disease seriousness and visible severity contribution, but they do not provide an official numeric weight table. The numbers below are the final project weights derived from your confirmed order.

## How the numeric weights were derived

To turn the final ranking into numeric weights, a simple descending rank-score method is used.

Assigned rank scores:

- `tomato_late_blight` = 8
- `tomato_early_blight` = 7
- `tomato_septoria_leaf_spot` = 6
- `tomato_bacterial_leaf_spot` = 5
- `tomato_leaf_mold` = 4
- `tomato_yellow_leaf_curl_virus` = 3
- `tomato_mosaic_virus` = 2
- `damage` = 1

Total score:

```text
8 + 7 + 6 + 5 + 4 + 3 + 2 + 1 = 36
```

Normalized weight formula:

```text
weight = rank_score / 36
```

## Final weights

- `tomato_late_blight` = `8/36` = `0.2222`
- `tomato_early_blight` = `7/36` = `0.1944`
- `tomato_septoria_leaf_spot` = `6/36` = `0.1667`
- `tomato_bacterial_leaf_spot` = `5/36` = `0.1389`
- `tomato_leaf_mold` = `4/36` = `0.1111`
- `tomato_yellow_leaf_curl_virus` = `3/36` = `0.0833`
- `tomato_mosaic_virus` = `2/36` = `0.0556`
- `damage` = `1/36` = `0.0278`

## Current implementation

- multiplies each disease percentage by its final weight
- multiplies average leaf damage percentage by the final damage weight
- sums all weighted components into one infection average

## Formula used

```text
infection_average =
    (tomato_late_blight x 0.2222) +
    (tomato_early_blight x 0.1944) +
    (tomato_septoria_leaf_spot x 0.1667) +
    (tomato_bacterial_leaf_spot x 0.1389) +
    (tomato_leaf_mold x 0.1111) +
    (tomato_yellow_leaf_curl_virus x 0.0833) +
    (tomato_mosaic_virus x 0.0556) +
    (damage x 0.0278)
```

## Output

- weighted infection average
- the final weights used for that calculation
