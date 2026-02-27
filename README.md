<<<<<<< HEAD
# SentiraTrader
SentiraTrader is the only autonomous trading terminal that bridges the gap between institutional risk guardrails and generative AI by forcing the Gemini LLM to ingest live multi-stream market data and synthesize strictly quantified position-sizing executions directly against a physically persistent accounting ledger.
=======
# Stock Market Sentiment Agentic Trader

An autonomous trading agent that monitors sentiment in news and social media to adjust portfolio risk and execute buy/sell orders. Built with Python, BeautifulSoup, LLM interfaces, and Streamlit.

## ✨ Features

- **Real-time Sentiment Analysis**: Converts news and social media text into polarity scores using keyword heuristics (extensible to LLM-based models).
- **Dynamic Risk Adjustment**: Automatically adjusts portfolio risk exposure based on market sentiment.
- **Autonomous Order Generation**: Drafts buy/sell orders proportional to sentiment strength and risk posture.
- **Live Price Fetching**: Integrates with Alpha Vantage API for real-time price data (with mock fallback).
- **Trade Execution & History**: Tracks all trades with timestamps, prices, and sentiment scores.
- **Real-time Dashboard**: Multi-tab Streamlit UI with live sentiment analysis, portfolio status, trade history, and market overview.
- **Auto-refresh**: Optional 30-second auto-refresh for continuous monitoring.
- **Mock Data Demo**: Standalone demo script with multi-symbol trading and detailed trade tracking.

## 📊 Project Structure

```
.
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── docs/
│   └── SENTIMENT_ANALYSIS.md      # Algorithm and design documentation
└── src/
    ├── __init__.py
    ├── sentiment.py               # Sentiment analysis module
    ├── portfolio.py               # Portfolio management and trading logic
    ├── market_data.py             # Live price and news fetching
    ├── app.py                     # Streamlit dashboard (main UI)
    └── demo.py                    # Mock data demonstration script
```

## 🚀 Setup

1. **Create a Python virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set API Keys for live data**:
   - Edit `src/market_data.py` and add your:
     - **Alpha Vantage API key** for stock prices
     - **NewsAPI key** for live news headlines

## 💻 Usage

### Run the Enhanced Demo

Execute the agent with mock news texts, multiple symbols, and detailed trade tracking:

```bash
cd src
python demo.py
```

**Sample Output**:
```
═══════════════════════════════════════════════════════════════════════════
STOCK MARKET SENTIMENT AGENTIC TRADER - DEMO
═══════════════════════════════════════════════════════════════════════════

Starting Portfolio Value: $100000.00
Initial Cash: $100000.00
Watched Symbols: AAPL, GOOGL, TSLA, MSFT

──────────────────────────────────────────────────────────────────────────
ROUND 1: News Event
──────────────────────────────────────────────────────────────────────────
📰 News: Company reports excellent earnings, buy now!
📊 Sentiment Score: 0.60 (BULLISH 📈)
⚠️  Risk Level Updated: 80%

📋 Generated Orders:
  • BUY     480.00 shares of AAPL @ $100.00
             ✅ Executed | Trade Value: $48000.00
  ...

💼 Portfolio Status:
  Cash:        $52000.00
  Total Value: $100000.00
  Positions: 1 open
    - AAPL: 480.00 shares @ $100.00 = $48000.00

═══════════════════════════════════════════════════════════════════════════
FINAL RESULTS
═══════════════════════════════════════════════════════════════════════════
Total Trades Executed: 8
Final Portfolio Value: $99500.00
Remaining Cash: $12500.00
Final Risk Level: 50%

📈 Trade Summary:
  Total Buys: 4
  Total Sells: 4
  Total Trading Volume: $187500.00
```

### Run the Interactive Dashboard

Interact with the agent in real-time via a professional web UI with live updates:

```bash
cd src
streamlit run app.py
```

**Dashboard Features**:

1. **Live Trading Tab**:
   - Paste financial news URLs or raw text
   - Real-time sentiment analysis
   - Automatic order generation for multiple watched symbols
   - One-click order execution with confirmation
   - Quick-action buttons for live news fetching

2. **Portfolio Tab**:
   - Key metrics: Total Value, Cash, Risk Level, Trade Count
   - Current positions with live prices
   - Symbol-specific price quotes

3. **Trade History Tab**:
   - Complete trade log with timestamps
   - Trade details: symbol, action, quantity, price, sentiment
   - Summary statistics: total buys, sells, trading volume

4. **Market Overview Tab**:
   - Market trend (bullish/bearish)
   - VIX volatility index
   - S&P 500 movement
   - Portfolio value chart over time
   - Sentiment trend visualization

5. **Auto-Refresh**:
   - Optional 30-second auto-refresh for continuous monitoring
   - Sidebar configuration panel

## 🧠 Algorithm Overview

### Sentiment Scoring

Sentiment is derived by scanning text for bullish and bearish keywords:
- **Positive**: "good", "excellent", "bullish", "buy" → +0.3 to +0.6 per keyword
- **Negative**: "sell", "bad", "bearish" → -0.6 per keyword
- Final score is clamped to [-1.0, 1.0]

### Risk Adjustment

$$r = \max(0, \min(1, 0.5 + s/2))$$

Where $r \in [0, 1]$ is the risk level and $s \in [-1, 1]$ is the sentiment score.

### Order Generation

- **Strong Bullish** ($s > 0.3$): Buy shares proportional to risk and available cash.
- **Strong Bearish** ($s < -0.3$ and position held): Sell entire position.
- **Neutral**: Hold.

### Dynamic Position Sizing

Order quantity scales with both market sentiment and portfolio risk level:

$$\text{quantity} = \frac{\text{available\_cash} \times \text{risk\_level}}{\text{current\_price}}$$

## 🔌 Live Data Integration

### Market Data Sources
### Market Data Sources & Hybrid Ingestion

News and text ingestion is handled by a **Hybrid News Fetcher** located in
`src/ingestion.py`.  It attempts the following in order:

1. Use the NewsAPI for live headlines
2. Scrape a finance website (e.g. Yahoo Finance) for text
3. Return a set of hard‑coded mock headlines

This ensures the sentiment engine always receives some input, even when
the internet or APIs are unavailable.

Meanwhile the system can integrate with these real-time services:
 - **Alpha Vantage** – Stock prices, market indicators
 - **NewsAPI** – Financial news headlines
 - **Finnhub** – Market sentiment data (optional)

### Setting up API Keys

1. Get a free API key:
   - [Alpha Vantage](https://www.alphavantage.co/api)
   - [NewsAPI](https://newsapi.org)

2. Update `src/market_data.py`:
   ```python
   ALPHA_VANTAGE_API_KEY = "your_key_here"
   NEWSAPI_KEY = "your_key_here"
   ```

3. The system automatically falls back to mock data if APIs are unavailable.

## 🎯 Trade Tracking

Each executed trade records:
- **Symbol**: Asset being traded
- **Action**: BUY or SELL
- **Quantity**: Number of shares
- **Price**: Execution price (live or mock)
- **Timestamp**: Exact execution time
- **Sentiment Score**: Market sentiment at execution
- **Trade Value**: Total transaction value

Trades are persisted in session state and displayed in the Trade History tab with analytics.

## 🛠️ Extensibility

### LLM-Based Sentiment

Replace the keyword heuristic with an LLM (e.g., OpenAI GPT-4) for more nuanced understanding. See [SENTIMENT_ANALYSIS.md](docs/SENTIMENT_ANALYSIS.md).

### Multi-Symbol Trading

The system already supports tracking and trading multiple symbols simultaneously with per-symbol risk limits.

### Backtesting & Historical Analysis

Extend the system to:
- Fetch historical price data
- Replay sentiment streams
- Calculate returns and Sharpe ratios
- Optimize sentiment thresholds

## 📋 Requirements

- Python 3.8+
- Dependencies (see [requirements.txt](requirements.txt)):
  - `beautifulsoup4` – HTML parsing for web scraping
  - `streamlit` – Dashboard UI framework
  - `requests` – HTTP client for fetching URLs and APIs
  - `pandas` – Data manipulation and visualization
  - `openai` – (Optional) LLM integration for advanced sentiment

## 📖 Documentation

For detailed algorithm explanations, design rationale, and integration guides, see [docs/SENTIMENT_ANALYSIS.md](docs/SENTIMENT_ANALYSIS.md).

## 🔄 Workflow

The agent operates in a continuous loop:

1. **Sense**: Fetch and analyze sentiment from news/social media
2. **Decide**: Compute risk level and draft orders
3. **Act**: Execute trades autonomously
4. **Monitor**: Track performance and visualize results
>>>>>>> 27979f6 (Initial secure commit with AI API keys hidden)
