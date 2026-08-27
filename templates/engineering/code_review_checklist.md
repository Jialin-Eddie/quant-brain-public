# Code Review Checklist

**Reviewer**: {{reviewer}}
**Date**: {{date}}
**PR/Files**: {{files}}

## General
- [ ] Code follows project conventions
- [ ] No bare except clauses (E001)
- [ ] No print debugging (E002)
- [ ] No mutable default arguments (E003)
- [ ] Type hints present (E004)
- [ ] No star imports (E005)

## Testing
- [ ] Unit tests added/updated
- [ ] Edge cases covered
- [ ] Tests pass locally

## Documentation
- [ ] Docstrings updated
- [ ] README updated if needed

## Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection safe
