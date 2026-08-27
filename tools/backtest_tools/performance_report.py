"""Performance Report — Generate standardized performance metrics."""

import numpy as np
import pandas as pd


def compute_metrics(returns: pd.Series, freq: int = 252) -> dict:
    """Compute standard performance metrics from a return series."""
    ann_ret = returns.mean() * freq
    ann_vol = returns.std() * np.sqrt(freq)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

    cum = (1 + returns).cumprod()
    peak = cum.expanding().max()
    drawdown = (cum - peak) / peak
    max_dd = drawdown.min()

    calmar = ann_ret / abs(max_dd) if max_dd != 0 else 0
    win_rate = (returns > 0).mean()

    return {
        "ann_return": round(float(ann_ret), 4),
        "ann_vol": round(float(ann_vol), 4),
        "sharpe": round(float(sharpe), 3),
        "max_drawdown": round(float(max_dd), 4),
        "calmar": round(float(calmar), 3),
        "win_rate": round(float(win_rate), 4),
        "n_days": len(returns),
    }


def format_performance_table(metrics: dict) -> str:
    """Format metrics as a readable table."""
    lines = ["Performance Summary", "=" * 40]
    labels = {
        "ann_return": "Annual Return",
        "ann_vol": "Annual Volatility",
        "sharpe": "Sharpe Ratio",
        "max_drawdown": "Max Drawdown",
        "calmar": "Calmar Ratio",
        "win_rate": "Win Rate",
        "n_days": "Trading Days",
    }
    for key, label in labels.items():
        val = metrics.get(key, "N/A")
        if isinstance(val, float):
            if key in ("ann_return", "ann_vol", "max_drawdown", "win_rate"):
                lines.append(f"  {label:20s}: {val:>10.2%}")
            else:
                lines.append(f"  {label:20s}: {val:>10.3f}")
        else:
            lines.append(f"  {label:20s}: {val:>10}")
    return "\n".join(lines)
