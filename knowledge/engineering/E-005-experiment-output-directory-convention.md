---
id: E-005
domain: engineering
title: "Project Structure: Use experiment_dir() Helper for Organized Output Folders"
summary: "Use this when writing a new experiment script to automatically create numbered output folders with README stubs instead of dumping files into a flat outputs/ directory."
tags: [engineering, project-structure, outputs, experiment-management, best-practice]
keywords: [experiment_dir, output folder, numbered folders, experiment organization, outputs directory, README stub]
aliases: ["experiment directory helper", "organized outputs", "experiment folder convention"]
triggers: [new experiment script, save output files, outputs directory, experiment results, CSV PNG output]
severity: medium
date_created: 2026-03-15
source_project: 02HW_QT
transferable: true
---

## Problem
Quant experiment scripts tend to dump all output files (CSV, PNG) directly into a flat `outputs/` folder. After 10+ experiments, the folder becomes unnavigable — no structure, no context, no way to link results back to the experiment that produced them.

## Root Cause
No convention for per-experiment output directories, leading to a flat pile of files with no metadata about which experiment produced which output.

## Solution

### 1. `experiment_dir(name)` helper in `config.py`

```python
def experiment_dir(name: str) -> Path:
    """Return outputs/NN_name/, creating it if needed.

    Auto-assigns the next available NN prefix based on existing folders.
    Creates a README.md stub if one does not already exist.
    Re-running the same script reuses the existing folder (no duplicates).
    """
    existing = sorted(
        [d for d in OUTPUTS.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )
    for d in existing:
        if d.name.split("_", 1)[-1] == name:
            d.mkdir(parents=True, exist_ok=True)
            return d
    next_num = len(existing) + 1
    folder = OUTPUTS / f"{next_num:02d}_{name}"
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {name}\n\n"
            "## Motivation\n\n"
            "## Changes\n\n"
            "## Findings\n\n"
            "## Results\n\n"
            "## Output Files\n"
        )
    return folder
```

### 2. Usage in every experiment script

```python
from config import experiment_dir

OUT = experiment_dir("normalization")   # → outputs/05_normalization/

perf_df.to_csv(OUT / "perf.csv")
fig.savefig(OUT / "equity.png")

# Fill README at end of main()
(OUT / "README.md").write_text(f"""# normalization
## Motivation
Test whether rank norm outperforms Z-score for XGBoost signal.

## Findings
Rank wins +0.06 Sharpe on Long basket.

## Results
{perf_df.to_string()}

## Output Files
- perf.csv, equity.png
""")
```

### 3. Naming convention
- `name` = lowercase with underscores, matching the script suffix
- e.g. `src/20_foo_bar.py` → `experiment_dir("foo_bar")` → `outputs/20_foo_bar/`

### 4. Resulting structure
```
outputs/
├── data/                    # pipeline intermediates (parquet, pkl)
├── 01_alpha_benchmark/
│   ├── README.md            # motivation, findings, results table
│   ├── perf.csv
│   └── equity.png
├── 02_spread_analysis/
│   ├── README.md
│   └── spread_analysis.csv
└── ...
```

## Prevention
- **Rule**: Every new experiment script MUST use `experiment_dir(name)` — never write directly to `OUTPUTS`
- **Rule**: Script must populate the README.md stub at end of `main()`
- **NOT needed for** pipeline intermediates (train/test splits, feature matrices) — those go in `data/` directly

## Related
- knowledge/engineering/E-004-no-data-files-in-git.md — what not to commit from outputs/
