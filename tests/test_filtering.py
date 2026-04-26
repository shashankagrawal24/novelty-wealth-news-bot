from datetime import datetime, timezone

from src.filtering import score_item
from src.models import RawItem


def test_indian_mutual_fund_item_scores_high():
    config = {
        "positive": {
            "india": {"weight": 25, "terms": ["india", "sebi", "amfi"]},
            "mutual_funds": {"weight": 20, "terms": ["mutual fund", "sip"]},
        },
        "exclude": {"hard": ["sports"], "soft": []},
    }

    item = RawItem(
        source="AMFI",
        source_trust="official",
        category_hint="mutual_funds",
        title="AMFI reports India mutual fund SIP inflows rise",
        link="https://example.com",
        published_at=datetime.now(timezone.utc),
        description="SIP inflows into mutual fund schemes increased.",
    )

    scored = score_item(item, config)
    assert scored.score >= 45


def test_sports_item_scores_low():
    config = {
        "positive": {"india": {"weight": 25, "terms": ["india"]}},
        "exclude": {"hard": ["sports"], "soft": []},
    }

    item = RawItem(
        source="Biztoc",
        source_trust="discovery",
        category_hint="news",
        title="NFL sports draft update",
        link="https://example.com",
        published_at=datetime.now(timezone.utc),
        description="Sports story.",
    )

    scored = score_item(item, config)
    assert scored.score < 45
