---
name: ml-model-training
description: Standardized ML model training workflow for quant finance
user_invocable: true
instructions_for_claude: |
  When the user invokes /ml-model-training:
  1. Search knowledge for relevant ML pitfalls: search_knowledge("model training", "engineering")
  2. Check rules: get_rules("L2") for time-series specific constraints
  3. Ensure purged cross-validation is used (no information leakage)
  4. Validate feature engineering against lookahead rules
  5. Track experiment with proper logging
---

# ML Model Training Skill

Guides ML model training with quant-finance-specific safeguards.

## Key Safeguards
- **Purged Cross-Validation**: Never use standard k-fold on time series
- **Feature Leakage**: Check all features against lookahead bias rules
- **Overfitting**: Monitor IS vs OOS performance gap
- **Label Definition**: Ensure labels use proper forward returns with shift

## Steps
1. Define target variable and horizon
2. Engineer features (check for lookahead)
3. Split data with temporal purging
4. Train model with hyperparameter search
5. Evaluate OOS performance
6. Generate experiment report
