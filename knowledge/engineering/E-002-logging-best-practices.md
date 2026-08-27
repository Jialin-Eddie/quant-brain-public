---
id: E-002
domain: engineering
title: "Logging: Use logging Module, Never print() in Library Code"
summary: "Use this when setting up any Python script or library to choose correct logging patterns and avoid print() for production observability."
tags: [logging, debugging, observability, print, engineering]
keywords: [print statement, logging module, logger, debug, structured logging, log level, basicConfig]
aliases: ["print vs logging", "logging setup", "no print in library"]
triggers: [logging setup, print statement, debug output, observability, logger, library code]
severity: medium
date_created: 2026-03-14
source_project: general
transferable: true
---

## Problem
Insufficient or poorly structured logging makes it extremely difficult to debug production issues and reproduce research results. Silent failures are common when exceptions are swallowed without logging.

## Root Cause
- Using `print()` instead of `logging` module (no severity levels, no timestamps)
- Logging only at ERROR level — missing the context trail
- Not logging function inputs/outputs for critical computation steps
- No structured format — hard to grep or parse logs programmatically

## Solution
```python
import logging

# Module-level logger — use __name__ for auto-hierarchy
logger = logging.getLogger(__name__)

# Configure at entry point (main.py or notebook setup cell), NOT in library modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Log at appropriate levels
logger.debug("Factor values: %s", factor.describe())   # Dev detail
logger.info("Processing %d stocks for date %s", n, date)  # Progress
logger.warning("Missing data for %d tickers — filling with 0", n_missing)
logger.error("Failed to load prices for %s: %s", ticker, e)
```

## Prevention
- Never use `print()` in library code — always `logger.info/debug`
- Log at the START of any long-running operation with key parameters
- Log exceptions with full traceback: `logger.exception("msg")` inside except blocks
- Add structured fields for downstream parsing: `logger.info("sharpe=%.3f n_days=%d", sharpe, n)`

## Related
- knowledge/engineering/E-001-async-exception-handling.md — proper exception handling patterns
- rules/L1_engineering.yaml — E002 no-print-debugging rule
