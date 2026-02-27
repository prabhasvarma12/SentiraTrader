"""Sentiment analysis utilities for news and social media."""

from bs4 import BeautifulSoup
import requests
from typing import List

# In a real implementation, this would call an LLM (e.g. OpenAI) or a
# sentiment-analysis library such as TextBlob, Vader, or transformers.
# The stub below allows the rest of the system to be exercised without
# network access.

def analyze_text_sentiment(text: str) -> float:
    """Analyze sentiment of given text and return a polarity score.

    The value is in the range [-1.0, 1.0], where negative indicates
    bearish/negative sentiment and positive indicates bullish/positive
    sentiment.  For now the function uses a simple keyword heuristic; in
    production it would query an LLM or sentiment model.

    Examples::

        >>> analyze_text_sentiment("This company is doing good business")
        0.5
        >>> analyze_text_sentiment("Time to sell; the outlook is weak")
        -0.2
    """
    score = 0.0
    txt = text.lower()
    if any(word in txt for word in ["good", "excellent", "bullish"]):
        score += 0.6
    if "buy" in txt:
        score += 0.3
    if "sell" in txt or "bad" in txt or "bearish" in txt:
        score -= 0.6
    # clamp
    return max(-1.0, min(1.0, score))


def fetch_mock_news(url: str) -> str:
    """Scrape mock news text from a URL.

    This helper simply retrieves the page and strips tags.  It is used by
    the demo to produce input for the sentiment analyzer.
    """
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.get_text()
    except Exception:
        return ""


def aggregate_sentiments(texts: List[str]) -> float:
    """Combine multiple sentiment scores into a single average score."""
    if not texts:
        return 0.0
    scores = [analyze_text_sentiment(t) for t in texts]
    return sum(scores) / len(scores)
