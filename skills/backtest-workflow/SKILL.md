---
name: backtest-workflow
description: Run a standardized backtesting workflow — from signal generation to performance report
user_invocable: true
instructions_for_claude: |
  When the user invokes /backtest-workflow, follow these steps:
  1. Search knowledge for relevant backtest pitfalls: search_knowledge("backtest", "quant/backtest")
  2. Load the backtest workflow: get_workflow("quant/backtest", "backtest_pipeline")
  3. Load the backtest report template: get_template("quant/backtest", "backtest_report")
  4. Load rules: get_rules("L2") to check for quant-specific pitfalls
  5. Execute each step, validating against rules at each stage
  6. Generate report using the template
  7. If new pitfalls discovered, suggest_knowledge() for human review
---

# Backtest Workflow Skill

This skill guides Claude through a standardized backtesting process.

## Steps
1. **Load Knowledge** — Check known backtest pitfalls
2. **Validate Data** — Run timestamp checker, check for lookahead bias
3. **Generate Signals** — Apply signal logic with proper shift(1)
4. **Run Backtest** — Execute backtest with transaction costs
5. **Validate Results** — Check for suspiciously high Sharpe, verify no lookahead
6. **Generate Report** — Use backtest_report template

## References
- knowledge/quant/backtest/lookahead-bias.md
- rules/L2_quant.yaml (Q001, Q002, Q006)
