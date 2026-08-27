---
id: LIB-001
domain: libraries
title: "Pandas: Chained Assignment, apply() Performance, and bfill Lookahead"
summary: "Use this when writing pandas data manipulation to avoid silent data loss from chained assignment, performance traps from apply(), and bfill lookahead bias."
tags: [pandas, performance, chained-assignment, copy, dtype, apply, bfill]
keywords: [SettingWithCopyWarning, loc vs iloc, bfill lookahead, apply slow, inplace, float32 memory, vectorized pandas]
aliases: ["pandas gotchas", "pandas chained assignment", "SettingWithCopyWarning"]
triggers: [pandas chained assignment, SettingWithCopyWarning, bfill pandas, apply() performance, loc iloc, DataFrame assignment]
severity: high
date_created: 2026-03-14
source_project: general
transferable: true
---

## Problem
Several common pandas patterns silently produce incorrect results or cause severe performance degradation in quant research code.

## Root Cause / Patterns

### 1. Chained Assignment (Silent Data Loss)
```python
# WRONG — may or may not modify original df
df[df['sector'] == 'Tech']['score'] = 0

# CORRECT
df.loc[df['sector'] == 'Tech', 'score'] = 0
```

### 2. `apply()` on Large DataFrames (Performance)
```python
# WRONG — Python loop, 100x slower on large frames
factor = prices.apply(lambda x: x.rolling(20).mean() / x.rolling(60).mean() - 1)

# CORRECT — vectorized
factor = prices.rolling(20).mean() / prices.rolling(60).mean() - 1
```

### 3. `bfill()` / `ffill()` Without Lag (Lookahead)
```python
# WRONG — fills today's NaN with FUTURE value
df['signal'] = df['signal'].bfill()

# CORRECT — only fill with past values
df['signal'] = df['signal'].ffill()
# Or: shift before any fill
```

### 4. `inplace=True` with Chained Operations
```python
# WRONG — behavior undefined with copy vs view
df.dropna(inplace=True).reset_index(inplace=True)  # may fail

# CORRECT — reassign
df = df.dropna().reset_index(drop=True)
```

### 5. Default `float64` Precision Waste
For large panel data (dates × stocks), use `float32` where exact precision isn't needed — cuts memory in half.

## Prevention
- Enable `pd.options.mode.chained_assignment = 'raise'` in development
- Use `.loc[]` and `.iloc[]` exclusively for setting values
- Profile with `%timeit` before using `apply()` — consider vectorized alternatives first
- rules/L3_libraries.yaml covers pandas-specific linter rules

## Related
- rules/L3_libraries.yaml — LIB001-LIB004 pandas rules
- examples/libraries/pandas_vectorized.py — vectorized vs apply benchmark
- knowledge/quant/backtest/QB-001-lookahead-bias.md — bfill lookahead connection
