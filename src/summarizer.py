import json
import os

from openai import OpenAI

from src.models import ScoredItem, SummaryItem
from src.utils import truncate


PROMPT_TEMPLATE = """
You are summarizing Indian personal finance and wealth-management news for Novelty Wealth.

Rules:
- Do not give investment advice.
- Do not recommend buying, selling, or switching securities/funds.
- Do not make return guarantees.
- Keep language factual, cautious, and educational.
- If the item is not clearly relevant to Indian investors, produce a conservative education angle.
- Return valid JSON only.

Create:
headline, summary, why_it_matters, content_angle, suggested_format.

Allowed suggested_format values:
blog, carousel, reel, push notification, in-app insight, NovaAI prompt.

Item:
Title: {title}
Description: {description}
Source: {source}
Link: {link}
Category: {category}
Score: {score}
Matched terms: {matched_terms}
"""


def fallback_summary(item: ScoredItem) -> SummaryItem:
    raw = item.raw
    title = truncate(raw.title, 140)
    description = truncate(raw.description or "No description available.", 260)

    return SummaryItem(
        headline=title,
        summary=description,
        why_it_matters=(
            "This may affect how Indian users think about tax, regulation, investing, "
            "banking, insurance, or long-term financial planning."
        ),
        content_angle=(
            "Explain the update in simple terms and clarify what users should watch next, "
            "without making product or investment recommendations."
        ),
        suggested_format="in-app insight",
        source_link=raw.link,
        relevance_score=item.score,
        category=item.category,
        source=raw.source,
        metadata={"mode": "fallback"},
    )


def llm_summary(item: ScoredItem) -> SummaryItem:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_summary(item)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(
        title=item.raw.title,
        description=item.raw.description,
        source=item.raw.source,
        link=item.raw.link,
        category=item.category,
        score=item.score,
        matched_terms=", ".join(item.matched_terms),
    )

    try:
        response = client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=500,
        )
        data = json.loads(response.output_text)
    except Exception:
        return fallback_summary(item)

    return SummaryItem(
        headline=truncate(data.get("headline", item.raw.title), 140),
        summary=truncate(data.get("summary", item.raw.description), 500),
        why_it_matters=truncate(data.get("why_it_matters", ""), 500),
        content_angle=truncate(data.get("content_angle", ""), 500),
        suggested_format=data.get("suggested_format", "in-app insight"),
        source_link=item.raw.link,
        relevance_score=item.score,
        category=item.category,
        source=item.raw.source,
        metadata={"mode": "llm"},
    )


def summarize_items(items: list[ScoredItem]) -> list[SummaryItem]:
    return [llm_summary(item) for item in items]
