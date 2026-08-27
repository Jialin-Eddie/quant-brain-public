"""Correlation Analyzer — Compute factor correlation matrices."""

import pandas as pd


def factor_correlation_matrix(
    factors: dict[str, pd.DataFrame],
    method: str = "spearman",
) -> pd.DataFrame:
    """Compute average cross-sectional correlation between factors.

    Args:
        factors: Dict of {factor_name: DataFrame(date x stocks)}
        method: Correlation method ('spearman' or 'pearson')

    Returns:
        Correlation matrix DataFrame.
    """
    names = list(factors.keys())
    n = len(names)
    corr_matrix = pd.DataFrame(index=names, columns=names, dtype=float)

    for i in range(n):
        for j in range(n):
            if i == j:
                corr_matrix.iloc[i, j] = 1.0
                continue

            fi = factors[names[i]]
            fj = factors[names[j]]
            common_dates = fi.index.intersection(fj.index)

            corrs = []
            for date in common_dates:
                ri = fi.loc[date].dropna()
                rj = fj.loc[date].dropna()
                common_stocks = ri.index.intersection(rj.index)
                if len(common_stocks) < 30:
                    continue
                if method == "spearman":
                    c = ri[common_stocks].rank().corr(rj[common_stocks].rank())
                else:
                    c = ri[common_stocks].corr(rj[common_stocks])
                corrs.append(c)

            corr_matrix.iloc[i, j] = sum(corrs) / len(corrs) if corrs else 0.0

    return corr_matrix
