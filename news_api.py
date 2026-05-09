import os
from typing import List, Dict

import requests
import streamlit as st

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_ENDPOINT = "https://newsdata.io/api/1/news"

HIGH_IMPACT_KEYWORDS = [
    "cpi",
    "inflation",
    "interest rate",
    "fomc",
    "ecb",
    "policy",
    "gdp",
    "employment",
    "pmi",
]

POSITIVE_WORDS = [
    "rise",
    "gain",
    "up",
    "increase",
    "positive",
    "bullish",
    "strengthen",
    "surge",
]

NEGATIVE_WORDS = [
    "drop",
    "fall",
    "down",
    "decrease",
    "negative",
    "bearish",
    "slip",
    "decline",
]


def _extract_sentiment(title: str) -> str:

    lowered = title.lower()

    if any(w in lowered for w in POSITIVE_WORDS):
        return "Bullish"

    if any(w in lowered for w in NEGATIVE_WORDS):
        return "Bearish"

    return "Neutral"


@st.cache_data(ttl=300)
def fetch_news() -> List[Dict]:

    if not NEWS_API_KEY:
        return []

    params = {
        "apikey": NEWS_API_KEY,
        "category": "business",
        "language": "en",
        "q": "forex OR USD OR EUR OR GBP OR JPY",
        "size": 20,
    }

    try:

        resp = requests.get(
            NEWS_ENDPOINT,
            params=params,
            timeout=10
        )

        resp.raise_for_status()

        payload = resp.json()

        raw_items = payload.get("results", [])

    except Exception:

        return []

    filtered: List[Dict] = []

    for item in raw_items:

        title = item.get("title", "")

        if not title:
            continue

        if not any(
            k in title.lower()
            for k in HIGH_IMPACT_KEYWORDS
        ):
            continue

        sentiment = _extract_sentiment(title)

        filtered.append(
            {
                "title": title,
                "description": item.get(
                    "description",
                    ""
                ),
                "pubDate": item.get(
                    "pubDate",
                    ""
                ),
                "sentiment": sentiment,
                "source": item.get(
                    "source_id",
                    ""
                ),
                "link": item.get(
                    "link",
                    ""
                ),
            }
        )

    return filtered


def summarize_news(
    news_items: List[Dict]
) -> str:

    if not news_items:
        return "No recent high-impact forex news."

    lines = []

    for n in news_items[:5]:

        sentiment = n.get(
            "sentiment",
            "Neutral"
        )

        title = n.get(
            "title",
            ""
        ).strip()

        source = n.get(
            "source",
            ""
        )

        line = f"{sentiment} - {title}"

        if source:
            line += f" (source: {source})"

        lines.append(f"• {line}")

    return "\n".join(lines)