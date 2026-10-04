# Marvel Legends Pricing, 2019–2026

**Production Costs, Demand, and the Persistence of Higher Prices**  
Joe Guido — BFIN515 Economic Analysis (5061)

## Project question

This project asks how changes in observable production-cost pressures and demand conditions were associated with the standard retail price of Hasbro Marvel Legends six-inch action figures from 2019 through August 2026.

The study does **not** attempt to reconstruct Hasbro's confidential unit cost, profit margin, or full pricing equation. Public data are used as transparent proxies for the economic environment surrounding three observed MSRP increases.

## Why this matters

For a manager, investor, or analyst, the practical question is whether a product's price path can be understood as simple cost pass-through or whether different cost shocks, demand conditions, and pricing persistence matter at different times.

The main conclusion is that the three Marvel Legends price increases occurred under materially different cost environments. Production-cost pressure was most visible around the 2021–2022 increases, while the 2025 increase occurred after several pandemic-era cost pressures had eased. Higher price tiers also persisted after some input pressures weakened, so the observed price path is not consistent with a simple one-for-one cost-plus rule.

## Data

The core monthly sample runs from **January 2019 through August 2026** and includes:

- Marvel Legends standard MSRP regime
- thermoplastic plastics/resin producer-price index
- tooling/dies index
- paints index
- packaging inputs and an equal-weight packaging composite
- deep-sea freight producer-price index
- USD/CNY exchange rate
- U.S. hobby/toy/game retail sales and year-over-year growth

The frozen workbook also contains Hasbro accounting context, labor sensitivity analysis, tariff context, demand evidence, source provenance, model diagnostics, and robustness tables.

The study intentionally excludes retailer exclusives, deluxe/oversized figures, multipacks, vehicles, and other nonstandard price tiers. Build-a-Figure parts and accessories are treated as embedded product costs rather than separate predictors.

## Method

The preferred regression uses twelve-month percentage changes:

`Δ12 MSRP_t = α + β1 Δ12 Resin_t + β2 Δ12 Tooling_t + β3 Δ12 Freight_t + β4 Demand_t + ε_t`

where `Δ12 X_t = X_t / X_(t-12) - 1`.

HAC/Newey-West standard errors with 12 lags are used because overlapping annual-change windows create serial dependence. Common supply lags of 0, 3, 6, 9, and 12 months are tested as robustness checks. The analysis also compares the regression evidence with six- and twelve-month windows before the three actual price transitions.

This is an **associational** study. It does not claim causal identification. Endogeneity remains possible because demand measured in retail dollars can itself rise when prices rise, and unobserved factors such as licensing, retailer economics, product mix, promotions, and corporate pricing objectives may affect both price and market conditions.

## Headline results

Preferred annual-change regression (N = 79):

| Predictor | Standardized beta | HAC p-value |
|---|---:|---:|
| Resin | +0.173 | 0.091 |
| Tooling | +0.315 | 0.041 |
| Freight | +0.478 | <0.001 |
| Demand proxy | -0.076 | 0.143 |

Model fit: **R² = 0.630**, **adjusted R² = 0.610**, **maximum VIF = 2.29**.

The rejected raw-level diagnostic model had an R² near 0.96 but a maximum VIF near 185. It is retained only as an example of why trending levels can create misleadingly strong fits.

## Validation and robustness

The frozen V20 workbook was independently rerun through a separate validation pipeline. The preferred coefficients, HAC standard errors, VIFs, lag models, and robustness checks reproduced without material numerical differences.

Important limitations remain: there are only **three upward pricing decisions**, so 92 monthly rows must not be interpreted as 92 independent pricing choices. The models describe conditional associations and timing patterns, not causal pass-through rates.

## Repository contents

- `paper/` — final paper PDF
- `data/action_figure_production_study_working_data_v20.xlsx` — frozen research workbook
- `data/monthly_model_data.csv` — clean model-ready monthly data used by the reproduction script
- `data/source_register.csv` — source/provenance register from the workbook
- `code/reproduce_analysis.py` — reproduces the preferred model and major robustness checks
- `code/requirements.txt` — Python dependencies
- `validation/VALIDATION_REPORT.md` — independent reproducibility review
- `figures/` — charts used in the paper and appendix
- `outputs/` — generated regression summaries after running the script

## Reproduce the analysis

From the repository root:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r code/requirements.txt
```

Run:

```bash
python code/reproduce_analysis.py
```

The script writes CSV summaries and benchmark checks to `outputs/`. The frozen benchmark checks should report **PASS** when the published data and specification are reproduced correctly.

## Data provenance

Most monthly economic series are public U.S. government/FRED series. Exact series IDs, URLs, date coverage, transformations, Hasbro filings, tariff sources, labor sources, and product-price evidence are preserved in `data/source_register.csv` and the frozen V20 workbook.

## Interpretation

The study's governing rule is simple: when Marvel Legends-specific cost data are not public, the analysis uses a transparent proxy or bounded sensitivity range and does not manufacture precision. Public proxy data are used to classify the **direction, relative magnitude, and timing of economic pressure** surrounding known price changes rather than to estimate missing Hasbro dollar costs or profits.
