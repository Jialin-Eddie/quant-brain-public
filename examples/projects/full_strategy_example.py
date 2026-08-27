"""Example: Full Strategy Implementation (Skeleton)

Shows the correct structure for implementing a trading strategy,
following all knowledge library rules and best practices.
"""

import numpy as np
import pandas as pd


class MomentumStrategy:
    """Simple momentum strategy with proper safeguards.

    Rules applied:
    - Q001: No bfill
    - Q002: Signal shifted by lag period
    - Q003: Winsorize before neutralization
    - Q006: Transaction costs included
    """

    def __init__(
        self,
        lookback: int = 20,
        n_groups: int = 5,
        cost_bps: float = 10.0,
        lag: int = 1,
    ):
        self.lookback = lookback
        self.n_groups = n_groups
        self.cost_bps = cost_bps
        self.lag = lag

        if lag < 1:
            raise ValueError("lag must be >= 1 (Q002: prevent lookahead bias)")

    def compute_signal(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Compute momentum signal (past N-day return)."""
        signal = prices.pct_change(self.lookback)

        # Winsorize cross-sectionally (Q003)
        signal = signal.apply(
            lambda row: row.clip(
                lower=row.quantile(0.01),
                upper=row.quantile(0.99),
            ),
            axis=1,
        )

        # Fill missing with ffill only (Q001: NEVER bfill)
        signal = signal.ffill()
        return signal

    def generate_positions(self, signal: pd.DataFrame) -> pd.DataFrame:
        """Generate positions from signal with proper lag."""
        # CRITICAL: Shift signal by lag (Q002)
        lagged = signal.shift(self.lag)

        # Rank cross-sectionally and normalize to [-1, 1]
        ranks = lagged.rank(axis=1, pct=True)
        positions = (ranks - 0.5) * 2
        return positions

    def backtest(self, prices: pd.DataFrame) -> dict:
        """Run full backtest with transaction costs (Q006)."""
        signal = self.compute_signal(prices)
        positions = self.generate_positions(signal)
        returns = prices.pct_change()

        portfolio_ret = (positions.shift(1) * returns).sum(axis=1) / positions.shift(1).abs().sum(axis=1)

        # Transaction costs (Q006)
        turnover = (positions - positions.shift(1)).abs().sum(axis=1) / 2
        cost = turnover * self.cost_bps / 10000
        portfolio_ret_net = portfolio_ret - cost

        return {
            "gross_returns": portfolio_ret,
            "net_returns": portfolio_ret_net,
            "positions": positions,
            "turnover": turnover,
        }


if __name__ == "__main__":
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=504, freq="B")
    stocks = [f"S{i:03d}" for i in range(100)]

    prices = pd.DataFrame(
        np.exp(np.cumsum(np.random.randn(len(dates), len(stocks)) * 0.02, axis=0)) * 100,
        index=dates,
        columns=stocks,
    )

    strategy = MomentumStrategy(lookback=20, cost_bps=10, lag=1)
    result = strategy.backtest(prices)

    net = result["net_returns"].dropna()
    print(f"Ann. Return: {net.mean() * 252:.4f}")
    print(f"Ann. Vol:    {net.std() * np.sqrt(252):.4f}")
    print(f"Sharpe:      {net.mean() / net.std() * np.sqrt(252):.4f}")
    print(f"Avg Turnover:{result['turnover'].mean():.4f}")
