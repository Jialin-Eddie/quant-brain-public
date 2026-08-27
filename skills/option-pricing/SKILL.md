---
name: option-pricing
description: Option pricing and Greeks calculation workflow
user_invocable: true
instructions_for_claude: |
  When the user invokes /option-pricing:
  1. Search knowledge: search_knowledge("option", "quant")
  2. Determine pricing model (Black-Scholes, Binomial, Monte Carlo)
  3. Validate inputs (spot, strike, vol, rate, time)
  4. Compute price and Greeks
  5. Run sensitivity analysis
---

# Option Pricing Skill

Guides option pricing calculations with proper validation.

## Supported Models
- Black-Scholes-Merton (European options)
- Binomial Tree (American options)
- Monte Carlo (Exotic options)

## Key Checks
- Implied vol reasonableness (0 < vol < 300%)
- Time to expiry in correct units (annualized)
- Interest rate and dividend yield consistency
- Put-call parity validation
