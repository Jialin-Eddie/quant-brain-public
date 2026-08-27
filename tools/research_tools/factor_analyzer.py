"""Factor Analyzer — Compute IC, ICIR, and quintile returns for alpha factors.

Usage:
    Import and use in research notebooks, or call via MCP tools.
"""

import numpy as np
import pandas as pd


def compute_rank_ic(factor: pd.DataFrame, returns: pd.DataFrame, lag: int = 1) -> pd.Series:
    """Compute cross-sectional rank IC between factor and forward returns.

    Args:
        factor: Factor values (date x stocks)
        returns: Forward returns (date x stocks)
        lag: Signal lag (must be >= 1 per Q002)
    """
    if lag < 1:
        raise ValueError("lag must be >= 1 to avoid lookahead bias (Q002)")

    lagged = factor.shift(lag)
    ic_values = {}

    for date in lagged.index:
        if date not in returns.index:
            continue
        f = lagged.loc[date].dropna()
        r = returns.loc[date].dropna()
        common = f.index.intersection(r.index)
        if len(common) < 30:
            continue
        ic_values[date] = f[common].rank().corr(r[common].rank())

    return pd.Series(ic_values, name="IC")


def compute_quintile_returns(
    factor: pd.DataFrame,
    returns: pd.DataFrame,
    n_groups: int = 5,
    lag: int = 1,
) -> pd.DataFrame:
    """Compute equal-weighted quintile portfolio returns."""
    if lag < 1:
        raise ValueError("lag must be >= 1 (Q002)")

    lagged = factor.shift(lag)
    group_returns = {f"Q{i+1}": [] for i in range(n_groups)}
    dates = []

    for date in lagged.index:
        if date not in returns.index:
            continue
        f = lagged.loc[date].dropna()
        r = returns.loc[date].dropna()
        common = f.index.intersection(r.index)
        if len(common) < n_groups * 5:
            continue

        try:
            groups = pd.qcut(f[common], n_groups, labels=False, duplicates="drop")
        except ValueError:
            continue

        dates.append(date)
        for g in range(n_groups):
            mask = groups == g
            group_returns[f"Q{g+1}"].append(r[common][mask].mean())

    result = pd.DataFrame(group_returns, index=dates)
    result["L/S"] = result["Q1"] - result[f"Q{n_groups}"]
    return result


def ic_summary(ic: pd.Series) -> dict:
    """Compute IC summary statistics."""
    return {
        "mean_ic": ic.mean(),
        "ic_std": ic.std(),
        "icir": ic.mean() / ic.std() if ic.std() > 0 else 0,
        "ic_positive_ratio": (ic > 0).mean(),
        "n_periods": len(ic),
    }
