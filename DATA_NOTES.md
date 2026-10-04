# Data and Reproducibility Notes

## Sample

- Monthly coverage: January 2019 through August 2026
- Standard Marvel Legends single-figure MSRP only
- MSRP regimes used in the study:
  - $19.99 through June 2021
  - $22.99 from July 2021 through March 2022
  - $24.99 from April 2022 through August 2025
  - $27.99 beginning September 2025

## Model-ready CSV

`data/monthly_model_data.csv` is a transparent extract from the frozen V20 workbook's `Monthly Master` sheet. It exists so the reproduction script does not depend on Excel-specific formula behavior.

The final August 2026 observation lacks the monthly demand proxy. This is why the preferred model has N=79 while the supply-only robustness check has N=80 after twelve-month differencing.

## Proxy interpretation

The PPI and freight series are not Hasbro invoices and are not treated as Marvel Legends unit-cost weights. They represent observable movements in broader cost conditions. The packaging composite is an equal-weight composite of four packaging-related indexes, and the broad-cost robustness factor equally weights normalized tooling, paint, packaging, and freight levels before computing its annual change.

## Causality

No coefficient should be read as a causal pass-through rate. The study does not have a credible instrument, natural experiment, or Marvel Legends-specific cost panel sufficient for causal identification. The paper therefore uses language such as `associated with`, `aligned with`, and `consistent with`.

## Frozen benchmark

The reproducibility benchmark is the V20 workbook. The validation report confirms internal numerical reproduction while also documenting methodological limitations and stale workbook labels that do not affect the frozen calculations.
