# Public-release boundary

## Allowed

- Generic MCP implementation, tests, documentation, templates, prompts, workflows, rules, and examples.
- Generalizable research lessons with no customer, employer, account, dataset-license, strategy, market-position, or project identifiers.

## Never commit

- Credentials, tokens, cookies, SSH keys, certificates, local MCP configuration, or environment files.
- Personal identity data, local paths, email addresses, account names, machine names, or private URLs.
- Proprietary datasets, data extracts, experiment outputs, backtests, positions, PnL, trading parameters, and strategy-specific conclusions.
- Notes or generated suggestions from private work. Keep these in `pending/`, `private/`, or `knowledge/private/`.

## Review gate

Before staging files, run `pwsh -File scripts/audit-public.ps1`. Review every new knowledge entry manually; a passing pattern scan is necessary but not sufficient to prove that research is safe to publish.
