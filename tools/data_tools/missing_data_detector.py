"""Missing Data Detector — Analyze missing data patterns and suggest handling.

Usage:
    python tools/data_tools/missing_data_detector.py <csv_path>
"""

import argparse
import sys

import numpy as np
import pandas as pd


def detect_missing_patterns(df: pd.DataFrame) -> dict:
    """Analyze missing data patterns in a DataFrame.

    Returns:
        Dict with per-column missing info and pattern analysis.
    """
    total_rows = len(df)
    report = {"total_rows": total_rows, "columns": {}}

    for col in df.columns:
        missing_mask = df[col].isna()
        n_missing = missing_mask.sum()

        if n_missing == 0:
            continue

        # Detect pattern: random vs systematic
        # Check if missing values cluster together
        runs = missing_mask.astype(int).diff().abs().sum()
        avg_run_length = n_missing / max(runs / 2, 1)

        pattern = "random" if avg_run_length < 3 else "systematic"

        report["columns"][col] = {
            "n_missing": int(n_missing),
            "pct_missing": round(n_missing / total_rows * 100, 2),
            "pattern": pattern,
            "avg_gap_length": round(float(avg_run_length), 1),
            "suggestion": _suggest_handling(pattern, n_missing / total_rows),
        }

    return report


def _suggest_handling(pattern: str, pct: float) -> str:
    """Suggest missing data handling based on pattern and percentage."""
    if pct > 0.5:
        return "DROP column (>50% missing)"
    if pattern == "systematic":
        return "INVESTIGATE source — systematic gaps suggest data feed issues"
    if pct < 0.05:
        return "FFILL for time series, MEDIAN for cross-section"
    return "FFILL for time series (NEVER bfill per Q001)"


def main():
    parser = argparse.ArgumentParser(description="Missing Data Detector")
    parser.add_argument("file", help="CSV file to analyze")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.file, parse_dates=True)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = detect_missing_patterns(df)

    print(f"Missing Data Report ({report['total_rows']} rows)\n")
    for col, info in report["columns"].items():
        print(f"  {col}: {info['n_missing']} ({info['pct_missing']}%) — {info['pattern']}")
        print(f"    Suggestion: {info['suggestion']}")


if __name__ == "__main__":
    main()
