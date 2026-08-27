---
name: factor-research
description: Guide factor research from hypothesis to IC analysis
user_invocable: true
instructions_for_claude: |
  When the user invokes /factor-research, follow these steps:
  1. Search knowledge: search_knowledge("factor", "quant/alpha")
  2. Load workflow: get_workflow("quant/alpha", "factor_mining")
  3. Load template: get_template("quant/alpha", "alpha_research")
  4. Load example: get_example("quant/alpha", "factor_ic_analysis")
  5. Load rules: get_rules("L2") for quant pitfalls
  6. Guide the user through hypothesis → data → signal → IC test → report
  7. Validate neutralization approach against knowledge
---

# Factor Research Skill

This skill provides a structured workflow for researching new alpha factors.

## Steps
1. **Define Hypothesis** — What market inefficiency are we capturing?
2. **Prepare Data** — Load, clean, align timestamps
3. **Compute Factor** — Implement the factor with proper handling
4. **Neutralize** — Industry/market-cap neutralization (check pitfalls)
5. **IC Analysis** — Rank IC, IC_IR, decay analysis
6. **Group Returns** — Quintile portfolio analysis
7. **Report** — Generate structured research report

## References
- knowledge/quant/alpha/neutralization-pitfalls.md
- rules/L2_quant.yaml (Q003, Q004)
