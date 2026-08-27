"""Turnover Analyzer — Analyze portfolio turnover and transaction cost impact."""

import numpy as np
import pandas as pd


def compute_turnover(positions: pd.DataFrame) -> pd.Series:
    """Compute daily portfolio turnover.

    Args:
        positions: Position weights (date x stocks)

    Returns:
        Series of daily turnover values.
    """
    changes = (positions - positions.shift(1)).abs()
    turnover = changes.sum(axis=1) / 2  # One side
    return turnover


def analyze_turnover(
    positions: pd.DataFrame,
    returns: pd.Series,
    cost_scenarios: list[float] | None = None,
) -> dict:
    """Analyze turnover and its impact on strategy performance.

    Args:
        positions: Position weights (date x stocks)
        returns: Gross strategy returns
        cost_scenarios: List of cost assumptions in bps (default: [5, 10, 20, 50])
    """
    if cost_scenarios is None:
        cost_scenarios = [5.0, 10.0, 20.0, 50.0]

    turnover = compute_turnover(positions)
    freq = 252

    result = {
        "avg_daily_turnover": round(float(turnover.mean()), 4),
        "median_daily_turnover": round(float(turnover.median()), 4),
        "ann_turnover": round(float(turnover.mean() * freq), 2),
        "cost_impact": {},
    }

    gross_sharpe = returns.mean() / returns.std() * np.sqrt(freq) if returns.std() > 0 else 0

    for cost_bps in cost_scenarios:
        cost_drag = turnover * cost_bps / 10000
        net_returns = returns - cost_drag
        net_sharpe = net_returns.mean() / net_returns.std() * np.sqrt(freq) if net_returns.std() > 0 else 0

        result["cost_impact"][f"{cost_bps}bps"] = {
            "ann_cost_drag": round(float(cost_drag.mean() * freq), 4),
            "net_sharpe": round(float(net_sharpe), 3),
            "sharpe_decay": round(float(gross_sharpe - net_sharpe), 3),
        }

    return result
