# 🚀 Quick Start Guide

Get your sentiment trading agent running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Terminal or command prompt

## Step 1: Install Dependencies (1 min)

```bash
# Navigate to project folder
cd project

# Install packages
pip install -r requirements.txt
```

## Step 2: Run the Demo (2 min)

See the agent in action with mock data:

```bash
cd src
python demo.py
```

**Expected Output:**
```
═══════════════════════════════════════════════════════════════════════════
STOCK MARKET SENTIMENT AGENTIC TRADER - DEMO
═══════════════════════════════════════════════════════════════════════════

Starting Portfolio Value: $100000.00
Initial Cash: $100000.00
Watched Symbols: AAPL, GOOGL, TSLA, MSFT

──────────────────────────────────────────────────────────────────────────
ROUND 1: News Event
...
```

✅ **If you see this, everything works!**

## Step 3: Launch the Dashboard (2 min)

Open the interactive web UI:

```bash
streamlit run app.py
```

This will open a browser window at `http://localhost:8501`

## Step 4: Try It Out

### In the Dashboard:

1. **Left sidebar**: Configure symbols (default: AAPL, GOOGL, TSLA, MSFT)
2. **Live Trading tab**: Paste a financial news snippet:
   ```
   Company reports excellent earnings, buy now!
   ```
   Click "Fetch & Analyze"
3. **Portfolio tab**: Watch your portfolio metrics update
4. **Trade History tab**: See all executed trades
5. **Market Overview tab**: View sentiment trends

## Example Trading Scenario

### Input Text:
```
Tech stocks are rallying as AI breakthrough announced. 
Strong buy signals across the sector.
```

### What Happens:
1. Sentiment: +0.7 (BULLISH 📈)
2. Risk Level: 85%
3. Orders Generated: BUY signals for all 4 symbols
4. Trades Executed: Shares purchased proportional to risk level
5. Portfolio Value: Increases with position value

## Next: Add Real API Keys (Optional)

Want live stock prices and news?

1. Get free API keys:
   - [Alpha Vantage](https://www.alphavantage.co/api) – stock prices
   - [NewsAPI](https://newsapi.org) – financial news

2. Update `src/market_data.py` (line 10 & 46):
   ```python
   ALPHA_VANTAGE_API_KEY = "your_key_here"
   NEWSAPI_KEY = "your_key_here"
   ```

3. Run demo or dashboard again – now with real data!

See [docs/API_SETUP.md](docs/API_SETUP.md) for details.

## Project Structure

```
src/
├── app.py           ← Run this: streamlit run app.py
├── demo.py          ← Run this: python demo.py
├── sentiment.py     ← Analyzes text sentiment
├── portfolio.py     ← Manages trades & positions
└── market_data.py   ← Fetches live prices & news

docs/
├── SENTIMENT_ANALYSIS.md  ← Algorithm details
├── API_SETUP.md           ← How to get API keys
└── LIVE_TRADING_GUIDE.md  ← Full feature overview
```

## Common Tasks

### Change the Symbols Being Traded

In `src/app.py` line ~30:
```python
st.session_state.watched_symbols = ["AAPL", "GOOGL", "TSLA", "MSFT"]
```

Change to:
```python
st.session_state.watched_symbols = ["NVDA", "META", "AMZN"]
```

### Adjust Risk Thresholds

In `src/portfolio.py` lines 29-30:
```python
if sentiment_score > 0.3:  # Change 0.3 to 0.5 for more conservative
    # BUY order generated
```

### Modify Sentiment Keywords

In `src/sentiment.py` lines ~20:
```python
if any(word in txt for word in ["good", "excellent", "bullish"]):
    score += 0.6
```

Add more keywords to detect.

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "requests.ConnectionError" or timeout errors
- APIs might be rate-limited
- System falls back to mock data automatically
- Wait 60 seconds and try again

### Dashboard won't open
```bash
# Make sure you're in src/ folder
cd src
streamlit run app.py
```

### Demo runs but all prices are the same
- Normal if you don't have API keys set
- Mock prices are deterministic (AAPL ≈ 125, GOOGL ≈ 150, etc.)
- Add real API keys to get variable prices

## Performance

| Action | Time |
|--------|------|
| Sentiment Analysis | < 10ms |
| Price Fetch | 200-500ms (cached) |
| Order Execution | < 1ms |
| Dashboard Load | 2-3 seconds |

## What's Next?

1. **Explore**: Try different market sentiments
2. **Customize**: Modify risk levels, symbols, thresholds
3. **Integrate**: Add real API keys from Alpha Vantage & NewsAPI
4. **Extend**: Add backtesting, more symbols, advanced ML models
5. **Deploy**: Host on cloud (Heroku, AWS, Google Cloud)

## Learning Resources

- **Algorithm Details**: [docs/SENTIMENT_ANALYSIS.md](docs/SENTIMENT_ANALYSIS.md)
- **Full Feature Guide**: [docs/LIVE_TRADING_GUIDE.md](docs/LIVE_TRADING_GUIDE.md)
- **API Integration**: [docs/API_SETUP.md](docs/API_SETUP.md)
- **Source Code**: Well-commented in `src/` folder

## Support

- Check README.md for full documentation
- Review source code comments for implementation details
- Visit API provider docs for integration help

---

**Ready?** Run this:

```bash
cd src
python demo.py
```

Then open the dashboard:

```bash
streamlit run app.py
```

Happy trading! 📊🚀
