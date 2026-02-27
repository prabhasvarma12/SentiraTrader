"""Hybrid engine for news/text ingestion.

Attempts to fetch live content from the web; if any step fails, returns
hardcoded mock data to guarantee that downstream components always receive
some text.
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import feedparser
import logging

# Set up simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fallback data
MOCK_HEADLINES = [
    "Market remains stable despite global uncertainties.",
    "Tech stocks rally on positive earnings reports.",
    "Investors cautious as inflation data approaches.",
    "Energy sector underperforms amid supply concerns.",
]


class HybridNewsFetcher:
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or []

    def fetch(self) -> Dict[str, str]:
        """Return a dict mapping each symbol to a block of text.

        Live data is attempted first; on failure the method returns mock
        headlines concatenated together so that sentiment analysis always
        has material to work on.
        """
        aggregated = {}
        for sym in self.symbols:
            try:
                # 1. Try Yahoo Finance RSS
                url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={sym}"
                feed = feedparser.parse(url)
                
                headlines = []
                if not feed.bozo and feed.entries:
                    # Successfully parsed RSS
                    for entry in feed.entries[:5]: # Get top 5 headlines
                        headlines.append(entry.title)
                
                if headlines:
                    aggregated[sym] = " ".join(headlines)
                    logger.info(f"Fetched RSS headlines for {sym}")
                    continue
                
                # 2. Try scraping if RSS fails or is empty
                url = f"https://finance.yahoo.com/quote/{sym}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resp = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Yahoo finance page structure changes often, try to find h3 tags which often hold news
                news_tags = soup.find_all('h3')
                scraped_text = " ".join([tag.get_text() for tag in news_tags if tag.get_text()])
                
                if scraped_text:
                     aggregated[sym] = scraped_text
                     logger.info(f"Scraped headlines for {sym}")
                     continue
                     
            except Exception as e:
                logger.warning(f"Failed to fetch news for {sym}: {e}")

            # 3. Fallback to mock
            logger.info(f"Using mock data for {sym}")
            aggregated[sym] = " ".join(MOCK_HEADLINES)
            
        return aggregated


# convenience function

def get_news_text(symbols: List[str]) -> Dict[str, str]:
    return HybridNewsFetcher(symbols).fetch()
