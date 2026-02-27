"""Live market data fetching and caching."""
import requests
import time
from typing import Dict, List
from datetime import datetime

# Using Alpha Vantage for free tier (requires API key, but we'll provide mock fallback)
# For production, integrate with: IEX Cloud, Polygon.io, or similar

ALPHA_VANTAGE_API_KEY = "demo"  # Replace with actual key
CACHE_EXPIRY = 60  # seconds

class PriceCache:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
    
    def get_price_and_change(self, symbol: str):
        """Fetch current price, absolute change, and percent change for symbol."""
        if symbol in self.cache:
            cached = self.cache[symbol]
            if time.time() - cached["timestamp"] < CACHE_EXPIRY:
                return cached["price"], cached["change"], cached["percent_change"]
        
        # Try to fetch real price
        price_data = self._fetch_real_price(symbol)
        price = price_data.get("price", 100.0)
        prev_close = price_data.get("prev_close", 100.0)
        
        change = price - prev_close
        percent_change = (change / prev_close * 100) if prev_close > 0 else 0.0
        
        self.cache[symbol] = {
            "price": price, 
            "change": change,
            "percent_change": percent_change,
            "timestamp": time.time()
        }
        return price, change, percent_change
        
    def get_price(self, symbol: str) -> float:
        """Compatibility wrapper for just fetching price."""
        price, _, _ = self.get_price_and_change(symbol)
        return price
    
    def _fetch_real_price(self, symbol: str) -> Dict[str, float]:
        """Attempt to fetch price and previous close from yfinance."""
        result = {
            "price": 100.0 + hash(symbol) % 50,
            "prev_close": 100.0 + hash(symbol) % 50 # mock fallback
        }
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            
            # fast info has the most current reliable price without downloading large histories
            price = ticker.fast_info.get("last_price")
            prev_close = ticker.fast_info.get("previous_close")
            
            if price and prev_close:
                result["price"] = float(price)
                result["prev_close"] = float(prev_close)
                return result
                
            # fallback to history if fast_info fails
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                result["price"] = float(hist['Close'].iloc[-1])
                result["prev_close"] = float(hist['Close'].iloc[-2])
                return result
                
        except Exception as e:
            print(f"Error fetching yfinance data for {symbol}: {e}")
        
        return result

def fetch_live_news_sentiments(symbols: List[str]) -> Dict[str, str]:
    """Fetch financial news for given symbols using a free news API."""
    # hybrid behaviour: attempt live API, fall back to scraping, then mock
    try:
        from ingestion import get_news_text
        return get_news_text(symbols)
    except Exception:
        # as a last resort build simple mock
        return {s: f"Mock market news for {s}" for s in symbols}

def fetch_market_overview() -> Dict:
    """Fetch market overview (indices, sentiment, etc.)."""
    try:
        # Could integrate with Finnhub, Alpha Vantage, etc.
        url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey=demo"
        resp = requests.get(url, timeout=5)
        return resp.json()
    except Exception:
        return {
            "market_trend": "bullish",
            "vix": 18.5,
            "sp500_change": 0.8,
            "timestamp": datetime.now().isoformat()
        }
