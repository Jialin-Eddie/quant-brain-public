"""Example: Proper Error Handling in Python

Demonstrates correct patterns for exception handling,
avoiding common pitfalls documented in knowledge/engineering/.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


# ── BAD: Bare except swallows all errors ─────────────────

def bad_error_handling():
    try:
        result = 1 / 0
    except:  # noqa: E722 — NEVER do this
        pass  # Bug silently swallowed


# ── GOOD: Specific exceptions with proper logging ─────────

def good_error_handling(divisor: float) -> float | None:
    """Divide with proper error handling."""
    try:
        return 1.0 / divisor
    except ZeroDivisionError:
        logger.warning("Division by zero attempted with divisor=%s", divisor)
        return None
    except TypeError as e:
        logger.error("Invalid type for divisor: %s", e)
        raise


# ── GOOD: Async exception handling with TaskGroup ─────────

async def fetch_data(url: str) -> dict:
    """Simulated async data fetch."""
    if "bad" in url:
        raise ConnectionError(f"Failed to connect to {url}")
    return {"url": url, "data": "ok"}


async def good_async_handling():
    """Use TaskGroup to properly propagate async exceptions."""
    urls = ["https://api.example.com/data", "https://api.example.com/prices"]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_data(url)) for url in urls]

    # All exceptions propagate here — nothing is silently lost
    return [t.result() for t in tasks]


# ── GOOD: Context manager for resource cleanup ───────────

class DataConnection:
    """Example resource that needs cleanup."""

    def __init__(self, source: str):
        self.source = source
        self._conn = None

    def __enter__(self):
        logger.info("Connecting to %s", self.source)
        self._conn = f"connection:{self.source}"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing connection to %s", self.source)
        self._conn = None
        return False  # Don't suppress exceptions

    def query(self, sql: str) -> list:
        if self._conn is None:
            raise RuntimeError("Not connected")
        return [{"result": "data"}]


def good_resource_usage():
    """Always use context managers for resource cleanup."""
    with DataConnection("wind_db") as conn:
        data = conn.query("SELECT * FROM stocks")
    # Connection is always closed, even if query raises


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Demo proper error handling
    result = good_error_handling(0)
    print(f"Result with zero divisor: {result}")

    result = good_error_handling(2)
    print(f"Result with valid divisor: {result}")

    # Demo resource management
    good_resource_usage()
