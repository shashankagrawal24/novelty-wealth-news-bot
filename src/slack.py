import os
from collections import defaultdict

import httpx

from src.models import SummaryItem
from src.utils import truncate


def section_block(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def build_blocks(items: list[SummaryItem]) -> list[dict]:
    blocks: list[dict] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Novelty Wealth Finance Radar"},
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        "Top India finance, tax, investing, regulator, and "
                        "wealth-management updates."
                    ),
                }
            ],
        },
        {"type": "divider"},
    ]

    grouped = defaultdict(list)
    for item in items:
        grouped[item.category].append(item)

    for category, category_items in grouped.items():
        blocks.append(section_block(f"*{category}*"))

        for item in category_items[:3]:
            text = (
                f"*<{item.source_link}|{item.headline}>*\n"
                f"{item.summary}\n"
                f"*Why it matters:* {item.why_it_matters}\n"
                f"*Novelty angle:* {item.content_angle}\n"
                f"*Format:* {item.suggested_format} | "
                f"*Score:* {item.relevance_score} | *Source:* {item.source}"
            )
            blocks.append(section_block(truncate(text, 2900)))

    content_ideas = [
        f"- {item.suggested_format}: {item.content_angle}"
        for item in items[:3]
    ]
    if content_ideas:
        blocks.extend(
            [
                {"type": "divider"},
                section_block("*Content Ideas for Novelty Wealth*"),
                section_block(truncate("\n".join(content_ideas), 2900)),
            ]
        )

    return blocks[:45]


def send_to_slack(items: list[SummaryItem]) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    blocks = build_blocks(items)
    payload = {
        "text": "Novelty Wealth Finance Radar",
        "blocks": blocks,
    }

    if dry_run:
        print(payload)
        return

    if not webhook_url:
        raise RuntimeError("SLACK_WEBHOOK_URL is required unless DRY_RUN=true")

    response = httpx.post(webhook_url, json=payload, timeout=30)
    response.raise_for_status()
