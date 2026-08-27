---
id: QB-003
domain: quant/backtest
title: "Backtest: Turnover Must Account for Weight Drift, Not Just Basket Changes"
summary: "Use this when calculating portfolio turnover or transaction costs to correctly account for intra-holding-period weight drift from price movement."
tags: [turnover, backtest, transaction-cost, weight-drift, mktcap, rebalancing]
keywords: [weight drift, buy and hold, turnover underestimate, equal weight drift, market cap drift, one-way turnover, basket composition, rebalancing cost]
aliases: ["turnover drift bug", "weight drift turnover", "mktcap drift rebalancing"]
triggers: [turnover calculation, transaction costs, rebalancing, weight drift, equal weight basket, holding period returns]
severity: high
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
Turnover calculation only counts stocks entering/exiting the basket, ignoring the weight drift that occurs within the holding period as prices move. In a 5-day equal-weight basket, even if the same stocks stay in the basket, equal weights must be restored at next rebalance — this requires trading proportional to how far weights have drifted.

## Root Cause
Naive turnover = `(entering stocks) / N` only captures compositional changes. In reality, a buy-and-hold basket sees weight drift every day. Restoring target weights at rebalance requires trades proportional to `|w_target - w_drifted|`, not just stock entry/exit.

Additionally, `compute_basket_5d` using `total_ret += day_rets.mean()` implies daily rebalancing (not true buy-and-hold) and only works for equal-weight.

## Solution
```python
# WRONG — only counts composition changes, misses drift
entering = curr_basket - prev_basket
turnover = len(entering) / len(curr_basket)

# CORRECT — accounts for drift
# 1. Compute end-of-period drifted weights (buy-and-hold from last rebal)
w_drifted_i = w_init_i * (1 + r_i) / sum_j(w_init_j * (1 + r_j))

# 2. New target weights (e.g. equal weight = 1/N_new)
w_target_i = 1 / N_new

# 3. One-way turnover = 0.5 * sum|w_target - w_drifted|
turnover = 0.5 * sum(abs(w_target_i - w_drifted_i))
```

**Correct PnL formula (buy-and-hold, vectorized):**
```python
# ret_df: DataFrame shape (all_dates, stocks) — pre-built pivot table
for t_idx in rebal_date_indices:
    hold_ret = ret_df.iloc[t_idx : t_idx + 5]        # shape (5, N)
    cum_log  = np.log(1 + hold_ret).sum(axis=0)       # sum across days (log is time-additive)
    cum_ret  = np.exp(cum_log) - 1                    # back to simple return

    # Equal-weight basket:
    portfolio_pnl[t] = cum_ret[selected_stocks].mean()
    # Cap-weighted:
    portfolio_pnl[t] = (cum_ret * weights).sum()
```

**Key rules:**
- NEVER sum simple daily returns across days — use log then exp
- NEVER sum log returns across assets — log is NOT asset-additive
- ALWAYS build a `ret_df` pivot (date × permno) first, then use `.iloc` slicing + numpy

## Prevention
- **Rule**: Any turnover function must accept `w_init`, `prices_over_holding_period`, `w_target` — not just two basket sets
- **Rule**: `compute_basket_5d` must use compounding, not `day_rets.mean()` in a loop

## Related
- knowledge/quant/backtest/QB-001-lookahead-bias.md
- knowledge/quant/backtest/QB-002-benchmark-date-alignment.md
