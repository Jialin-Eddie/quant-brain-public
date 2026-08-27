"""Example: Backtest Without Lookahead Bias

Demonstrates how to structure a simple backtest that avoids
all common sources of lookahead bias (Q001, Q002, Q005).

See knowledge/quant/backtest/lookahead-bias.md for details.
"""

import numpy as np
import pandas as pd


def simple_factor_backtest(
    prices: pd.DataFrame,
    factor: pd.DataFrame,
    n_groups: int = 5,
    cost_bps: float = 10.0,
    lag: int = 1,
) -> pd.DataFrame:
    """Run a simple long-short factor backtest.

    Args:
        prices: Adjusted close prices (date x stocks)
        factor: Factor values (date x stocks)
        n_groups: Number of quantile groups
        cost_bps: Round-trip transaction cost in basis points (Q006)
        lag: Signal lag in periods (Q002: must be >= 1)

    Returns:
        DataFrame with group returns
    """
    if lag < 1:
        raise ValueError("lag must be >= 1 (Rule Q002)")

    # Step 1: Compute forward returns
    returns = prices.pct_change()

    # Step 2: CRITICAL — shift factor by lag periods (Q002)
    # We use YESTERDAY's factor to trade TODAY
    lagged_factor = factor.shift(lag)

    # Step 3: Assign stocks to quantile groups each day
    def assign_groups(row: pd.Series) -> pd.Series:
        valid = row.dropna()
        if len(valid) < n_groups * 2:
            return pd.Series(np.nan, index=row.index)
        # pd.qcut for equal-sized groups
        try:
            groups = pd.qcut(valid, n_groups, labels=False, duplicates="drop")
        except ValueError:
            return pd.Series(np.nan, index=row.index)
        return groups.reindex(row.index)

    group_assignments = lagged_factor.apply(assign_groups, axis=1)

    # Step 4: Compute group returns
    group_returns = {}
    for g in range(n_groups):
        mask = group_assignments == g
        # Equal-weighted return within group
        group_ret = (returns * mask).sum(axis=1) / mask.sum(axis=1)
        group_returns[f"Q{g+1}"] = group_ret

    result = pd.DataFrame(group_returns)

    # Long-short portfolio
    result["L/S"] = result[f"Q1"] - result[f"Q{n_groups}"]

    # Step 5: Apply transaction costs (Q006)
    # Estimate turnover from group changes
    turnover = (group_assignments != group_assignments.shift(1)).sum(axis=1) / group_assignments.notna().sum(axis=1)
    cost_drag = turnover * cost_bps / 10000.0

    result["L/S_after_cost"] = result["L/S"] - cost_drag

    return result


def compute_performance_metrics(returns: pd.Series, freq: int = 252) -> dict:
    """Compute standard performance metrics."""
    ann_ret = returns.mean() * freq
    ann_vol = returns.std() * np.sqrt(freq)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

    # Maximum drawdown
    cum = (1 + returns).cumprod()
    peak = cum.expanding().max()
    drawdown = (cum - peak) / peak
    max_dd = drawdown.min()

    return {
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "calmar": ann_ret / abs(max_dd) if max_dd != 0 else 0,
    }


if __name__ == "__main__":
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=504, freq="B")
    stocks = [f"S{i:03d}" for i in range(200)]

    # Synthetic prices
    log_returns = np.random.randn(len(dates), len(stocks)) * 0.02
    prices = pd.DataFrame(
        np.exp(np.cumsum(log_returns, axis=0)) * 100,
        index=dates,
        columns=stocks,
    )

    # Synthetic factor
    factor = pd.DataFrame(
        np.random.randn(len(dates), len(stocks)),
        index=dates,
        columns=stocks,
    )

    # Run backtest
    result = simple_factor_backtest(prices, factor, cost_bps=10, lag=1)

    # Report
    for col in ["Q1", "Q5", "L/S", "L/S_after_cost"]:
        if col in result.columns:
            metrics = compute_performance_metrics(result[col].dropna())
            print(f"\n{col}:")
            for k, v in metrics.items():
                print(f"  {k}: {v:.4f}")
