"""Search engine for quant-brain knowledge library.

Phase 1: Keyword-based search with domain filtering.
Phase 2 (future): Semantic search via sentence-transformers.
"""

from typing import Optional

from models import KnowledgeEntry, SearchResult
from storage import KnowledgeStore


class SearchEngine:
    """Keyword search with relevance scoring."""

    def __init__(self, store: KnowledgeStore):
        self.store = store

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        tags: Optional[list[str]] = None,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search knowledge with relevance scoring.

        Scoring:
        - Title exact match: +3.0
        - Title partial match: +2.0
        - Tag match: +1.5 per tag
        - Summary match: +1.0
        - ID match: +0.5
        """
        entries = self.store.search(query, domain, tags)
        query_lower = query.lower()
        scored: list[SearchResult] = []

        for entry in entries:
            score = 0.0
            matched = []

            # Title scoring
            if query_lower == entry.title.lower():
                score += 3.0
                matched.append("title_exact")
            elif query_lower in entry.title.lower():
                score += 2.0
                matched.append("title_partial")

            # Tag scoring
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 1.5
                    matched.append(f"tag:{tag}")

            # Summary scoring
            if query_lower in entry.summary.lower():
                score += 1.0
                matched.append("summary")

            # ID scoring
            if query_lower in entry.id.lower():
                score += 0.5
                matched.append("id")

            # Severity boost
            severity_boost = {"critical": 0.4, "high": 0.2, "medium": 0.0, "low": -0.1}
            score += severity_boost.get(entry.severity.value, 0.0)

            scored.append(SearchResult(
                entry=entry,
                relevance_score=score,
                matched_fields=matched,
            ))

        # Sort by relevance
        scored.sort(key=lambda r: r.relevance_score, reverse=True)
        return scored[:max_results]
