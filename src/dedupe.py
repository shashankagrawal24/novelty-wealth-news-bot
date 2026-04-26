import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from src.models import RawItem, ScoredItem


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "what", "why", "how", "did", "does", "is", "are",
}


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    words = [word for word in title.split() if word not in STOPWORDS]
    return " ".join(words)


def item_key(item: RawItem) -> str:
    domain = urlparse(item.link).netloc.lower().replace("www.", "")
    base = f"{normalize_title(item.title)}|{domain}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        return set(json.loads(path.read_text(encoding="utf-8")).get("seen", []))
    except Exception:
        return set()


def save_seen(path: Path, seen: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen": sorted(seen)[-5000:]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def remove_seen(items: list[ScoredItem], seen: set[str]) -> list[ScoredItem]:
    fresh = []
    for item in items:
        key = item_key(item.raw)
        if key not in seen:
            fresh.append(item)
    return fresh


def mark_seen(items: list[ScoredItem], seen: set[str]) -> set[str]:
    updated = set(seen)
    for item in items:
        updated.add(item_key(item.raw))
    return updated
