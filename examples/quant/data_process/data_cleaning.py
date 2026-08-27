"""Example: Data Cleaning Best Practices

Demonstrates correct data preprocessing for quant research,
avoiding pitfalls documented in knowledge/quant/data_process/.

Key rules:
  - Q001: Never use bfill on time series
  - Proper handling of missing data, outliers, timestamps
"""

import numpy as np
import pandas as pd


def clean_price_data(
    df: pd.DataFrame,
    price_col: str = "close",
    volume_col: str = "volume",
) -> pd.DataFrame:
    """Clean raw price data following best practices.

    Args:
        df: Raw price data with datetime index
        price_col: Column name for close price
        volume_col: Column name for volume
    """
    df = df.copy()

    # 1. Remove exact duplicate timestamps
    df = df[~df.index.duplicated(keep="first")]

    # 2. Sort by timestamp
    df = df.sort_index()

    # 3. Handle missing prices
    # GOOD: Forward fill (use last known price)
    df[price_col] = df[price_col].ffill()
    # BAD: df[price_col] = df[price_col].bfill()  # ← NEVER DO THIS (Q001)

    # 4. Handle zero/negative prices
    df.loc[df[price_col] <= 0, price_col] = np.nan
    df[price_col] = df[price_col].ffill()

    # 5. Handle volume
    df[volume_col] = df[volume_col].fillna(0)
    df.loc[df[volume_col] < 0, volume_col] = 0

    return df


def winsorize_cross_section(
    data: pd.DataFrame,
    lower_pct: float = 0.01,
    upper_pct: float = 0.99,
) -> pd.DataFrame:
    """Winsorize data cross-sectionally (row by row).

    Must be done BEFORE neutralization (Q003).
    """
    def _clip_row(row):
        lo = row.quantile(lower_pct)
        hi = row.quantile(upper_pct)
        return row.clip(lower=lo, upper=hi)

    return data.apply(_clip_row, axis=1)


def check_timestamp_alignment(
    *dataframes: pd.DataFrame,
    expected_freq: str = "B",
) -> dict:
    """Check if multiple DataFrames have aligned timestamps.

    Returns a report of alignment issues.
    """
    report = {"aligned": True, "issues": []}

    if len(dataframes) < 2:
        return report

    base_index = dataframes[0].index

    for i, df in enumerate(dataframes[1:], start=1):
        missing_in_base = df.index.difference(base_index)
        missing_in_other = base_index.difference(df.index)

        if len(missing_in_base) > 0:
            report["aligned"] = False
            report["issues"].append(
                f"DataFrame {i} has {len(missing_in_base)} dates not in base"
            )

        if len(missing_in_other) > 0:
            report["aligned"] = False
            report["issues"].append(
                f"Base has {len(missing_in_other)} dates not in DataFrame {i}"
            )

    return report


if __name__ == "__main__":
    # Demo data cleaning
    dates = pd.date_range("2024-01-01", periods=10, freq="B")
    raw_data = pd.DataFrame({
        "close": [100, 101, np.nan, 103, -1, 105, 106, np.nan, 108, 109],
        "volume": [1000, 1200, np.nan, 800, 900, -100, 1100, 1300, 0, 1500],
    }, index=dates)

    print("Raw data:")
    print(raw_data)

    clean = clean_price_data(raw_data)
    print("\nCleaned data:")
    print(clean)
