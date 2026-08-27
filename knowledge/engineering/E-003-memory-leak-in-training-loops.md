---
id: E-003
domain: engineering
title: "Memory Leak: gc.collect() + del Mandatory in Walk-Forward Training Loops"
summary: "Use this when writing any loop that calls .fit() repeatedly to prevent RAM overflow from XGBoost memory retention and pandas reference cycles."
tags: [memory, gc, xgboost, training-loop, ram-overflow, walk-forward]
keywords: [memory leak, gc.collect, del model, RAM overflow, psutil, XGBoost memory, pandas reference cycle, walk-forward OOM, out of memory]
aliases: ["RAM overflow in training", "XGBoost memory leak", "gc.collect pattern", "OOM walk-forward"]
triggers: [walk-forward training, XGBoost fit loop, training loop, memory error, OOM, gc.collect, RAM overflow]
severity: high
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
Python process RAM overflows during walk-forward retraining loops (typically around iteration 20–30), killing all running tasks. XGBoost allocates RAM on each `.fit()` call but never releases it, and pandas DataFrame reference cycles prevent `del` alone from freeing memory.

**Confirmed crash conditions**: 1.58M row × 736 stock panel, 48+ walk-forward iterations, each XGBoost fit adding 200–400 MB.

## Root Cause
1. **XGBoost memory retention**: `xgb.XGBRegressor.fit()` does not release internal C++ allocations between calls (GitHub Issue #4843)
2. **Pandas reference cycles**: `del df` does not immediately free memory because pandas DataFrames participate in reference cycles that CPython's reference counter cannot break — `gc.collect()` is required to force cycle collection (Issue #49582)
3. **Loop accumulation**: Without cleanup, each iteration adds to resident set size (RSS) until OOM

## Solution
```python
import gc
import psutil

results = []
process = psutil.Process()

for i, month in enumerate(months):
    # Use .copy() to break reference to parent DataFrame
    train = df[df['date'] <= cutoff].copy()
    test  = df[df['date'] == test_date].copy()

    X_train = train[FEATURES].values
    y_train = train[TARGET].values
    X_test  = test[FEATURES].values

    model = xgb.XGBRegressor(...)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    results.append(preds)

    # MANDATORY: all three lines, every iteration
    del model, train, test, X_train, y_train, X_test
    gc.collect()

    # Recommended: monitor RAM per fold
    ram_gb = process.memory_info().rss / 1024**3
    print(f"[fold {i+1}/{len(months)}] RAM: {ram_gb:.2f} GB")
```

**Additional: load panel with memory-efficient dtypes once at script start**
```python
df = pd.read_parquet(PANEL_PATH)
df['permno'] = df['permno'].astype('category')   # 736 unique → saves ~80%
for col in FEATURES:
    df[col] = df[col].astype('float32')           # float64→float32 saves 50%
# Never load the full panel more than once per script
```

## Prevention
- **Rule**: Every loop that calls `.fit()` inside MUST end with `del` + `gc.collect()`
- **Rule**: Never load the full panel more than once per script
- **Applies to**: any `for` loop over months/folds/dates/model configs that calls `.fit()`, walk-forward retraining, grid searches, hyperparameter sweeps
- **Does NOT apply to**: single one-time model training, vectorized pandas operations outside a loop

## Related
- knowledge/engineering/E-002-logging-best-practices.md — monitoring pattern (psutil logging)
