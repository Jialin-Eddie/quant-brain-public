---
id: QD-003
domain: quant/data_process
title: "Data Prep: Never Use np.vstack to Recombine Split Training Data"
summary: "Use this when combining split training arrays to prevent XGBoost irreproducibility caused by np.vstack reordering rows relative to original DataFrame index."
tags: [numpy, xgboost, training-data, row-order, reproducibility, vstack]
keywords: [np.vstack, np.concatenate, row order, sort_index, XGBoost subsample, training data shuffle, walk-forward recombine, pd.concat sort]
aliases: ["vstack row order bug", "numpy vstack training data", "XGBoost reproducibility row order"]
triggers: [np.vstack, training data merge, walk-forward recombine, grid search retrain, XGBoost subsample, pd.concat sort_index]
severity: high
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
When training data is split into parts (e.g., pre-validation + validation for grid search) and then recombined for final retraining, using `np.vstack` to merge the parts reorders rows. XGBoost's `subsample=0.8` samples rows by position — different row order → different random subsets → different model → different (irreproducible) predictions.

**Confirmed impact**: Caused Sharpe to swing from +0.163 to -0.018 in a L/S strategy due to row-order-dependent subsampling in final retrain.

## Root Cause
`np.vstack([X_pre, X_val])` concatenates in the order provided (all pre-2020 rows first, then 2020 rows). This deviates from the original parquet MultiIndex order. XGBoost's internal tree building and subsampling is position-based, so row reordering breaks reproducibility even with fixed random seeds.

## Solution
```python
# WRONG — reorders rows, breaks XGBoost reproducibility
X_base = np.vstack([X_pre, X_val])
y_base = np.concatenate([y_pre, y_val])

# CORRECT — preserves original parquet MultiIndex order
clean_base = pd.concat([clean_pre_val, clean_val]).sort_index()
X_base = clean_base[features].to_numpy(dtype=np.float64)
y_base = clean_base[TARGET].to_numpy(dtype=np.float64)
```

**General rule for any training data accumulation:**
```python
# WRONG
accumulated_X = np.vstack([accumulated_X, new_month_X])

# CORRECT
accumulated_df = pd.concat([accumulated_df, new_month_df]).sort_index()
X = accumulated_df[features].to_numpy(dtype=np.float64)
```

## Prevention
- **Rule**: Never use `np.vstack` or `np.concatenate` to recombine training data split from a DataFrame
- **Rule**: Always concat at DataFrame level with `.sort_index()` before `.to_numpy()`
- **Applies to**: any walk-forward accumulation, grid-search split/recombine, pre-val + val merges
- **Check**: If using `subsample < 1.0` in tree models, verify training data row order is deterministic

## Related
- knowledge/engineering/E-003-memory-leak-in-training-loops.md — other training loop pitfalls
