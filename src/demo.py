"""Demo script generating mock sentiment data and exercising the agent with live trading."""
from sentiment import analyze_text_sentiment
from sentiment_engine import analyze_text
from portfolio import Portfolio
from market_data import PriceCache
import time

MOCK_TEXTS = [
    "Company reports excellent earnings, buy now!",
    "Rumors of leadership change, bearish outlook.",
    "Industry trend looks good, investors optimistic.",
    "Sell-off expected after regulatory news.",
    "Market remains neutral, no action recommended.",
]

SYMBOLS = ["AAPL", "GOOGL", "TSLA", "MSFT"]


def run_demo():
    port = Portfolio()
    port.price_provider = PriceCache()  # Use live price fetching
    
    print("=" * 70)
    print("STOCK MARKET SENTIMENT AGENTIC TRADER - DEMO")
    print("=" * 70)
    print(f"\nStarting Portfolio Value: ${port.total_value():.2f}")
    print(f"Initial Cash: ${port.cash:.2f}")
    print(f"Watched Symbols: {', '.join(SYMBOLS)}\n")
    
    for i, text in enumerate(MOCK_TEXTS, start=1):
        print(f"\n{'-' * 70}")
        print(f"ROUND {i}: News Event")
        print(f"{'-' * 70}")
        print(f"News: {text}")
        
        # Analyze sentiment
        result = analyze_text(text)
        score = result.get("score", 0.0)
        summary = result.get("summary", "")
        print(f"Summary: {summary}")
        print(f"Raw Sentiment Score: {score:.2f}", end="")
        if score > 0.3:
            print(" (BULLISH)")
        elif score < -0.3:
            print(" (BEARISH)")
        else:
            print(" (NEUTRAL)")
        
        # Update portfolio risk
        port.update_risk(score)
        print(f"EMA Smoothed Sentiment: {port.raw_sentiment_ema:.2f}")
        print(f"Risk Level Updated: {port.risk_level:.0%}")
        
        # Generate orders for each symbol
        print(f"\nGenerated Orders (scaled by signal magnitude):")
        for symbol in SYMBOLS:
            order = port.draft_order(symbol, score)
            price = port.get_price(symbol)
            
            if order["action"] != "hold":
                print(f"  - {order['action'].upper():4s} {order['quantity']:8.2f} shares of {symbol} @ ${price:.2f}")
                port.apply_order(order, sentiment_score=score)
                trade = port.trades[-1]
                trade_value = trade.quantity * trade.price
                print(f"             Executed | Trade Value: ${trade_value:.2f}")
                print(f"  - {order['action'].upper():4s} {symbol} (Price: ${price:.2f})")
        
        # Show portfolio status
        print(f"\nPortfolio Status:")
        print(f"  Cash: ${port.cash:>12.2f}")
        print(f"  Total Value: ${port.total_value():>8.2f}")
        print(f"  Positions: {len(port.positions)} open")
        if port.positions:
            for symbol, pos in port.positions.items():
                price = port.get_price(symbol)
                print(f"    - {symbol}: {pos.shares:.2f} shares @ ${price:.2f} = ${pos.shares * price:.2f}")
        
        time.sleep(0.5)  # brief pause between rounds
    
    print(f"\n\n{'=' * 70}")
    print("FINAL RESULTS")
    print(f"{'=' * 70}")
    print(f"Total Trades Executed: {len(port.trades)}")
    print(f"Final Portfolio Value: ${port.total_value():.2f}")
    print(f"Remaining Cash: ${port.cash:.2f}")
    print(f"Final Risk Level: {port.risk_level:.0%}")
    
    if port.positions:
        print(f"\nOpen Positions:")
        for symbol, pos in port.positions.items():
            price = port.get_price(symbol)
            print(f"  {symbol}: {pos.shares:.2f} shares @ ${price:.2f}")
    
    print(f"\nTrade Summary:")
    buys = [t for t in port.trades if t.action == 'buy']
    sells = [t for t in port.trades if t.action == 'sell']
    print(f"  Total Buys: {len(buys)}")
    print(f"  Total Sells: {len(sells)}")
    if port.trades:
        total_volume = sum([t.quantity * t.price for t in port.trades])
        print(f"  Total Trading Volume: ${total_volume:.2f}")
    
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    run_demo()
