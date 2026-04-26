import logging
from datetime import datetime, timedelta, timezone

import feedparser
import httpx

from src.models import RawItem
from src.utils import clean_text, parse_datetime

logger = logging.getLogger(__name__)


def fetch_rss_source(source: dict, lookback_hours: int) -> list[RawItem]:
    url = source["url"]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    try:
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return []

    feed = feedparser.parse(response.content)
    items: list[RawItem] = []

    for entry in feed.entries:
        published_at = parse_datetime(
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
            or getattr(entry, "pubDate", None)
        )

        if published_at and published_at < cutoff:
            continue

        tags = []
        for tag in getattr(entry, "tags", []) or []:
            term = tag.get("term") if isinstance(tag, dict) else getattr(tag, "term", "")
            if term:
                tags.append(str(term))

        items.append(
            RawItem(
                source=source["name"],
                source_trust=source.get("trust", "unknown"),
                category_hint=source.get("category_hint", "news"),
                title=clean_text(getattr(entry, "title", "")),
                link=getattr(entry, "link", ""),
                published_at=published_at,
                description=clean_text(
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                ),
                tags=tags,
            )
        )

    return items


def fetch_all_sources(config: dict, lookback_hours: int) -> list[RawItem]:
    all_items: list[RawItem] = []

    for source in config.get("sources", []):
        if source.get("type") != "rss":
            continue
        all_items.extend(fetch_rss_source(source, lookback_hours))

    return all_items
