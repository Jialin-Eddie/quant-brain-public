# Quant-Brain MCP Server

Quant-Brain is a local MCP server that provides reusable quantitative-research and engineering knowledge, templates, workflows, and small analysis utilities to compatible MCP clients.

## What is included

- A stdio MCP server built with `FastMCP`
- Read-only retrieval for curated public knowledge and resources
- Suggestion tools that write only to a local, Git-ignored `pending/` directory
- Generic quant, engineering, and data-quality utilities

## What is deliberately not included

This public repository contains no credentials, local MCP configuration, private datasets, trading positions, backtest outputs, client material, or project-specific research. Local working material belongs in one of the Git-ignored directories: `pending/`, `private/`, or `knowledge/private/`.

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Configure your MCP client to run:

```text
python /absolute/path/to/quant-brain-public/main.py
```

## Before publishing a change

Run the release audit and review its output:

```powershell
pwsh -File scripts/audit-public.ps1
```

Read [OPEN_SOURCE_SCOPE.md](OPEN_SOURCE_SCOPE.md) before adding knowledge, examples, or workflows.

## License

A license has not yet been selected. Do not publish the repository as open source until a license is added.
