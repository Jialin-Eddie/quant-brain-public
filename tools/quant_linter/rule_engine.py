"""Rule Engine — Loads and manages linting rules from YAML files."""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
RULES_DIR = PROJECT_ROOT / "rules"

LEVEL_FILES = {
    "L1": "L1_engineering.yaml",
    "L2": "L2_quant.yaml",
    "L3": "L3_libraries.yaml",
    "L4": "L4_projects.yaml",
}


class RuleEngine:
    """Load and filter rules from YAML files."""

    def __init__(self, rules_dir: Path | None = None):
        self.rules_dir = rules_dir or RULES_DIR

    def load_rules(self, levels: list[str] | None = None) -> list[dict]:
        """Load rules from YAML files, optionally filtered by level.

        Args:
            levels: List of levels to load (e.g. ["L1", "L2"]). None = all.

        Returns:
            List of rule dicts.
        """
        if levels is None:
            levels = list(LEVEL_FILES.keys())

        all_rules = []
        for level in levels:
            level = level.upper()
            filename = LEVEL_FILES.get(level)
            if not filename:
                continue

            filepath = self.rules_dir / filename
            if not filepath.exists():
                continue

            try:
                data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue

            rules = data.get("rules", [])
            for rule in rules:
                rule["level"] = level
            all_rules.extend(rules)

        return all_rules

    def get_rule(self, rule_id: str) -> dict | None:
        """Get a specific rule by ID."""
        all_rules = self.load_rules()
        for rule in all_rules:
            if rule.get("id") == rule_id:
                return rule
        return None
