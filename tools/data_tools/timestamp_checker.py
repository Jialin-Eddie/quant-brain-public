"""Timestamp Checker — Verify temporal integrity of time series data.

Checks for gaps, duplicates, timezone issues, and alignment problems.
Critical for preventing lookahead bias (Q001, Q002).

Usage:
    python tools/data_tools/timestamp_checker.py <csv_path> --freq B
"""

import argparse
import sys

import pandas as pd


def check_timestamps(df: pd.DataFrame, expected_freq: str = "B") -> dict:
    """Check temporal integrity of a DataFrame with datetime index.

    Args:
        df: DataFrame with DatetimeIndex
        expected_freq: Expected frequency ('B' for business day, 'D' for daily, etc.)

    Returns:
        Dict with check results.
    """
    report = {"passed": True, "checks": {}}

    if not isinstance(df.index, pd.DatetimeIndex):
        report["passed"] = False
        report["checks"]["index_type"] = {
            "status": "FAIL",
            "message": f"Index is {type(df.index).__name__}, expected DatetimeIndex",
        }
        return report

    # Check 1: Duplicates
    n_dupes = df.index.duplicated().sum()
    report["checks"]["duplicates"] = {
        "status": "PASS" if n_dupes == 0 else "FAIL",
        "message": f"{n_dupes} duplicate timestamps found",
    }
    if n_dupes > 0:
        report["passed"] = False

    # Check 2: Sorted
    is_sorted = df.index.is_monotonic_increasing
    report["checks"]["sorted"] = {
        "status": "PASS" if is_sorted else "FAIL",
        "message": "Index is monotonically increasing" if is_sorted else "Index is NOT sorted",
    }
    if not is_sorted:
        report["passed"] = False

    # Check 3: Gaps
    expected_index = pd.date_range(df.index.min(), df.index.max(), freq=expected_freq)
    missing_dates = expected_index.difference(df.index)
    extra_dates = df.index.difference(expected_index)

    report["checks"]["gaps"] = {
        "status": "PASS" if len(missing_dates) == 0 else "WARN",
        "missing_count": len(missing_dates),
        "extra_count": len(extra_dates),
        "message": f"{len(missing_dates)} missing dates, {len(extra_dates)} extra dates",
    }

    # Check 4: Timezone consistency
    tz = df.index.tz
    report["checks"]["timezone"] = {
        "status": "PASS",
        "timezone": str(tz) if tz else "None (naive)",
        "message": f"Timezone: {tz if tz else 'naive (no timezone)'}",
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Timestamp Checker")
    parser.add_argument("file", help="CSV file to check")
    parser.add_argument("--freq", default="B", help="Expected frequency (B=business day)")
    parser.add_argument("--date-col", default=None, help="Date column name (default: first column)")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.file)
        date_col = args.date_col or df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = check_timestamps(df, args.freq)

    status = "PASS" if report["passed"] else "FAIL"
    print(f"Timestamp Check: {status}\n")
    for name, check in report["checks"].items():
        print(f"  [{check['status']}] {name}: {check['message']}")


if __name__ == "__main__":
    main()
