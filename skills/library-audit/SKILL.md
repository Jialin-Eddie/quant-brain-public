---
name: library-audit
description: Audit the quant-brain knowledge library for completeness and consistency
user_invocable: true
instructions_for_claude: |
  When the user invokes /library-audit:
  1. List all knowledge domains: list_resources("knowledge")
  2. For each domain, check corresponding templates/workflows/prompts/examples exist
  3. Verify INDEX.md is up to date
  4. Check for orphaned files (files not in INDEX.md)
  5. Validate all frontmatter YAML is well-formed
  6. Report gaps and suggest additions
---

# Library Audit Skill

Self-audit tool for the quant-brain knowledge library.

## Checks
1. **Completeness**: Every knowledge entry has corresponding template/workflow/prompt/example
2. **Index Sync**: INDEX.md matches actual files
3. **Frontmatter**: All YAML frontmatter is valid and complete
4. **Cross-References**: All `reference:` and `Related` links point to existing files
5. **Coverage**: Identify domains with few entries that need attention

## Output
Generates an audit report with:
- Coverage matrix (knowledge x layer)
- Missing resources
- Broken references
- Suggested improvements
