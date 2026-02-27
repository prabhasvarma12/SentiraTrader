# Stock Market Sentiment Agentic Trader

**A production-ready autonomous trading agent that monitors market sentiment and executes trades dynamically.**

## 🚀 Quick Links

| Want to... | Start here |
|-----------|-----------|
| **Get running in 5 minutes** | [QUICKSTART.md](QUICKSTART.md) ⭐ |
| **Understand the full system** | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| **Read full documentation** | [README.md](README.md) |
| **Learn the algorithm** | [docs/SENTIMENT_ANALYSIS.md](docs/SENTIMENT_ANALYSIS.md) |
| **Set up live API keys** | [docs/API_SETUP.md](docs/API_SETUP.md) |
| **See live trading features** | [docs/LIVE_TRADING_GUIDE.md](docs/LIVE_TRADING_GUIDE.md) |

## ⭐ Highlights

✅ **Real-time Sentiment Analysis** – Converts news/text to trading signals  
✅ **Dynamic Risk Management** – Automatically adjusts portfolio risk (0-100%)  
✅ **Live Price Fetching** – Alpha Vantage API integration with caching  
✅ **Professional Dashboard** – 5-tab Streamlit UI with auto-refresh  
✅ **Complete Trade History** – Records every execution with metadata  
✅ **Multi-Symbol Trading** – Simultaneous trading of 4+ stocks  
✅ **Mock Data Mode** – Works without API keys  
✅ **Production Ready** – Well-structured, documented, extensible  

## 🎯 What It Does

1. **Analyzes** financial news and social media for sentiment
2. **Calculates** portfolio risk level based on market sentiment
3. **Generates** buy/sell orders automatically
4. **Executes** trades with live market prices (or mock data)
5. **Tracks** complete trading history
6. **Visualizes** portfolio performance in a web dashboard

## 📊 Project Structure

```
.
├── QUICKSTART.md              ← START HERE (5-min setup)
├── PROJECT_OVERVIEW.md        ← System architecture & features
├── README.md                  ← Full documentation
├── requirements.txt           ← pip install -r requirements.txt
│
├── src/
│   ├── app.py                 ← Streamlit dashboard (web UI)
│   ├── demo.py                ← Standalone demo script
│   ├── portfolio.py           ← Trade & portfolio management
│   ├── sentiment.py           ← Sentiment analysis engine
│   └── market_data.py         ← Live data fetching
│
└── docs/
    ├── SENTIMENT_ANALYSIS.md  ← Algorithm with equations
    ├── API_SETUP.md           ← Free API key setup
    └── LIVE_TRADING_GUIDE.md  ← Feature overview
```

## 🏃 Get Started (Choose One)

### Option 1: Run the Demo (No setup needed)
```bash
cd src
python demo.py
```
See the agent trade 4 stocks autonomously with mock market data.

### Option 2: Launch the Dashboard
```bash
cd src
streamlit run app.py
```
Interactive web UI for real-time trading and monitoring.

### Option 3: Add Real Market Data
Get free API keys:
- [Alpha Vantage](https://www.alphavantage.co/api) – stock prices
- [NewsAPI](https://newsapi.org) – financial news

Update `src/market_data.py` with your keys and run the dashboard.

See [docs/API_SETUP.md](docs/API_SETUP.md) for detailed instructions.

## 💡 Key Features

### Sentiment-Driven Trading
```
News Input → Sentiment Score → Risk Update → Auto Orders
"Great earnings!" → +0.7 → 85% Risk → BUY signals
```

### Real-time Dashboard
- **Live Trading**: Paste news, execute trades with one click
- **Portfolio**: View positions, cash, and live prices
- **Trade History**: Complete log of all executions
- **Market Overview**: VIX, trends, performance charts
- **Auto-refresh**: 30-second continuous monitoring

### Multi-Symbol Trading
Trade multiple stocks simultaneously with automatic order generation for each symbol.

### Trade Recording
Every trade is recorded with:
- Symbol, action (buy/sell), quantity
- Execution price, timestamp
- Sentiment score at execution
- Total trade value

## 🧠 How It Works

### 1. Sentiment Analysis
- Scans text for keywords
- Scores: -1.0 (bearish) to +1.0 (bullish)
- Fast, deterministic, extensible to LLMs

### 2. Risk Adjustment
- Maps sentiment to risk level: `Risk = 0.5 + sentiment/2`
- Ranges from 0% (conservative) to 100% (aggressive)

### 3. Order Generation
- **Bullish** (+score > 0.3): Buy proportional to risk and cash
- **Bearish** (score < -0.3): Sell all positions
- **Neutral**: Hold

### 4. Execution & Tracking
- Executes orders with live prices
- Records full trade metadata
- Updates portfolio in real-time

## 📈 Example Workflow

### Input
```
"Tech stocks surge on AI breakthroughs. Market remains bullish."
```

### Processing
1. Sentiment Analysis: +0.8 (BULLISH)
2. Risk Update: 90% (aggressive)
3. Orders Drafted: BUY signals for AAPL, GOOGL, TSLA, MSFT
4. Trades Executed: ~$72,000 invested across 4 stocks

### Results
- Portfolio Value: $100,000 → $100,000+ (with new positions)
- Open Positions: 4 stocks
- Cash Remaining: ~$28,000
- Trade Count: 4 executed

## 🔧 Customization

### Change Traded Symbols
Edit `src/app.py` line ~30:
```python
st.session_state.watched_symbols = ["NVDA", "META", "AMZN"]
```

### Adjust Sentiment Thresholds
Edit `src/portfolio.py` lines 29-30:
```python
if sentiment_score > 0.5:  # More conservative (was 0.3)
    # BUY order
```

### Add More Keywords
Edit `src/sentiment.py` lines 20-26:
```python
if any(word in txt for word in ["good", "excellent", "bullish", "rally"]):
    score += 0.6
```

## 📚 Documentation

| Document | Content |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup with examples |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Architecture, features, workflow |
| [README.md](README.md) | Full documentation with algorithms |
| [docs/SENTIMENT_ANALYSIS.md](docs/SENTIMENT_ANALYSIS.md) | Mathematical formulas and LLM integration |
| [docs/API_SETUP.md](docs/API_SETUP.md) | How to get and use free API keys |
| [docs/LIVE_TRADING_GUIDE.md](docs/LIVE_TRADING_GUIDE.md) | Feature overview and best practices |

## 🎓 What You'll Learn

- Sentiment analysis from financial text
- Risk management algorithms
- Portfolio tracking and trade execution
- Web UI development with Streamlit
- Live API integration
- System design patterns

## 🚀 Next Steps

1. **Try it now**: `python src/demo.py`
2. **Explore the dashboard**: `streamlit run app.py`
3. **Read the docs**: Start with [QUICKSTART.md](QUICKSTART.md)
4. **Get real data**: Add API keys from [docs/API_SETUP.md](docs/API_SETUP.md)
5. **Customize**: Modify symbols, thresholds, or keywords
6. **Extend**: Add backtesting, more symbols, ML models, real trading

## 📋 Requirements

- Python 3.8+
- `pip install -r requirements.txt`

## ✨ Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Sentiment Analysis | ✅ Complete | Keyword-based, LLM-ready |
| Portfolio Management | ✅ Complete | Multi-symbol, trade history |
| Risk Adjustment | ✅ Complete | Dynamic, sentiment-driven |
| Order Generation | ✅ Complete | Automatic, threshold-based |
| Trade Execution | ✅ Complete | Recorded with full metadata |
| Live Price Fetching | ✅ Complete | Alpha Vantage API + mock fallback |
| Live News Fetching | ✅ Complete | NewsAPI integration |
| Streamlit Dashboard | ✅ Complete | 5 tabs, auto-refresh |
| Trade History | ✅ Complete | Full audit log |
| Mock Data | ✅ Complete | Works without API keys |
| Documentation | ✅ Complete | 5 comprehensive guides |

## 🏆 Status

✅ **Complete and Ready for Use**

All deliverables implemented and tested:
- Sentiment trading agent ✅
- Portfolio management dashboard ✅
- Demo with mock data ✅
- Sentiment analysis documentation ✅

---

## 🤔 Questions?

1. **How do I get started?** → Read [QUICKSTART.md](QUICKSTART.md)
2. **How does it work?** → Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
3. **How do I add real API keys?** → Read [docs/API_SETUP.md](docs/API_SETUP.md)
4. **How do I customize it?** → See "Customization" section above
5. **What's the full documentation?** → Read [README.md](README.md)

---

**Made with ❤️ for autonomous trading and sentiment analysis**

Stock Market Sentiment Agentic Trader v1.0
