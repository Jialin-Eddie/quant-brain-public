"""Quant Linter — Scan Python code for quantitative finance anti-patterns.

Loads rules from rules/ YAML files and checks Python source code against them.
Can be invoked as a standalone tool or through the MCP server.

Usage:
    python tools/quant_linter/quant_linter.py <file_path> [--level L1,L2,L3]
"""

import argparse
import re
import sys
from pathlib import Path

from rule_engine import RuleEngine


def lint_file(file_path: str, levels: list[str] | None = None) -> list[dict]:
    """Lint a Python file against quant rules.

    Args:
        file_path: Path to the Python file to check
        levels: Rule levels to check (e.g. ["L1", "L2"]). None = all levels.

    Returns:
        List of violations found.
    """
    path = Path(file_path)
    if not path.exists():
        return [{"error": f"File not found: {file_path}"}]

    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()

    engine = RuleEngine()
    rules = engine.load_rules(levels)

    violations = []
    for rule in rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue

        try:
            regex = re.compile(pattern)
        except re.error:
            continue

        for i, line in enumerate(lines, start=1):
            # Skip excluded patterns
            excludes = rule.get("exclude_patterns", [])
            if any(ex in line for ex in excludes):
                continue

            if regex.search(line):
                violations.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "severity": rule.get("severity", "medium"),
                    "line": i,
                    "code": line.strip(),
                    "message": rule["description"],
                    "fix": rule.get("fix", ""),
                    "reference": rule.get("reference", ""),
                })

    return violations


def format_report(violations: list[dict], file_path: str) -> str:
    """Format violations into a readable report."""
    if not violations:
        return f"  {file_path}: No violations found."

    lines = [f"  {file_path}: {len(violations)} violation(s)\n"]

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    violations.sort(key=lambda v: severity_order.get(v["severity"], 99))

    for v in violations:
        lines.append(f"    L{v['line']} [{v['severity'].upper()}] {v['rule_id']}: {v['message']}")
        lines.append(f"      Code: {v['code']}")
        if v["fix"]:
            lines.append(f"      Fix:  {v['fix']}")
        if v["reference"]:
            lines.append(f"      Ref:  {v['reference']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Quant Linter")
    parser.add_argument("file", help="Python file to lint")
    parser.add_argument("--level", default="L1,L2,L3", help="Rule levels (comma-separated)")
    args = parser.parse_args()

    levels = [l.strip().upper() for l in args.level.split(",")]
    violations = lint_file(args.file, levels)
    report = format_report(violations, args.file)
    print(report)

    # Exit code: 1 if critical/high violations found
    critical = [v for v in violations if v.get("severity") in ("critical", "high")]
    sys.exit(1 if critical else 0)


if __name__ == "__main__":
    main()
