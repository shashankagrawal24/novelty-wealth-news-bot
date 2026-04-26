import re
from datetime import datetime, timezone

from src.models import RawItem, ScoredItem
from src.utils import normalize_for_match


CATEGORY_LABELS = {
    "india": "Regulators & Policy",
    "personal_finance": "Personal Finance",
    "wealth_management": "Mutual Funds & Wealth",
    "mutual_funds": "Mutual Funds & Wealth",
    "nps_retirement": "NPS & Retirement",
    "banking_credit": "Banking, Credit & Insurance",
    "markets_macro": "Markets & Macro",
}


def term_matches(text: str, term: str) -> bool:
    normalized_term = normalize_for_match(term)
    if not normalized_term:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def score_item(item: RawItem, keyword_config: dict) -> ScoredItem:
    text = normalize_for_match(
        " ".join([item.title, item.description, " ".join(item.tags), item.source])
    )

    score = 0
    matched_terms: list[str] = []
    category_scores: dict[str, int] = {}

    for category, rule in keyword_config.get("positive", {}).items():
        category_score = 0
        for term in rule.get("terms", []):
            if term_matches(text, term):
                category_score += int(rule.get("weight", 0))
                matched_terms.append(term)
        if category_score:
            category_scores[category] = category_score
            score += min(category_score, int(rule.get("weight", 0)) + 10)

    excluded_terms: list[str] = []
    for term in keyword_config.get("exclude", {}).get("hard", []):
        if term_matches(text, term):
            excluded_terms.append(term)
            score -= 40

    for term in keyword_config.get("exclude", {}).get("soft", []):
        if term_matches(text, term):
            excluded_terms.append(term)
            score -= 15

    if item.source_trust == "official":
        score += 10

    if item.published_at:
        age_hours = (datetime.now(timezone.utc) - item.published_at).total_seconds() / 3600
        if age_hours <= 24:
            score += 10

    if item.tags:
        score += 5

    india_markers = [
        "india", "indian", "rbi", "sebi", "pfrda", "irdai", "nse", "bse",
        "income tax", "amfi", "nifty", "sensex", "rupee", "inr",
    ]
    if not any(term_matches(text, marker) for marker in india_markers):
        score -= 30

    score = max(0, min(100, score))

    if category_scores:
        top_category = max(category_scores, key=category_scores.get)
        label = CATEGORY_LABELS.get(top_category, "India Finance")
    else:
        label = "India Finance"

    return ScoredItem(
        raw=item,
        score=score,
        category=label,
        matched_terms=sorted(set(matched_terms)),
        excluded_terms=sorted(set(excluded_terms)),
    )


def filter_and_rank(
    items: list[RawItem],
    keyword_config: dict,
    min_score: int,
    max_items: int,
) -> list[ScoredItem]:
    scored = [score_item(item, keyword_config) for item in items]
    relevant = [item for item in scored if item.score >= min_score]
    relevant.sort(key=lambda x: x.score, reverse=True)
    return relevant[:max_items]
