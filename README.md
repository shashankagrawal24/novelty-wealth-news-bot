# Novelty Wealth News Bot

Fetches Indian finance, wealth-management, tax, regulator, banking, insurance,
mutual fund, NPS, and macro updates from RSS feeds, filters them for relevance,
summarizes them, and sends a concise digest to Slack.

## What It Tracks

- Indian personal finance
- Wealth management
- Mutual funds
- NPS and retirement
- Credit cards and banking
- SEBI, RBI, IRDAI, PFRDA updates
- Income tax and government policy
- India macro updates relevant to investors
- Content ideas for blogs, carousels, reels, push notifications, in-app insights, and NovaAI prompts

## Architecture

```text
config/sources.yml      RSS feeds and monitored source pages
config/keywords.yml     Relevance keywords, exclusions, and scoring weights
src/rss_fetcher.py      RSS fetching and XML parsing
src/filtering.py        Keyword filtering, category assignment, and scoring
src/dedupe.py           Seen-item dedupe state
src/summarizer.py       LLM or fallback summaries
src/slack.py            Slack Block Kit delivery
src/main.py             Orchestrator
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and add:

```text
SLACK_WEBHOOK_URL=...
OPENAI_API_KEY=optional
DRY_RUN=true
```

Run locally:

```bash
python -m src.main
```

Run tests:

```bash
pytest
```

## Slack Webhook Setup

1. Go to Slack API apps.
2. Create a new app.
3. Enable Incoming Webhooks.
4. Add a webhook to the target channel.
5. Copy the webhook URL.
6. Store it as `SLACK_WEBHOOK_URL`.

## GitHub Secrets

In GitHub:

```text
Settings > Secrets and variables > Actions > New repository secret
```

Add:

```text
SLACK_WEBHOOK_URL
OPENAI_API_KEY
```

Optional repository variables:

```text
OPENAI_MODEL
MIN_RELEVANCE_SCORE
MAX_ITEMS_PER_RUN
LOOKBACK_HOURS
```

## Deployment

The workflow runs twice daily by default:

```yaml
30 3 * * *
30 11 * * *
```

These are UTC times. Adjust `.github/workflows/news-digest.yml` for India-friendly
delivery windows.

## Adding Feeds

Edit:

```text
config/sources.yml
```

Add a source:

```yaml
- name: Example Finance Feed
  type: rss
  url: https://example.com/rss
  trust: discovery
  category_hint: news
```

Use `trust: official` only for regulator/government/source-of-record feeds.

## Editing Keywords

Edit:

```text
config/keywords.yml
```

Increase weights for high-priority topics like SEBI, RBI, NPS, mutual funds, tax,
or retirement.

## Compliance Guardrails

This bot must not:

- Recommend buying or selling securities.
- Give stock tips.
- Promise or imply returns.
- Make SEBI-non-compliant promotional claims.
- Treat unverified RSS summaries as facts without source attribution.

Slack summaries should remain educational and factual.

## Notes

Some official sources provide RSS directories rather than clean single feed URLs.
Add exact feed URLs to `config/sources.yml` after selecting the relevant sections
from RBI, AMFI, NSE, BSE, PFRDA, and IRDAI.
