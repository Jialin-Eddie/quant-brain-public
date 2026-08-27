---
id: QB-002
domain: quant/backtest
title: "Backtest: Benchmark Must Be Computed Over Strategy's pnl_dates Only"
summary: "Use this when computing benchmark returns in a backtest to ensure benchmark PnL dates align exactly to strategy pnl_dates, not all OOS dates."
tags: [benchmark, backtest, date-alignment, oos, sharpe, ewbenchmark]
keywords: [EW benchmark, MCW benchmark, pnl_dates, all_test_dates, OOS comparison, benchmark Sharpe mismatch, date range mismatch]
aliases: ["benchmark date mismatch", "pnl_dates benchmark", "OOS date alignment", "EW benchmark wrong dates"]
triggers: [benchmark computation, EW benchmark, MCW benchmark, Sharpe comparison, OOS benchmark, date alignment, pnl_dates]
severity: high
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
Benchmark (EW / MCW) Sharpe differs from the strategy Sharpe even when performance should be comparable. The benchmark covers more dates than the strategy because the last few OOS dates have no strategy PnL (no t+1 return available).

**Confirmed case**: 4 extra December 2024 dates (including -0.77% and -0.96% crash days) in `08_alpha_benchmark.py` caused EW Sharpe to differ by 0.022 vs `07_performance.py`.

## Root Cause
Walk-forward OOS returns require a t+1 lookforward — the last `H` OOS dates (where H = holding period) have no strategy PnL. If benchmark iterates over `all_test_dates` instead of `pnl_dates`, it includes those terminal crash/recovery days, skewing the comparison.

## Solution
```python
# BAD: benchmark covers all OOS dates including terminal dates with no strategy PnL
for t in all_test_dates:
    benchmark_pnl[t] = compute_ew_return(universe, t)

# GOOD: align benchmark exactly to strategy's non-NaN PnL dates
pnl_dates = strategy_pnl.dropna().index
for t in pnl_dates:
    benchmark_pnl[t] = compute_ew_return(universe, t)
```

## Prevention
- **Rule**: In every script that builds benchmarks, derive `pnl_dates = strategy_pnl.dropna().index` and iterate over those — never over `all_test_dates`
- **Check**: Assert `len(benchmark_pnl) == len(strategy_pnl.dropna())` before computing comparative Sharpe
- **Test**: Benchmark and strategy PnL Series must have identical `.index` before any comparison

## Related
- knowledge/quant/backtest/QB-001-lookahead-bias.md
- knowledge/quant/backtest/QB-004-sharpe-plain-not-newey-west.md
