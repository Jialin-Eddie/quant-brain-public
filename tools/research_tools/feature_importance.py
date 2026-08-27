"""Feature Importance — Rank features by predictive power."""

import numpy as np
import pandas as pd


def rank_features_by_ic(
    features: dict[str, pd.DataFrame],
    returns: pd.DataFrame,
    lag: int = 1,
) -> pd.DataFrame:
    """Rank features by average IC with forward returns.

    Args:
        features: Dict of {feature_name: DataFrame(date x stocks)}
        returns: Forward returns (date x stocks)
        lag: Signal lag (must be >= 1 per Q002)

    Returns:
        DataFrame with feature ranking.
    """
    if lag < 1:
        raise ValueError("lag must be >= 1 (Q002)")

    results = []
    for name, factor in features.items():
        lagged = factor.shift(lag)
        ics = []
        for date in lagged.index:
            if date not in returns.index:
                continue
            f = lagged.loc[date].dropna()
            r = returns.loc[date].dropna()
            common = f.index.intersection(r.index)
            if len(common) < 30:
                continue
            ics.append(f[common].rank().corr(r[common].rank()))

        ic_series = pd.Series(ics)
        results.append({
            "feature": name,
            "mean_ic": ic_series.mean(),
            "ic_std": ic_series.std(),
            "icir": ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            "ic_positive_ratio": (ic_series > 0).mean(),
        })

    ranking = pd.DataFrame(results)
    ranking = ranking.sort_values("icir", ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1  # 1-based rank
    ranking.index.name = "rank"
    return ranking
