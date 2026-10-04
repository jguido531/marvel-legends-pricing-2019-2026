# Hasbro / Marvel Legends V20 validation

Validation date: October 2, 2026. Scope: the fixed workbook and specifications in `CODEX_TASK.md`, independently checked without model selection or final paper charts.

## Verdict

**PASS for quantitative reproduction, with documentation corrections and interpretation limits.** No specification-changing coding error or likely numerical data error was identified. The source workbook was unchanged. Its SHA-256 is `453c1e514e0bf2bee1cef0397d77df54fcb6c31fc7c7dec6b8b5d6a4927d66c2`, matching the manifest. All original manifest entries match.

## Reproduction and specifications

The supplied pipeline was run in a separate copy and completed successfully. The five supplied unit tests passed after regeneration. Independent matrix OLS and Bartlett/Newey-West covariance calculations also reproduce the baseline coefficients, HAC standard errors and normal-reference p-values. Fresh CSV and JSON results agree with the packaged outputs to numerical tolerance (relative 1e-9, absolute 1e-10). Workbook regression tables agree with the supplied numerical results. Runtime: Python 3.12, NumPy 2.5.3, statsmodels 0.15.0, SciPy 1.18.1; dependencies were installed separately in the workspace.

| Specification | N | R² | Adjusted R² |
|---|---:|---:|---:|
| Preferred annual change: resin, tooling, freight, demand | 79 | 0.629846 | 0.609837 |
| Packaging replaces tooling | 79 | 0.593962 | 0.572014 |
| Resin, broad-cost composite, demand | 79 | 0.622065 | 0.606948 |
| Level diagnostic | 91 | 0.958545 | 0.955584 |
| Common supply lag 0 months | 79 | 0.629846 | 0.609837 |
| Common supply lag 3 months | 76 | 0.586525 | 0.563231 |
| Common supply lag 6 months | 73 | 0.586452 | 0.562126 |
| Common supply lag 9 months | 70 | 0.573388 | 0.547135 |
| Common supply lag 12 months | 67 | 0.510246 | 0.478649 |
| Supply only | 80 | 0.628963 | 0.614317 |
| Preferred model through August 2025 | 68 | 0.720135 | 0.702365 |
| Mixed timing, exploratory: resin 12 months; tooling/freight current | 67 | 0.594417 | 0.568250 |

All models include an intercept and use HAC with 12 lags. Annual changes are `value(t)/value(t−12)−1`, expressed as fractions. Demand is contemporaneous sales YoY growth, also a fraction. Common lags apply equally to all three supply variables and leave demand current. The level diagnostic uses Jan-2019=100 levels for MSRP and five cost predictors, plus demand YoY; rebasing preserves fit and standardized coefficients but changes raw coefficient units. No separate best lag was selected.

Packaging is the equal-weight mean of four rebased indexes: ink, adhesives, paperboard and corrugated cartons. Independent recalculation agrees for all months. The broad-cost index equally weights tooling, paint, packaging and freight, then takes its annual change; it excludes resin, which enters separately. It is not the mean of their annual growth rates.

Baseline standardized betas and HAC p-values reproduce: resin 0.173229 (p=0.091294), tooling 0.315017 (p=0.041048), freight 0.477775 (p=0.000635), demand −0.076489 (p=0.142768). Maximum baseline VIF is 2.286531; level-model maximum VIF is 185.104696.

## Independent data audit and every automated flag

- The 92 months run consecutively from January 2019 through August 2026. No missing or duplicate month, nonfinite observed core value, or missing MSRP/cost/FX value was found. Independent reading agrees with every cleaned source variable; all six individual annual changes and the broad-cost annual change recompute correctly.
- MSRP is $19.99 through June 2021, $22.99 from July 2021, $24.99 from April 2022, and $27.99 from September 2025. These exactly reproduce the four tiers and three analytical breakpoints. They represent retail regimes with overlapping older product, rather than universal SKU effective dates.
- **The only missing-value flags are sales and demand YoY in August 2026.** The workbook explicitly limits demand coverage to July 2026. These are two missing fields in one month, not two missing months or an economic shock. Listwise deletion yields 79 annual-change observations (January 2020–July 2026), versus 80 supply-only observations through August 2026. No imputation occurred. Demand YoY agrees with sales ratios wherever both annual endpoints are present; the 2019 demand rates require 2018 source history absent from Monthly Master and cannot be independently reconstructed from this package.
- No jump meets the supplied cost/FX thresholds: 20% for resin/freight and 10% for tooling/paint/packaging/FX. Largest absolute monthly changes are resin +11.19% (May 2026), tooling +2.82% (January 2024), paint +5.27% (January 2022), packaging +2.49% (August 2022), freight +13.08% (May 2022), and CNY per USD +4.17% (May 2022). None shows an isolated factor-of-100 or unit-switch pattern. Different PPI base levels are legitimate; indexes are rebased before averaging. Sales are millions of dollars, MSRP is dollars, and EXCHUS is CNY per USD.
- The supplied jump audit omits sales/demand. Independent inspection finds sales −58.40% in April 2020 followed by +211.21% in May 2020, consistent with a plausible pandemic interruption/rebound, and large recurring holiday moves in unadjusted sales. These warrant economic context rather than automatic correction. This assessment is internal plausibility, not independent authentication of the underlying government releases.
- No stored Excel error cell was found. The reader uses stored values, not an Excel recalculation engine. Independent arithmetic checks address the transformations actually used here; a clean error scan alone cannot establish that every unrelated workbook calculation is correct.

## Discrepancies and code assumptions

1. **Workbook narrative corrections:** Freight Analysis row 10 calls August 2026 (518.617) a new study-period high, but July 2026 is higher (521.184). Demand Analysis row 11 describes 2025 category recovery as 6%, whereas its displayed $2.0bn to $2.1bn series computes 5%; clarify unrounded source figures or correct the text. Neither discrepancy changes regressions.
2. **Stale documentation:** Read Me still labels the file v1 and Current Version V5. Early Data Status rows still say to test lags or verify breakpoints despite later completed entries. The transition-evidence snapshot contains 2021/2022 evidence only; the September 2025 breakpoint appears in MSRP Timeline and Monthly Master. Complete the evidence appendix before submission.
3. **Output coverage:** Coefficient CSVs omit intercepts, and JSON omits some robustness standard errors, p-values and VIFs even though these are computed and fuller robustness tables exist in the workbook. This is incomplete export coverage, not an inconsistent specification. The pre-2025 test checks freight beta against 0.5909 at only three-decimal precision; the actual value is 0.591036522 and passes.
4. **Audit/test limitations:** Missing core values are reported but do not independently trigger the automated failure verdict. Tests read saved outputs, so tests passing after a failed pipeline would not prove regeneration. The pipeline correctly stops on subprocess failure. Its initial regression attempt failed because statsmodels was absent; that initial test pass was excluded from reproduction evidence.
5. **Implementation assumptions:** The XLSX reader assumes the Windows/1900 date system and consumes stored values; both are suitable for this source. Row-position annual changes/lags assume sorted consecutive months, confirmed independently. Normalization uses the first available value, confirmed to be January 2019. Broad-cost averaging would silently change component weights if a component were missing, but all components are complete here. Requirements specify minimum versions rather than a reproducible environment lock.

No analysis scripts, specifications, source cells or original packaged results were patched. Audit text line endings can differ between platforms without changing substantive findings.

## Material methodological concerns and paper decision

Only three upward pricing decisions underlie the monthly observations. Annual differencing and 12-lag HAC reduce particular trend/dependence problems but do not create independent pricing events, eliminate omitted variables, or establish causal identification. Default inference uses asymptotic normal p-values, Bartlett weights and no finite-sample HAC correction. Extremely small lag-model p-values should receive restrained interpretation given overlapping windows and the short sample.

Lag models use successively shorter samples, so differences in R² and AIC combine timing and sample effects. Supply-only also adds August 2026, so it is not a pure demand-removal comparison on identical observations. These are limitations of the fixed checks; no alternative model was searched or substituted. Broad nominal retail sales reflect prices as well as quantities and are not Marvel Legends demand. Equal-weight composites are transparent proxy constructions, not Hasbro cost shares. Tariff and labor context remains outside these monthly regressions.

**The V20 quantitative results are safe to carry into the paper as reproducible exploratory associations, subject to the narrative corrections above and explicit reporting of samples, units, dependence and proxy limitations.** Keep the approximately 96% level fit as a warning example. Give transition-window evidence and the differing 2021, 2022 and 2025 backdrops substantial interpretive weight. Do not present any coefficient as causation or product-level pass-through. This validation confirms internal reproduction from the frozen workbook; it does not independently certify every external source or qualitative claim.
