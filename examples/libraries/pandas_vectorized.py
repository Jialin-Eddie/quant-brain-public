"""Example: Pandas Vectorized Operations vs Anti-Patterns

Demonstrates why vectorized operations should replace .apply() and .iterrows(),
as documented in rules/L3_libraries.yaml (LIB001, LIB002).
"""

import time

import numpy as np
import pandas as pd


def demo_apply_vs_vectorized():
    """Show performance difference between apply and vectorized operations."""
    n = 100_000
    df = pd.DataFrame({
        "price": np.random.uniform(10, 200, n),
        "quantity": np.random.randint(1, 1000, n),
        "discount": np.random.uniform(0, 0.3, n),
    })

    # BAD: Using apply (LIB001) — SLOW
    start = time.perf_counter()
    _ = df.apply(lambda row: row["price"] * row["quantity"] * (1 - row["discount"]), axis=1)
    apply_time = time.perf_counter() - start

    # GOOD: Vectorized — FAST
    start = time.perf_counter()
    _ = df["price"] * df["quantity"] * (1 - df["discount"])
    vec_time = time.perf_counter() - start

    print(f"apply():     {apply_time:.4f}s")
    print(f"vectorized:  {vec_time:.4f}s")
    print(f"speedup:     {apply_time / vec_time:.0f}x")


def demo_conditional_assignment():
    """Show np.where/np.select vs apply for conditional logic."""
    df = pd.DataFrame({"value": np.random.randn(10000)})

    # BAD: apply for conditional
    _ = df["value"].apply(lambda x: "high" if x > 1 else ("low" if x < -1 else "mid"))

    # GOOD: np.select for multiple conditions
    conditions = [df["value"] > 1, df["value"] < -1]
    choices = ["high", "low"]
    _ = np.select(conditions, choices, default="mid")


if __name__ == "__main__":
    demo_apply_vs_vectorized()
