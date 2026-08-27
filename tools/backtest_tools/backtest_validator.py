"""Backtest Validator — Check backtest results for common issues.

Flags suspiciously good results that may indicate lookahead bias or other errors.
"""

import numpy as np
import pandas as pd


def validate_backtest(
    returns: pd.Series,
    benchmark_returns: pd.Series | None = None,
    freq: int = 252,
) -> dict:
    """Validate backtest results for reasonableness.

    Returns:
        Dict with validation checks and pass/fail status.
    """
    checks = {}

    ann_ret = returns.mean() * freq
    ann_vol = returns.std() * np.sqrt(freq)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

    # Check 1: Suspiciously high Sharpe
    checks["sharpe_reasonable"] = {
        "value": round(sharpe, 3),
        "status": "PASS" if sharpe < 3.0 else "WARN",
        "message": f"Sharpe={sharpe:.3f}" + (" — suspiciously high, check for lookahead bias" if sharpe >= 3.0 else ""),
    }

    # Check 2: Negative return days ratio
    neg_ratio = (returns < 0).mean()
    checks["neg_day_ratio"] = {
        "value": round(neg_ratio, 3),
        "status": "PASS" if neg_ratio > 0.30 else "WARN",
        "message": f"{neg_ratio:.1%} negative days" + (" — too few, may be unrealistic" if neg_ratio <= 0.30 else ""),
    }

    # Check 3: Max single-day return
    max_ret = returns.abs().max()
    checks["max_single_day"] = {
        "value": round(float(max_ret), 4),
        "status": "PASS" if max_ret < 0.20 else "WARN",
        "message": f"Max |return|={max_ret:.2%}" + (" — check for data errors" if max_ret >= 0.20 else ""),
    }

    # Check 4: Return autocorrelation (high autocorrelation = suspicious)
    autocorr = returns.autocorr(lag=1)
    checks["autocorrelation"] = {
        "value": round(float(autocorr), 3) if not np.isnan(autocorr) else None,
        "status": "PASS" if abs(autocorr) < 0.1 else "WARN",
        "message": f"Lag-1 autocorr={autocorr:.3f}" + (" — high autocorrelation is suspicious" if abs(autocorr) >= 0.1 else ""),
    }

    all_passed = all(c["status"] == "PASS" for c in checks.values())
    return {"passed": all_passed, "checks": checks}
