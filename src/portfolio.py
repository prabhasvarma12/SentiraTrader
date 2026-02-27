import pandas as pd
import os
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime



@dataclass
class Trade:
    """Record of an executed trade."""
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: str
    sentiment_score: float
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp,
            "sentiment": self.sentiment_score,
            "value": self.quantity * self.price,
        }


@dataclass
class Position:
    symbol: str
    shares: float
    cost_basis: float


@dataclass
class Portfolio:
    cash: float = 100000.0
    positions: Dict[str, Position] = field(default_factory=dict)
    risk_level: float = 1.0  # 0.0 conservative, 1.0 aggressive
    trades: List[Trade] = field(default_factory=list)  # execution history
    price_provider = None  # optional live price provider
    ema_alpha: float = 0.2 # smoothing factor for risk updates
    raw_sentiment_ema: float = 0.0

    def __post_init__(self):
        """Load persistent holdings and trades from disk on boot."""
        self.load_from_csv()
        self.load_trades_from_csv()

    def load_from_csv(self):
        """Fetch existing holdings from the CSV to preserve historical setup."""
        import json
        is_cash_persisted = False
        if os.path.exists("data/account.json"):
            try:
                with open("data/account.json", "r") as f:
                    acc = json.load(f)
                    self.cash = acc.get("cash", 100000.0)
                    self.risk_level = acc.get("risk_level", 1.0)
                    is_cash_persisted = True
            except Exception:
                pass

        if os.path.exists("data/holdings.csv"):
            try:
                df = pd.read_csv("data/holdings.csv")
                for _, row in df.iterrows():
                    sym = str(row["Symbol"])
                    shares = float(row["Shares"])
                    cost = float(row["CostBasis"])
                    if shares > 0:
                        self.positions[sym] = Position(sym, shares, cost)
                        # Only mechanically deduct if we are upgrading an old save file
                        if not is_cash_persisted:
                            self.cash -= (shares * cost)
            except Exception:
                pass

    def load_trades_from_csv(self):
        """Fetch historical trades from the CSV to preserve the activity log."""
        if os.path.exists("data/activity_log.csv"):
            try:
                df = pd.read_csv("data/activity_log.csv")
                for _, row in df.iterrows():
                    trade = Trade(
                        symbol=str(row["symbol"]),
                        action=str(row["action"]),
                        quantity=float(row["quantity"]),
                        price=float(row["price"]),
                        timestamp=str(row["timestamp"]),
                        sentiment_score=float(row["sentiment"])
                    )
                    self.trades.append(trade)
            except Exception:
                pass

    def update_risk(self, sentiment_score: float):
        """Adjust the portfolio's risk level from sentiment using EMA.
        
        Uses an Exponential Moving Average to smooth out noise from single 
        news events and prevent extreme portfolio volatility.
        """
        # Update the raw EMA
        self.raw_sentiment_ema = (self.ema_alpha * sentiment_score) + ((1 - self.ema_alpha) * self.raw_sentiment_ema)
        
        # Calculate risk level (0.5 is neutral)
        self.risk_level = max(0.0, min(1.0, 0.5 + (self.raw_sentiment_ema / 2)))

    def draft_order(self, symbol: str, sentiment_score: float) -> Dict:
        """Draft a simple buy/sell order based on sentiment and risk.

        The size is proportional to available cash, risk level, and the 
        magnitude of the sentiment score itself.
        """
        order = {"symbol": symbol, "action": "hold", "quantity": 0}
        
        # Scale the order size by the absolute magnitude of the sentiment 
        # (stronger signal = larger position relative to risk allowance)
        magnitude_scalar = min(1.0, abs(sentiment_score))
        
        if sentiment_score > 0.3:
            # allocate a portion of allowable risk capital based on signal strength
            raw_target_spend = (self.cash * self.risk_level) * magnitude_scalar
            price = self.get_price(symbol)
            
            # CRITICAL: Hard cap the buy order against the actual remaining unallocated cash pool
            max_affordable_shares = self.cash / price if price > 0 else 0
            
            # Choose the smaller between algorithmic target vs raw wallet balance
            qty = min(raw_target_spend / price, max_affordable_shares) if price > 0 else 0
            qty = round(qty, 2)
            
            if qty > 0:
                order["action"] = "buy"
                order["quantity"] = qty
        
        elif sentiment_score < -0.3 and symbol in self.positions:
            # sell a portion of the position based on signal strength, or all if very strong
            pos = self.positions[symbol]
            if sentiment_score < -0.7:
                 quantity_to_sell = pos.shares # Liquidate
            else:
                 quantity_to_sell = pos.shares * magnitude_scalar
            
            order = {"symbol": symbol, "action": "sell", "quantity": quantity_to_sell}
            
        return order

    def sync_to_csv(self):
        """Dumps current holdings to a CSV file and updates account state."""
        import json
        os.makedirs("data", exist_ok=True)
        
        # Save unallocated cash and risk persistently
        with open("data/account.json", "w") as f:
            json.dump({"cash": self.cash, "risk_level": self.risk_level}, f)
            
        if not self.positions:
            pd.DataFrame(columns=["Symbol", "Shares", "CostBasis", "TotalCost"]).to_csv("data/holdings.csv", index=False)
            return
            
        data = []
        for sym, pos in self.positions.items():
            data.append({
                "Symbol": sym,
                "Shares": pos.shares,
                "CostBasis": pos.cost_basis,
                "TotalCost": pos.shares * pos.cost_basis
            })
            
        pd.DataFrame(data).to_csv("data/holdings.csv", index=False)

    def log_trade_to_csv(self, trade: Trade):
        """Appends a single executed trade to the activity log CSV."""
        os.makedirs("data", exist_ok=True)
        file_path = "data/activity_log.csv"
        
        # Format the trade dict specifically for the CSV
        trade_data = trade.to_dict()
        df = pd.DataFrame([trade_data])
        
        # Append without headers if file exists, else write with headers
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)

    def apply_order(self, order: Dict, sentiment_score: float = 0.0, manual_price: float = None):
        """Execute an order and record the trade."""
        if order["action"] == "buy":
            price = manual_price if manual_price is not None else self.get_price(order["symbol"])
            cost = order["quantity"] * price
            if cost <= self.cash:
                self.cash -= cost
                pos = self.positions.get(order["symbol"], Position(order["symbol"], 0, 0))
                total_shares = pos.shares + order["quantity"]
                pos.cost_basis = ((pos.cost_basis * pos.shares) + cost) / total_shares
                pos.shares = total_shares
                self.positions[order["symbol"]] = pos
                # Record trade
                trade = Trade(
                    symbol=order["symbol"],
                    action="buy",
                    quantity=order["quantity"],
                    price=price,
                    timestamp=datetime.now().isoformat(),
                    sentiment_score=sentiment_score
                )
                self.trades.append(trade)
                self.log_trade_to_csv(trade)
                self.sync_to_csv()
        elif order["action"] == "sell":
            if order["symbol"] in self.positions:
                pos = self.positions[order["symbol"]]
                price = manual_price if manual_price is not None else self.get_price(order["symbol"])
                proceeds = order["quantity"] * price
                self.cash += proceeds
                pos.shares -= order["quantity"]
                if pos.shares <= 0:
                    del self.positions[order["symbol"]]
                # Record trade
                trade = Trade(
                    symbol=order["symbol"],
                    action="sell",
                    quantity=order["quantity"],
                    price=price,
                    timestamp=datetime.now().isoformat(),
                    sentiment_score=sentiment_score
                )
                self.trades.append(trade)
                self.log_trade_to_csv(trade)
                self.sync_to_csv()

    def manually_update_position(self, symbol: str, quantity: float, cost_basis: float):
        """Allow the user to explicitly define a holding's quantity and cost, bypassing trade simulation."""
        old_cost = 0.0
        if symbol in self.positions:
            old_pos = self.positions[symbol]
            old_cost = old_pos.shares * old_pos.cost_basis
            del self.positions[symbol]
            
        if quantity > 0:
            new_cost = quantity * cost_basis
            self.positions[symbol] = Position(symbol, quantity, cost_basis)
            # Rebalance cash pool based on the delta between old and new state
            self.cash = self.cash + old_cost - new_cost
        else:
            # Full liquidation, return old cost to cash pool
            self.cash += old_cost
            
        self.sync_to_csv()
            
    def set_base_risk_level(self, risk_level: float):
        """Manually override or set the global risk level."""
        self.risk_level = max(0.0, min(1.0, risk_level))

    def get_price(self, symbol: str) -> float:
        """Fetch price for symbol. Uses live provider if available, else mock."""
        if self.price_provider:
            return self.price_provider.get_price(symbol)
        # Fallback: mock price with symbol-based variation
        return 100.0 + hash(symbol) % 50

    def total_value(self) -> float:
        """Compute current portfolio value (cash + positions)."""
        value = self.cash
        for pos in self.positions.values():
            value += pos.shares * self.get_price(pos.symbol)
        return value

    def snapshot(self) -> Dict:
        """Return a dict summarizing cash, positions, risk, and value."""
        return {
            "cash": self.cash,
            "positions": {s: p.shares for s, p in self.positions.items()},
            "risk_level": self.risk_level,
            "total_value": self.total_value(),
            "trades_count": len(self.trades),
        }

    def get_trades(self, limit: int = 10) -> List[Dict]:
        """Return the most recent trades."""
        return [t.to_dict() for t in self.trades[-limit:]]
