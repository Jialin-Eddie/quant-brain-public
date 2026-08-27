---
id: QD-002
domain: quant/data_process
title: "Winsorization: Use Per-Date Cross-Section Bounds, Never Global History"
summary: "Use this when applying any preprocessing to OOS/test data to prevent cross-date leakage from global historical quantile bounds in winsorization."
tags: [winsorization, lookahead, cross-section, oos, data-leakage, preprocessing]
keywords: [global winsorization, per-date bounds, cross-date leakage, OOS preprocessing, train quantiles OOS fallback, winsorization lookback, expanding winsorize]
aliases: ["global winsorization bug", "per-date winsorize", "OOS winsorization leakage", "cross-date winsorization"]
triggers: [OOS preprocessing, winsorization OOS, global quantile bounds, apply_preprocess_pipeline, train test preprocessing]
severity: critical
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
Winsorization on OOS/TEST data uses global training-period quantiles (e.g., `global_p01`, `global_p99`) as a fallback for dates not found in a stored `train_params` dict. Since no OOS date is in `train_params`, the fallback always triggers — meaning OOS data is clipped using bounds derived from pooling all historical information, a look-ahead form of cross-date leakage.

## Root Cause
`apply_preprocess_pipeline` pattern:
1. For TRAIN dates: looks up stored per-date quantiles ✓ (correct)
2. For OOS dates: date not found in dict → falls through to global bounds ✗ (wrong)

The per-date dict lookup for OOS is always wrong — OOS dates will never be in the train dict, so every OOS date silently uses the global fallback.

## Solution
```python
# WRONG — uses pooled historical bounds for all OOS dates
def winsorize(factor, date, train_params, global_p01, global_p99):
    if date in train_params:
        lo, hi = train_params[date]['p01'], train_params[date]['p99']
    else:
        lo, hi = global_p01, global_p99  # BAD: leaks future data into OOS
    return factor.clip(lo, hi)

# CORRECT — each date computes its own cross-section bounds on the fly
def winsorize(factor, date, pct=0.01):
    # Works identically for TRAIN and OOS — no dict lookup needed
    lo = factor.quantile(pct)
    hi = factor.quantile(1 - pct)
    return factor.clip(lo, hi)
```

## Prevention
- **Rule**: TRAIN and OOS winsorization must use the same code path — per-date cross-section quantiles computed on the fly
- **Rule**: Never store train-period quantile dicts and use them as fallbacks for OOS
- **Check**: Assert that winsorization bounds are computed from the current date's cross-section, never from a pre-computed global dict
- See `QD-001` for winsorization ordering rule (winsorize → neutralize → standardize)

## Related
- knowledge/quant/data_process/QD-001-winsorization-order.md — winsorization ordering
- knowledge/quant/backtest/QB-001-lookahead-bias.md — broader lookahead bias patterns
