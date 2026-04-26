from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawItem:
    source: str
    source_trust: str
    category_hint: str
    title: str
    link: str
    published_at: datetime | None
    description: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class ScoredItem:
    raw: RawItem
    score: int
    category: str
    matched_terms: list[str]
    excluded_terms: list[str]


@dataclass
class SummaryItem:
    headline: str
    summary: str
    why_it_matters: str
    content_angle: str
    suggested_format: str
    source_link: str
    relevance_score: int
    category: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
