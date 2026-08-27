"""Quant-Brain MCP Server.

A knowledge library for managing lessons learned, bugs, and best practices
across quantitative finance projects.

Permission model:
  - Claude can READ all layers (knowledge, templates, workflows, prompts, examples, rules)
  - Claude can only SUGGEST new knowledge (writes to pending/)
  - Human approves/rejects suggestions manually
"""

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models import LayerType, Suggestion
from search import SearchEngine
from storage import KnowledgeStore

# ── Initialize ──────────────────────────────────────────────

mcp = FastMCP(
    "quant-brain",
    instructions="Quantitative finance knowledge library. "
    "Search lessons learned, avoid known pitfalls, and follow best practices.",
)

store = KnowledgeStore(PROJECT_ROOT)
search_engine = SearchEngine(store)


# ══════════════════════════════════════════════════════════════
# READ-ONLY TOOLS — Claude can auto-call these
# ══════════════════════════════════════════════════════════════


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def search_knowledge(query: str, domain: Optional[str] = None, tags: Optional[str] = None, max_results: int = 10) -> str:
    """Search the knowledge library for relevant lessons, bugs, and best practices.

    Call this BEFORE starting any task to check for known pitfalls in the domain.
    Returns matching knowledge entries ranked by relevance.

    Args:
        query: Keyword or phrase to search for (e.g. "lookahead bias", "neutralization")
        domain: Limit search scope (e.g. "quant/alpha", "quant/backtest", "engineering")
        tags: Comma-separated tags to filter by (e.g. "pandas,performance")
        max_results: Maximum number of results to return (default: 10)
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    results = search_engine.search(query, domain, tag_list)
    results = results[:max_results]

    if not results:
        return f"No knowledge found for '{query}'" + (f" in domain '{domain}'" if domain else "") + \
               ". Consider suggesting this as a new knowledge entry after the task."

    lines = [f"Found {len(results)} result(s):\n"]
    for r in results:
        e = r.entry
        lines.append(f"  [{e.severity.value.upper()}] {e.title}")
        lines.append(f"    Domain: {e.domain} | Tags: {', '.join(e.tags)}")
        lines.append(f"    File: knowledge/{e.file_path}")
        if e.summary:
            lines.append(f"    Summary: {e.summary}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_knowledge(path: str) -> str:
    """Read a specific knowledge entry by its file path.

    Use this after search_knowledge() to read the full details of a relevant entry.

    Args:
        path: Relative path within knowledge/, e.g. "quant/backtest/lookahead-bias.md"
    """
    content = store.get_entry(path)
    if content is None:
        return f"Knowledge file not found: {path}"
    return content


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def list_knowledge(domain: str, limit: int = 50, offset: int = 0) -> str:
    """List all knowledge entries in a domain.

    Use this to discover what lessons exist for a given area before starting work.

    Args:
        domain: Domain path, e.g. "quant/alpha", "engineering", "libraries"
        limit: Max entries to return (default: 50)
        offset: Skip first N entries for pagination (default: 0)
    """
    entries = store.list_domain(domain)
    if not entries:
        return f"No knowledge entries in domain '{domain}'."

    total = len(entries)
    page = entries[offset: offset + limit]

    lines = [f"Knowledge entries in '{domain}' ({total} total, showing {offset + 1}–{offset + len(page)}):\n"]
    for e in page:
        lines.append(f"  - [{e.severity.value}] {e.title} (knowledge/{e.file_path})")
        if e.summary:
            lines.append(f"    {e.summary}")
    if offset + limit < total:
        lines.append(f"\nShowing {offset + 1}–{offset + len(page)} of {total}. Use offset={offset + limit} for next page.")
    return "\n".join(lines)


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_template(domain: str, name: str) -> str:
    """Get a template file for generating standardized outputs.

    Templates mirror the knowledge directory structure.

    Args:
        domain: Domain path, e.g. "quant/alpha", "engineering"
        name: Template name without extension, e.g. "alpha_research", "bug_report"
    """
    content = store.get_resource("templates", domain, name)
    if content is None:
        available = store.list_resources("templates", domain)
        return f"Template '{name}' not found in '{domain}'. Available: {available}"
    return content


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_workflow(domain: str, name: str) -> str:
    """Get a workflow definition (YAML) for executing a standardized process.

    Workflows define step-by-step procedures for common tasks.

    Args:
        domain: Domain path, e.g. "quant/alpha", "engineering"
        name: Workflow name without extension, e.g. "factor_mining", "debugging_pipeline"
    """
    content = store.get_resource("workflows", domain, name)
    if content is None:
        available = store.list_resources("workflows", domain)
        return f"Workflow '{name}' not found in '{domain}'. Available: {available}"
    return content


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_example(domain: str, name: str) -> str:
    """Get an example file showing best-practice code for a given domain.

    Examples demonstrate the correct way to implement common patterns.

    Args:
        domain: Domain path, e.g. "quant/alpha", "engineering"
        name: Example name, e.g. "factor_ic_analysis", "proper_error_handling"
    """
    content = store.get_resource("examples", domain, name)
    if content is None:
        available = store.list_resources("examples", domain)
        return f"Example '{name}' not found in '{domain}'. Available: {available}"
    return content


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_prompt(domain: str, name: str) -> str:
    """Get a prompt template for standardized AI interactions.

    Prompts ensure consistent, high-quality AI outputs for specific task types.

    Args:
        domain: Domain path, e.g. "quant/alpha", "engineering"
        name: Prompt name, e.g. "research_factor", "debug_this"
    """
    content = store.get_resource("prompts", domain, name)
    if content is None:
        available = store.list_resources("prompts", domain)
        return f"Prompt '{name}' not found in '{domain}'. Available: {available}"
    return content


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def get_rules(level: str) -> str:
    """Get linting/checking rules by level.

    Levels:
      L1 = engineering (general coding rules)
      L2 = quant (quantitative finance specific)
      L3 = libraries (third-party library pitfalls)
      L4 = projects (project-specific constraints)

    Args:
        level: Rule level, one of "L1", "L2", "L3", "L4"
    """
    level = level.upper()
    valid = {"L1": "L1_engineering", "L2": "L2_quant", "L3": "L3_libraries", "L4": "L4_projects"}
    if level not in valid:
        return f"Invalid level '{level}'. Use one of: {list(valid.keys())}"

    rules_path = PROJECT_ROOT / "rules" / f"{valid[level]}.yaml"
    if not rules_path.exists():
        return f"Rules file not found: {rules_path.name}"
    return rules_path.read_text(encoding="utf-8")


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def list_resources(layer: str, domain: Optional[str] = None, limit: int = 50, offset: int = 0) -> str:
    """List available resources in any layer.

    Args:
        layer: One of "knowledge", "templates", "workflows", "prompts", "examples"
        domain: Optional domain filter, e.g. "quant/alpha"
        limit: Max entries to return (default: 50)
        offset: Skip first N entries for pagination (default: 0)
    """
    valid_layers = ["knowledge", "templates", "workflows", "prompts", "examples"]
    if layer not in valid_layers:
        return f"Invalid layer '{layer}'. Use one of: {valid_layers}"

    if layer == "knowledge":
        store._ensure_loaded()
        entries = store.list_domain(domain) if domain else store._index
        total = len(entries)
        page = entries[offset: offset + limit]
        lines = [f"  - {e.file_path}" for e in page]
        result = "\n".join(lines) or "No entries found."
        if offset + limit < total:
            result += f"\nShowing {offset + 1}–{offset + len(page)} of {total}. Use offset={offset + limit} for next page."
        return result

    files = store.list_resources(layer, domain)
    if not files:
        return f"No resources in {layer}/{domain or ''}."
    total = len(files)
    page = files[offset: offset + limit]
    result = "\n".join(f"  - {f}" for f in page)
    if offset + limit < total:
        result += f"\nShowing {offset + 1}–{offset + len(page)} of {total}. Use offset={offset + limit} for next page."
    return result


# ══════════════════════════════════════════════════════════════
# SUGGEST-ONLY TOOLS — writes to pending/, not knowledge/
# ══════════════════════════════════════════════════════════════


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_knowledge(domain: str, title: str, content: str, reason: str, tags: Optional[str] = None) -> str:
    """Suggest a new knowledge entry for human review.

    This does NOT write to knowledge/ directly. It creates a pending entry
    that the human must approve before it becomes part of the library.

    Call this when you discover a new pitfall, bug pattern, or best practice
    during a task that would be valuable for future work.

    Args:
        domain: Where this belongs, e.g. "quant/alpha", "engineering"
        title: Short descriptive title
        content: Full markdown content (Problem, Root Cause, Solution, Prevention)
        reason: Why this should be added to the knowledge library
        tags: Comma-separated tags, e.g. "pandas,performance,gotcha"
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    suggestion = Suggestion(
        domain=domain,
        title=title,
        content=content,
        reason=reason,
        suggested_tags=tag_list,
    )

    file_path = store.write_pending(suggestion)
    return (
        f"Suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"The human can review and move it to knowledge/{domain}/ when ready."
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_workflow(domain: str, name: str, content: str, reason: str) -> str:
    """Suggest a new workflow YAML for human review.

    Writes to pending/workflows/<domain>/<name>.yaml — NOT to workflows/ directly.
    Use this when you identify a reusable step-by-step process worth formalizing.

    Args:
        domain: e.g. "quant/alpha", "engineering"
        name: filename without extension, e.g. "factor-research-workflow"
        content: full YAML content for the workflow
        reason: why this workflow should be added
    """
    file_path = store.write_pending_resource("workflows", domain, name, content, reason)
    return (
        f"Workflow suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"The human can review and move it to workflows/{domain}/ when ready."
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_template(domain: str, name: str, content: str, reason: str) -> str:
    """Suggest a new template for human review.

    Writes to pending/templates/<domain>/<name>.md — NOT to templates/ directly.
    Use this when you have a reusable report or code template worth saving.

    Args:
        domain: e.g. "quant/alpha", "engineering"
        name: filename without extension, e.g. "alpha-research-report"
        content: full markdown content for the template
        reason: why this template should be added
    """
    file_path = store.write_pending_resource("templates", domain, name, content, reason)
    return (
        f"Template suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"The human can review and move it to templates/{domain}/ when ready."
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_prompt(domain: str, name: str, content: str, reason: str) -> str:
    """Suggest a new prompt template for human review.

    Writes to pending/prompts/<domain>/<name>.md — NOT to prompts/ directly.
    Use this when you craft a prompt that produces reliably good results.

    Args:
        domain: e.g. "quant/alpha", "engineering"
        name: filename without extension, e.g. "factor-critique-prompt"
        content: full markdown content for the prompt
        reason: why this prompt should be added
    """
    file_path = store.write_pending_resource("prompts", domain, name, content, reason)
    return (
        f"Prompt suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"The human can review and move it to prompts/{domain}/ when ready."
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_example(domain: str, name: str, content: str, reason: str) -> str:
    """Suggest a new best-practice example for human review.

    Writes to pending/examples/<domain>/<name>.md — NOT to examples/ directly.
    Use this when you write code that demonstrates a pattern worth preserving.

    Args:
        domain: e.g. "quant/alpha", "engineering"
        name: filename without extension, e.g. "vectorized-signal-compute"
        content: full markdown/code content for the example
        reason: why this example should be added
    """
    file_path = store.write_pending_resource("examples", domain, name, content, reason)
    return (
        f"Example suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"The human can review and move it to examples/{domain}/ when ready."
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest(
    title: str,
    content: str,
    reason: str,
    layer_type: str = "knowledge",
    domain: Optional[str] = None,
    classification_reasoning: Optional[str] = None,
    domain_alternatives: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """Suggest a new knowledge entry with pre-classification metadata. PREFERRED over suggest_knowledge().

    Pre-classify the suggestion by providing domain, layer_type, and your reasoning.
    If domain is uncertain, pass domain=None — the entry goes to pending/unclassified/ inbox.

    Layer type heuristics:
      knowledge  — incident-based gotcha/pitfall (Problem/Solution/Prevention)
      workflow   — repeatable multi-step process (YAML)
      template   — fill-in-the-blank document structure
      prompt     — structured LLM instruction template
      example    — working code demonstrating a pattern

    Valid domains: engineering, claude-code, libraries, quant/alpha, quant/backtest,
                   quant/data_process, projects. Use None if uncertain.

    Args:
        title: Short descriptive title
        content: Full markdown content of the entry
        reason: Why this should be added to the library
        layer_type: One of knowledge/workflow/template/prompt/example (default: knowledge)
        domain: Target domain path, or None to route to unclassified inbox
        classification_reasoning: Why you chose this domain+layer (shown during audit)
        domain_alternatives: Comma-separated alternative domains if uncertain
        tags: Comma-separated tags, e.g. "pandas,performance,gotcha"
    """
    try:
        layer = LayerType(layer_type)
    except ValueError:
        valid = [lt.value for lt in LayerType]
        return f"Invalid layer_type '{layer_type}'. Use one of: {valid}"

    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    alt_list = [d.strip() for d in domain_alternatives.split(",")] if domain_alternatives else []

    suggestion = Suggestion(
        domain=domain,
        title=title,
        content=content,
        reason=reason,
        layer_type=layer,
        classification_reasoning=classification_reasoning or "",
        domain_alternatives=alt_list,
        suggested_tags=tag_list,
    )

    file_path = store.write_pending_unified(suggestion)
    location = f"pending/unclassified/" if domain is None else f"pending/{domain}/"
    confidence = "LOW (unclassified inbox)" if domain is None else "CLASSIFIED"
    return (
        f"Suggestion saved to {file_path}\n"
        f"Status: PENDING — awaiting human approval.\n"
        f"Layer: {layer.value} | Domain: {domain or 'unclassified'} | Confidence: {confidence}\n"
        f"Location: {location}"
    )


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def classify_pending(
    file_path: str,
    new_domain: str,
    new_layer_type: Optional[str] = None,
    reason: str = "",
) -> str:
    """Reclassify a pending entry — move it to a new domain/layer within pending/.

    Use this during audit to correct Claude's classification of a pending suggestion.
    The file is moved within pending/ and frontmatter updated with human_classified=true.

    Args:
        file_path: Relative path from project root, e.g. "pending/unclassified/my-entry.md"
        new_domain: Target domain, e.g. "quant/backtest", "engineering"
        new_layer_type: One of knowledge/workflow/template/prompt/example (keeps existing if omitted)
        reason: Why you chose this classification
    """
    try:
        new_path = store.reclassify_pending(file_path, new_domain, new_layer_type, reason)
        return (
            f"Reclassified successfully.\n"
            f"Old path: {file_path}\n"
            f"New path: {new_path}\n"
            f"Domain: {new_domain} | Layer: {new_layer_type or 'unchanged'}\n"
            f"Marked: human_classified=true"
        )
    except (FileNotFoundError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
})
def suggest_update(path: str, reason: str) -> str:
    """Suggest that an existing knowledge entry needs updating.

    This does NOT modify the file. It creates a note in pending/ for human review.

    Args:
        path: Path to the knowledge file, e.g. "quant/backtest/lookahead-bias.md"
        reason: Why this entry should be updated (new findings, corrections, etc.)
    """
    suggestion = Suggestion(
        domain="updates",
        title=f"Update: {path}",
        content=f"Suggested update for: knowledge/{path}\n\nReason: {reason}",
        reason=reason,
    )

    file_path = store.write_pending(suggestion)
    return (
        f"Update suggestion saved to {file_path}\n"
        f"Status: PENDING — the human will review and apply changes manually."
    )


@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
def list_pending(domain: Optional[str] = None, unclassified_only: bool = False) -> str:
    """List all pending suggestions awaiting human approval.

    Shows UNCLASSIFIED entries first (need routing), then CLASSIFIED entries.
    Includes layer_type, classification_reasoning, and domain_alternatives for audit.

    Args:
        domain: Optional domain filter, e.g. "engineering", "claude-code"
        unclassified_only: If True, show only entries in pending/unclassified/
    """
    pending = store.list_pending(unclassified_only=unclassified_only)
    if domain:
        pending = [p for p in pending if (p.get("domain") or "").startswith(domain)]
    if not pending:
        msg = "No pending suggestions"
        if unclassified_only:
            msg += " in unclassified inbox"
        elif domain:
            msg += f" in domain '{domain}'"
        return msg + "."

    unclassified = [p for p in pending if not p.get("domain") or "unclassified" in p.get("file", "")]
    classified = [p for p in pending if p not in unclassified]

    lines = [f"Pending suggestions ({len(pending)} total):\n"]

    if unclassified:
        lines.append(f"━━ UNCLASSIFIED ({len(unclassified)} — needs routing) ━━\n")
        for p in unclassified:
            lines.append(f"  [{p.get('layer_type', 'knowledge')}] {p.get('title', '?')}")
            lines.append(f"    File: {p.get('file', '?')}")
            reasoning = p.get("classification_reasoning", "")
            if reasoning:
                lines.append(f"    Reasoning: {reasoning[:120]}{'…' if len(reasoning) > 120 else ''}")
            alts = p.get("domain_alternatives", [])
            if alts:
                lines.append(f"    Alternatives: {', '.join(alts)}")
            if p.get("reason"):
                lines.append(f"    Reason: {p['reason']}")
            lines.append("")

    if classified and not unclassified_only:
        lines.append(f"━━ CLASSIFIED ({len(classified)}) ━━\n")
        for p in classified:
            human = " [human-classified]" if p.get("human_classified") else ""
            lines.append(f"  [{p.get('layer_type', 'knowledge')}] {p.get('title', '?')}{human}")
            lines.append(f"    Domain: {p.get('domain', '?')} | File: {p.get('file', '?')}")
            reasoning = p.get("classification_reasoning", "")
            if reasoning:
                lines.append(f"    Reasoning: {reasoning[:120]}{'…' if len(reasoning) > 120 else ''}")
            alts = p.get("domain_alternatives", [])
            if alts:
                lines.append(f"    Alternatives: {', '.join(alts)}")
            if p.get("reason"):
                lines.append(f"    Reason: {p['reason']}")
            lines.append("")

    return "\n".join(lines)


# ── Entry point ─────────────────────────────────────────────

def main():
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
