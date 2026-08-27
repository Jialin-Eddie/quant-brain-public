"""Pydantic data models for quant-brain knowledge library."""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LayerType(str, Enum):
    KNOWLEDGE = "knowledge"
    WORKFLOW = "workflow"
    TEMPLATE = "template"
    PROMPT = "prompt"
    EXAMPLE = "example"


class KnowledgeEntry(BaseModel):
    """A single knowledge/lesson-learned entry."""

    id: str = Field(description="Unique slug identifier, e.g. 'lookahead-bias'")
    domain: str = Field(description="Domain path, e.g. 'quant/backtest'")
    title: str = Field(description="Human-readable title")
    summary: str = Field(default="", description="One-line summary")
    tags: list[str] = Field(default_factory=list)
    severity: Severity = Field(default=Severity.MEDIUM)
    date_created: date = Field(default_factory=date.today)
    source_project: str = Field(default="", description="Which project this came from")
    transferable: bool = Field(default=True, description="Can this be applied to other projects?")
    file_path: str = Field(default="", description="Relative path to the MD file")


class SearchQuery(BaseModel):
    """Search parameters for knowledge lookup."""

    query: str = Field(description="Keyword or phrase to search for")
    domain: Optional[str] = Field(default=None, description="Limit search to this domain, e.g. 'quant/alpha'")
    tags: list[str] = Field(default_factory=list, description="Filter by tags")


class SearchResult(BaseModel):
    """A single search result."""

    entry: KnowledgeEntry
    relevance_score: float = Field(default=0.0, description="Higher = more relevant")
    matched_fields: list[str] = Field(default_factory=list)


class Suggestion(BaseModel):
    """A suggestion for new knowledge, pending human approval."""

    domain: Optional[str] = Field(default=None, description="Target domain; None → pending/unclassified/")
    title: str
    content: str
    reason: str = Field(description="Why this should be added")
    status: SuggestionStatus = Field(default=SuggestionStatus.PENDING)
    suggested_date: date = Field(default_factory=date.today)
    suggested_tags: list[str] = Field(default_factory=list)
    layer_type: LayerType = Field(default=LayerType.KNOWLEDGE)
    classification_reasoning: str = Field(default="", description="Why Claude chose this domain+layer")
    domain_alternatives: list[str] = Field(default_factory=list, description="Other plausible domains")
