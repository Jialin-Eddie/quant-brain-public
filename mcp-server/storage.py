"""Storage engine for quant-brain knowledge library.

Reads knowledge from MD files with YAML frontmatter.
Writes ONLY to pending/ directory for human approval.
"""

import json
import re
from datetime import date
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from models import KnowledgeEntry, LayerType, Suggestion, SuggestionStatus

# Project root (one level up from mcp-server/)
PROJECT_ROOT = Path(__file__).parent.parent


class KnowledgeStore:
    """Read-only access to knowledge/ directory + write to pending/."""

    def __init__(self, root: Optional[Path] = None):
        self.root = root or PROJECT_ROOT
        self.knowledge_dir = self.root / "knowledge"
        self.pending_dir = self.root / "pending"
        self._index: list[KnowledgeEntry] = []
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self.reload_index()

    def reload_index(self):
        """Scan all MD files in knowledge/ and build in-memory index."""
        self._index = []
        for md_file in self.knowledge_dir.rglob("*.md"):
            if md_file.stem.startswith("_") or md_file.name == "INDEX.md":
                continue
            entry = self._parse_frontmatter(md_file)
            if entry:
                self._index.append(entry)
        self._loaded = True

    def _parse_frontmatter(self, path: Path) -> Optional[KnowledgeEntry]:
        """Parse YAML frontmatter from a knowledge MD file."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return None

        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not match:
            return None

        try:
            meta = yaml.safe_load(match.group(1))
        except (yaml.YAMLError, Exception):
            return None

        if not isinstance(meta, dict):
            return None

        rel_path = path.relative_to(self.knowledge_dir)
        domain = str(rel_path.parent).replace("\\", "/")

        try:
            return KnowledgeEntry(
                id=meta.get("id", path.stem),
                domain=meta.get("domain", domain),
                title=meta.get("title", path.stem.replace("-", " ").title()),
                summary=meta.get("summary", ""),
                tags=meta.get("tags", []),
                severity=meta.get("severity", "medium"),
                date_created=meta.get("date_created", date.today()),
                source_project=meta.get("source_project", ""),
                transferable=meta.get("transferable", True),
                file_path=str(rel_path).replace("\\", "/"),
            )
        except (ValidationError, ValueError, Exception):
            return None

    # ── READ operations ──────────────────────────────────────

    def search(self, query: str, domain: Optional[str] = None, tags: Optional[list[str]] = None) -> list[KnowledgeEntry]:
        """Search knowledge entries by keyword, optionally filtered by domain and tags."""
        self._ensure_loaded()
        query_lower = query.lower()
        results = []

        for entry in self._index:
            # Domain filter
            if domain and not entry.domain.startswith(domain):
                continue

            # Tag filter
            if tags and not any(t in entry.tags for t in tags):
                continue

            # Keyword match in title, summary, tags, id
            searchable = f"{entry.title} {entry.summary} {' '.join(entry.tags)} {entry.id}".lower()
            if query_lower in searchable:
                results.append(entry)

        return results

    def get_entry(self, file_path: str) -> Optional[str]:
        """Read a specific knowledge file by relative path. Returns full content."""
        full_path = self.knowledge_dir / file_path
        if not full_path.exists():
            return None
        if not full_path.resolve().is_relative_to(self.knowledge_dir.resolve()):
            return None  # Security: prevent path traversal
        return full_path.read_text(encoding="utf-8")

    def list_domain(self, domain: str) -> list[KnowledgeEntry]:
        """List all knowledge entries under a domain."""
        self._ensure_loaded()
        return [e for e in self._index if e.domain.startswith(domain)]

    def list_all_domains(self) -> list[str]:
        """Return all unique domains."""
        self._ensure_loaded()
        return sorted(set(e.domain for e in self._index))

    # ── Resource reader (templates, workflows, prompts, examples) ──

    def get_resource(self, layer: str, domain: str, name: str) -> Optional[str]:
        """Read a file from templates/, workflows/, prompts/, or examples/.

        Args:
            layer: one of 'templates', 'workflows', 'prompts', 'examples'
            domain: e.g. 'quant/alpha'
            name: filename without extension for md/yaml, with extension for py
        """
        layer_dir = self.root / layer / domain

        # Try common extensions
        for ext in [".md", ".yaml", ".yml", ".py", ".ipynb", ""]:
            candidate = layer_dir / f"{name}{ext}"
            if candidate.exists():
                if not candidate.resolve().is_relative_to(self.root.resolve()):
                    return None
                return candidate.read_text(encoding="utf-8")

        return None

    def list_resources(self, layer: str, domain: Optional[str] = None) -> list[str]:
        """List all files in a layer, optionally filtered by domain."""
        layer_dir = self.root / layer
        if domain:
            layer_dir = layer_dir / domain

        if not layer_dir.exists():
            return []

        results = []
        for f in layer_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(self.root / layer)
                results.append(str(rel).replace("\\", "/"))
        return sorted(results)

    # ── WRITE operations (pending only) ──────────────────────

    def write_pending(self, suggestion: Suggestion) -> str:
        """Write a suggestion to pending/ directory. Returns the file path."""
        safe_title = re.sub(r"[^\w\-]", "-", suggestion.title.lower().strip())
        safe_title = re.sub(r"-+", "-", safe_title).strip("-")

        target_dir = self.pending_dir / suggestion.domain
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_title}.md"

        frontmatter = {
            "title": suggestion.title,
            "domain": suggestion.domain,
            "status": suggestion.status.value,
            "suggested_date": suggestion.suggested_date.isoformat(),
            "reason": suggestion.reason,
            "tags": suggestion.suggested_tags,
        }

        content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n\n{suggestion.content}\n"
        target_path.write_text(content, encoding="utf-8")

        return str(target_path.relative_to(self.root)).replace("\\", "/")

    def _pending_path_for(self, layer_type: LayerType, domain: Optional[str]) -> Path:
        """Compute the pending subdirectory for a given layer_type and domain."""
        if domain is None:
            return self.pending_dir / "unclassified"
        if layer_type == LayerType.KNOWLEDGE:
            return self.pending_dir / domain
        else:
            return self.pending_dir / f"{layer_type.value}s" / domain

    def write_pending_unified(self, suggestion: Suggestion) -> str:
        """Write a suggestion using unified routing based on layer_type and domain.

        Routes:
          knowledge  → pending/<domain>/          (domain=None → pending/unclassified/)
          workflow   → pending/workflows/<domain>/
          template   → pending/templates/<domain>/
          prompt     → pending/prompts/<domain>/
          example    → pending/examples/<domain>/

        Returns the relative file path.
        """
        safe_title = re.sub(r"[^\w\-]", "-", suggestion.title.lower().strip())
        safe_title = re.sub(r"-+", "-", safe_title).strip("-")

        target_dir = self._pending_path_for(suggestion.layer_type, suggestion.domain)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_title}.md"

        frontmatter = {
            "title": suggestion.title,
            "domain": suggestion.domain,
            "layer_type": suggestion.layer_type.value,
            "status": suggestion.status.value,
            "suggested_date": suggestion.suggested_date.isoformat(),
            "reason": suggestion.reason,
            "tags": suggestion.suggested_tags,
            "classification_reasoning": suggestion.classification_reasoning,
            "domain_alternatives": suggestion.domain_alternatives,
        }

        content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n\n{suggestion.content}\n"
        target_path.write_text(content, encoding="utf-8")

        return str(target_path.relative_to(self.root)).replace("\\", "/")

    def reclassify_pending(self, file_path: str, new_domain: str, new_layer_type: Optional[str] = None, reason: str = "") -> str:
        """Move a pending file to a new domain/layer_type location, updating its frontmatter.

        Args:
            file_path: Relative path from project root, e.g. "pending/unclassified/my-entry.md"
            new_domain: Target domain, e.g. "quant/backtest"
            new_layer_type: If None, keep existing layer_type from frontmatter
            reason: Human's reasoning for reclassification

        Returns the new relative file path.
        """
        full_path = self.root / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Pending file not found: {file_path}")
        if not full_path.resolve().is_relative_to(self.pending_dir.resolve()):
            raise ValueError(f"File is not inside pending/: {file_path}")

        text = full_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not match:
            raise ValueError(f"No YAML frontmatter found in: {file_path}")

        meta = yaml.safe_load(match.group(1)) or {}
        body = text[match.end():]

        # Determine new layer_type
        if new_layer_type:
            layer = LayerType(new_layer_type)
        else:
            existing = meta.get("layer_type", "knowledge")
            layer = LayerType(existing)

        # Update frontmatter
        meta["domain"] = new_domain
        meta["layer_type"] = layer.value
        meta["human_classified"] = True
        if reason:
            meta["human_classification_reason"] = reason

        # Compute new path
        target_dir = self._pending_path_for(layer, new_domain)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / full_path.name

        new_content = f"---\n{yaml.dump(meta, allow_unicode=True, default_flow_style=False)}---\n\n{body}"
        target_path.write_text(new_content, encoding="utf-8")

        # Remove old file if different location
        if target_path.resolve() != full_path.resolve():
            full_path.unlink()

        return str(target_path.relative_to(self.root)).replace("\\", "/")

    def write_pending_resource(self, resource_type: str, domain: str, name: str, content: str, reason: str) -> str:
        """Write a suggested resource (workflow/template/prompt/example) to pending/<type>/.

        Args:
            resource_type: one of 'workflows', 'templates', 'prompts', 'examples'
            domain: e.g. 'quant/alpha'
            name: filename without extension
            content: full file content (YAML for workflows, Markdown for others)
            reason: why this resource should be added
        """
        ext = ".yaml" if resource_type == "workflows" else ".md"
        safe_name = re.sub(r"[^\w\-/]", "-", name.lower().strip())
        safe_name = re.sub(r"-+", "-", safe_name).strip("-")

        target_dir = self.pending_dir / resource_type / domain
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_name}{ext}"

        header = f"# PENDING {resource_type[:-1].upper()} SUGGESTION\n# Reason: {reason}\n# Domain: {domain}\n# Status: PENDING — awaiting human approval\n\n"
        target_path.write_text(header + content, encoding="utf-8")

        return str(target_path.relative_to(self.root)).replace("\\", "/")

    def list_pending(self, unclassified_only: bool = False) -> list[dict]:
        """List all pending suggestions, optionally filtered to unclassified only."""
        results = []
        unclassified_dir = self.pending_dir / "unclassified"
        for md_file in self.pending_dir.rglob("*.md"):
            if unclassified_only and not md_file.resolve().is_relative_to(unclassified_dir.resolve()):
                continue
            try:
                text = md_file.read_text(encoding="utf-8")
                match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
                if match:
                    meta = yaml.safe_load(match.group(1)) or {}
                    meta["file"] = str(md_file.relative_to(self.root)).replace("\\", "/")
                    results.append(meta)
            except Exception:
                continue
        return results
