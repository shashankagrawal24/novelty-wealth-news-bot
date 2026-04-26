import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.dedupe import load_seen, mark_seen, remove_seen, save_seen
from src.filtering import filter_and_rank
from src.rss_fetcher import fetch_all_sources
from src.slack import send_to_slack
from src.summarizer import summarize_items

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def main() -> None:
    load_dotenv()

    sources_config = load_yaml(ROOT / "config" / "sources.yml")
    keyword_config = load_yaml(ROOT / "config" / "keywords.yml")

    min_score = int(os.getenv("MIN_RELEVANCE_SCORE", "45"))
    max_items = int(os.getenv("MAX_ITEMS_PER_RUN", "8"))
    lookback_hours = int(os.getenv("LOOKBACK_HOURS", "36"))
    seen_path = ROOT / "data" / "seen.json"

    logger.info("Fetching RSS items")
    raw_items = fetch_all_sources(sources_config, lookback_hours)
    logger.info("Fetched %d raw items", len(raw_items))

    ranked = filter_and_rank(raw_items, keyword_config, min_score, max_items * 3)
    logger.info("Found %d relevant items before dedupe", len(ranked))

    seen = load_seen(seen_path)
    fresh = remove_seen(ranked, seen)[:max_items]
    logger.info("Found %d fresh items after dedupe", len(fresh))

    if not fresh:
        logger.info("No fresh relevant items to send")
        return

    summaries = summarize_items(fresh)
    send_to_slack(summaries)

    updated_seen = mark_seen(fresh, seen)
    save_seen(seen_path, updated_seen)
    logger.info("Sent %d items to Slack", len(summaries))


if __name__ == "__main__":
    main()
