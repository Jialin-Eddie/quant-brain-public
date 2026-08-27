---
id: PREFIX-NNN            # e.g. QB-002 — must match filename prefix+number
domain: quant/backtest    # folder path under knowledge/
title: "Domain: Core Issue in 5–8 Words"
summary: "One sentence describing the problem and consequence — used by search ranking."
tags: [tag1, tag2, tag3]                   # 3–6 lowercase keywords from the content
keywords: [synonym1, alternate-term, jargon]  # extra terms AI might search with
aliases: ["short name", "alternate title"]    # what someone might call this informally
triggers: [task keyword, scenario, code pattern]  # when Claude should proactively retrieve this
severity: high            # low | medium | high | critical
date_created: YYYY-MM-DD
source_project: project-name-where-discovered
transferable: true        # true = applies beyond source project; false = project-specific
---

## Problem
<!-- What goes wrong? Describe the observable symptom, not the cause. -->

## Root Cause
<!-- Why does it happen? Enumerate specific patterns or mechanisms. -->

## Solution
```python
# BAD — describe what the wrong pattern looks like
wrong_code()

# GOOD — correct replacement
correct_code()
```

## Prevention
<!-- Rules, assertions, checklist items, or linter hooks to prevent recurrence. -->
- **Rule**: ...
- **Check**: ...
- **Tool**: ...

## Related
<!-- Link to related knowledge entries, rules, or external references. -->
- knowledge/...
- rules/...
