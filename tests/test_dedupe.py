from src.dedupe import item_key
from src.models import RawItem


def test_same_title_and_domain_generate_same_key():
    first = RawItem(
        source="A",
        source_trust="discovery",
        category_hint="news",
        title="What changed in SEBI mutual fund rules?",
        link="https://example.com/a",
        published_at=None,
    )
    second = RawItem(
        source="B",
        source_trust="discovery",
        category_hint="news",
        title="What changed in SEBI mutual fund rules",
        link="https://example.com/b",
        published_at=None,
    )

    assert item_key(first) == item_key(second)
