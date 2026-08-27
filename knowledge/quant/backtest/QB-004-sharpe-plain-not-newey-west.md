---
id: QB-004
domain: quant/backtest
title: "Backtest: Use Plain Annualized Sharpe, Not Newey-West Corrected"
summary: "Use this when computing or reporting Sharpe ratios to ensure plain annualized Sharpe is used, with column name 'Sharpe' not 'Sharpe_NW'."
tags: [sharpe, backtest, performance-metric, newey-west, reporting]
keywords: [Newey-West Sharpe, HAC correction, annualized Sharpe, Sharpe_NW, performance table, Sharpe calculation]
aliases: ["Sharpe_NW vs Sharpe", "plain Sharpe", "no Newey-West"]
triggers: [Sharpe ratio, performance metrics, Newey-West, HAC correction, Sharpe_NW, experiment table column]
severity: medium
date_created: 2026-03-15
source_project: 02HW_QT
transferable: false
---

## Problem
Scripts and output tables report Newey-West corrected Sharpe (`Sharpe_NW`) when plain annualized Sharpe is preferred. Inconsistent column naming makes table comparisons unreliable.

## Root Cause
Newey-West HAC correction adjusts for autocorrelation in returns — academically valid but not preferred for this project's internal reporting standards.

## Solution
```python
# WRONG — Newey-West corrected Sharpe
from statsmodels.stats.sandwich_covariance import cov_hac
nw_var = cov_hac(pnl_series, nlags=4)
sharpe_nw = pnl_series.mean() / np.sqrt(nw_var) * np.sqrt(252)

# CORRECT — plain annualized Sharpe
sharpe = pnl_series.mean() / pnl_series.std() * np.sqrt(252)

# Output table column name: "Sharpe" not "Sharpe_NW"
```

## Prevention
- **Rule**: Column header = `"Sharpe"`, not `"Sharpe_NW"`
- **Rule**: Use `mean(pnl) / std(pnl) * sqrt(freq)` — no HAC correction
- See `projects/PRJ-002-experiment-output-table-format.md` for full standard table format

## Related
- knowledge/projects/PRJ-002-experiment-output-table-format.md
- knowledge/quant/backtest/QB-002-benchmark-date-alignment.md
