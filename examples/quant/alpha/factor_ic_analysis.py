"""Example: Factor IC Analysis (Best Practice)

Demonstrates the correct way to compute Information Coefficient (IC)
for an alpha factor, avoiding pitfalls documented in knowledge/quant/alpha/.

Key rules applied:
  - Q001: No bfill on time series
  - Q002: Signal shifted by 1 period
  - Q003: Winsorize before neutralization
  - Q004: Expanding window for z-score
"""

import numpy as np
import pandas as pd


def compute_factor_ic(
    factor: pd.DataFrame,
    forward_returns: pd.DataFrame,
    lag: int = 1,
) -> pd.Series:
    """Compute rank IC between factor values and forward returns.

    Args:
        factor: DataFrame with index=date, columns=stock_codes, values=factor_values
        forward_returns: DataFrame with same shape, values=forward returns
        lag: Signal delay in periods (minimum 1 to avoid lookahead)

    Returns:
        Series of IC values indexed by date
    """
    if lag < 1:
        raise ValueError(
            "lag must be >= 1 to avoid lookahead bias (Rule Q002). "
            "See knowledge/quant/backtest/lookahead-bias.md"
        )

    # CRITICAL: Shift factor by lag periods to prevent lookahead bias (Q002)
    lagged_factor = factor.shift(lag)

    # Compute rank IC for each cross-section
    ic_series = {}
    for date in lagged_factor.index:
        if date not in forward_returns.index:
            continue

        f = lagged_factor.loc[date].dropna()
        r = forward_returns.loc[date].dropna()

        # Align
        common = f.index.intersection(r.index)
        if len(common) < 30:  # Need sufficient stocks for meaningful IC
            continue

        # Spearman rank correlation
        ic = f[common].rank().corr(r[common].rank())
        ic_series[date] = ic

    return pd.Series(ic_series, name="IC")


def winsorize_factor(factor: pd.DataFrame, lower: float = 0.01, upper: float = 0.99) -> pd.DataFrame:
    """Winsorize factor cross-sectionally (Q003: winsorize before neutralization).

    Args:
        factor: Factor values (date x stocks)
        lower: Lower quantile for clipping
        upper: Upper quantile for clipping
    """
    def _winsorize_row(row: pd.Series) -> pd.Series:
        lo = row.quantile(lower)
        hi = row.quantile(upper)
        return row.clip(lower=lo, upper=hi)

    return factor.apply(_winsorize_row, axis=1)


def expanding_zscore(factor: pd.DataFrame) -> pd.DataFrame:
    """Standardize using expanding window (Q004: no full-period z-score).

    Uses only past data for mean/std computation.
    """
    expanding_mean = factor.expanding(min_periods=20).mean()
    expanding_std = factor.expanding(min_periods=20).std()
    return (factor - expanding_mean) / expanding_std


def analyze_factor(
    factor_raw: pd.DataFrame,
    forward_returns: pd.DataFrame,
) -> dict:
    """Full factor analysis pipeline following best practices.

    Steps:
    1. Winsorize (Q003)
    2. Standardize with expanding window (Q004)
    3. Shift by 1 period (Q002)
    4. Compute IC, ICIR, decay
    """
    # Step 1: Winsorize cross-sectionally
    factor_win = winsorize_factor(factor_raw)

    # Step 2: Expanding z-score (NOT full-period)
    factor_std = expanding_zscore(factor_win)

    # Step 3 & 4: Compute IC with lag=1 (prevents lookahead)
    ic = compute_factor_ic(factor_std, forward_returns, lag=1)

    # Summary statistics
    results = {
        "mean_ic": ic.mean(),
        "ic_std": ic.std(),
        "icir": ic.mean() / ic.std() if ic.std() > 0 else 0,
        "ic_positive_ratio": (ic > 0).mean(),
        "n_periods": len(ic),
    }

    # IC decay analysis
    for lag in [1, 2, 3, 5, 10, 20]:
        decay_ic = compute_factor_ic(factor_std, forward_returns, lag=lag)
        results[f"ic_lag{lag}"] = decay_ic.mean()

    return results


# ── Demo with synthetic data ─────────────────────────────

if __name__ == "__main__":
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    stocks = [f"S{i:03d}" for i in range(100)]

    # Synthetic factor with some predictive power
    factor_raw = pd.DataFrame(
        np.random.randn(len(dates), len(stocks)),
        index=dates,
        columns=stocks,
    )

    # Synthetic forward returns (weakly correlated with factor)
    noise = np.random.randn(len(dates), len(stocks))
    forward_returns = pd.DataFrame(
        0.02 * factor_raw.values + 0.98 * noise,
        index=dates,
        columns=stocks,
    )

    results = analyze_factor(factor_raw, forward_returns)

    print("Factor Analysis Results:")
    for k, v in results.items():
        print(f"  {k}: {v:.4f}")
