"""Data Inspector — Quick overview of dataset quality and statistics.

Usage:
    python tools/data_tools/data_inspector.py <csv_path>
"""

import argparse
import sys

import numpy as np
import pandas as pd


def inspect_dataframe(df: pd.DataFrame) -> dict:
    """Generate a comprehensive data quality report.

    Returns:
        Dict with shape, dtypes, missing, outliers, and basic stats.
    """
    report = {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": {},
        "outliers": {},
        "stats": {},
    }

    for col in df.columns:
        # Missing data
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            report["missing"][col] = {
                "count": int(n_missing),
                "pct": round(n_missing / len(df) * 100, 2),
            }

        # Numeric columns: outliers and stats
        if pd.api.types.is_numeric_dtype(df[col]):
            series = df[col].dropna()
            if len(series) == 0:
                continue

            mean = series.mean()
            std = series.std()
            if std > 0:
                z_scores = ((series - mean) / std).abs()
                n_outliers = int((z_scores > 3).sum())
                if n_outliers > 0:
                    report["outliers"][col] = {
                        "count": n_outliers,
                        "pct": round(n_outliers / len(series) * 100, 2),
                    }

            report["stats"][col] = {
                "mean": round(float(mean), 6),
                "std": round(float(std), 6),
                "min": round(float(series.min()), 6),
                "max": round(float(series.max()), 6),
                "skew": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
            }

    return report


def format_report(report: dict) -> str:
    """Format inspection report as readable text."""
    lines = ["=== Data Inspection Report ===\n"]

    lines.append(f"Shape: {report['shape']['rows']} rows x {report['shape']['columns']} columns\n")

    if report["missing"]:
        lines.append("Missing Data:")
        for col, info in report["missing"].items():
            lines.append(f"  {col}: {info['count']} ({info['pct']}%)")
        lines.append("")

    if report["outliers"]:
        lines.append("Outliers (>3 sigma):")
        for col, info in report["outliers"].items():
            lines.append(f"  {col}: {info['count']} ({info['pct']}%)")
        lines.append("")

    if report["stats"]:
        lines.append("Numeric Stats:")
        for col, stats in report["stats"].items():
            lines.append(f"  {col}: mean={stats['mean']}, std={stats['std']}, "
                        f"skew={stats['skew']}, kurt={stats['kurtosis']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Data Inspector")
    parser.add_argument("file", help="CSV file to inspect")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.file, parse_dates=True)
    except Exception as e:
        print(f"Error reading {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    report = inspect_dataframe(df)
    print(format_report(report))


if __name__ == "__main__":
    main()
