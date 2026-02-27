import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from sentiment import fetch_mock_news
from sentiment_engine import analyze_text
from portfolio import Portfolio
from market_data import PriceCache, fetch_live_news_sentiments, fetch_market_overview
import math
import os
from dotenv import load_dotenv
load_dotenv()

def inject_custom_css():
    st.markdown("""
        <style>
        /* Base styling for the Kite aesthetic */
        .stApp {
            background-color: #f9f9f9;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #444;
        }
        
        /* Top Navigation styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid #eeeeee;
            padding-bottom: 0px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 0;
            color: #666;
            font-weight: 500;
            font-size: 15px;
            text-transform: capitalize;
        }
        .stTabs [aria-selected="true"] {
            color: #ff5722 !important;
            border-bottom: 2px solid #ff5722 !important;
        }
        
        /* Sidebar (Watchlist) styling */
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid #eee;
        }
        .watchlist-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            border-bottom: 1px solid #f1f1f1;
            cursor: pointer;
            transition: background 0.2s;
        }
        .watchlist-item:hover {
            background-color: #f8f8f8;
        }
        .wl-symbol {
            font-weight: 500;
            font-size: 13px;
        }
        .wl-price-container {
            text-align: right;
            font-size: 12px;
        }
        .wl-price {
            font-weight: 500;
        }
        .wl-change {
            font-size: 11px;
            margin-left: 8px;
        }
        .green-text { color: #4caf50; }
        .red-text { color: #e53935; }
        .neutral-text { color: #999; }
        
        /* Dashboard Cards */
        .kite-card {
            background: white;
            border: 1px solid #eaeaea;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 400;
            color: #444;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Large numbers */
        .big-number {
            font-size: 42px;
            font-weight: 300;
            line-height: 1;
            margin-bottom: 4px;
            color: #444;
        }
        .sub-label {
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }
        
        /* PnL specific styling */
        .pnl-loss { color: #e53935; }
        .pnl-profit { color: #4caf50; }
        
        .greeting {
            font-size: 28px;
            font-weight: 400;
            color: #444;
            margin-bottom: 32px;
            margin-top: 16px;
        }
        
        /* Utility */
        .divider-vertical {
            border-left: 1px solid #eee;
            height: 100%;
            margin: 0 24px;
        }
        
        .small-metric {
            font-size: 13px;
            color: #666;
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px dashed #eee;
        }
        .small-metric strong {
            font-weight: 500;
            color: #333;
        }
        
        .view-statement {
            color: #2196f3;
            font-size: 13px;
            text-decoration: none;
            cursor: pointer;
            margin-top: 8px;
            display: inline-block;
        }

        /* News Feed Cards */
        .news-card {
            background: white;
            border: 1px solid #eee;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: box-shadow 0.2s;
        }
        .news-card:hover {
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .news-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .news-symbol {
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }
        .sentiment-badge {
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }
        .sentiment-bullish { background: #e8f5e9; color: #4caf50; border: 1px solid #4caf50; }
        .sentiment-bearish { background: #ffebee; color: #e53935; border: 1px solid #e53935; }
        .sentiment-neutral { background: #f5f5f5; color: #757575; border: 1px solid #9e9e9e; }
        .news-snippet {
            font-size: 13px;
            color: #555;
            line-height: 1.4;
        }
        .news-action {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px dashed #eee;
            font-size: 12px;
        }
    """, unsafe_allow_html=True)


def render_sidebar_watchlist(port: Portfolio, symbols: list):
    st.sidebar.markdown(f"<div style='padding: 16px; font-size: 12px; color: #888;'>Watchlist ({len(symbols)}/50)</div>", unsafe_allow_html=True)
    
    # Dynamic Search Bar hooking into Yahoo Finance native ticker resolution
    search_q = st.sidebar.text_input("Search Company / Ticker", placeholder="e.g. NVIDIA or NVDA", key="wl_search_input")
    if st.sidebar.button("🔍 Search", use_container_width=True):
        if search_q.strip():
            import requests
            try:
                res = requests.get(f"https://query2.finance.yahoo.com/v1/finance/search?q={search_q.strip()}", headers={'User-Agent': 'Mozilla/5.0'}).json()
                quotes = res.get('quotes', [])
                if quotes:
                    st.session_state.wl_search_results = [(q.get('symbol', ''), q.get('shortname', q.get('symbol', ''))) for q in quotes if 'symbol' in q][:5]
                else:
                    st.session_state.wl_search_results = []
                    st.sidebar.error("No results found.")
            except Exception:
                st.session_state.wl_search_results = []
                st.sidebar.error("Search API failed.")

    # Render Active Search Results Context Menu
    if "wl_search_results" in st.session_state and st.session_state.wl_search_results:
        st.sidebar.markdown("<div style='font-size: 11px; color: #666; margin-top: 4px; border-bottom: 1px solid #eee; padding-bottom: 4px;'>Search Results:</div>", unsafe_allow_html=True)
        for sym, name in st.session_state.wl_search_results:
            col_name, col_add = st.sidebar.columns([4, 1])
            with col_name:
                short_name = name[:20] if name else sym
                st.markdown(f"<div style='font-size: 12px; margin-top: 6px;'><b>{sym}</b><br><span style='color: #888;'>{short_name}</span></div>", unsafe_allow_html=True)
            with col_add:
                if st.button("➕", key=f"add_search_{sym}"):
                    if sym not in st.session_state.watched_symbols:
                        st.session_state.watched_symbols.append(sym)
                    st.session_state.wl_search_results = None # Hide the menu after add
                    st.rerun()
                
    st.sidebar.markdown("<div style='background: white; border-top: 1px solid #eee; margin-top: 8px;'></div>", unsafe_allow_html=True)
    
    # Re-fetch the updated list references if mutated
    symbols = list(st.session_state.watched_symbols)
    
    for symbol in symbols:
        price, chg_abs, chg_perc = port.price_provider.get_price_and_change(symbol)
        
        color_cls = "green-text" if chg_abs > 0 else "red-text" if chg_abs < 0 else "neutral-text"
        arrow = "▲" if chg_abs > 0 else "▼" if chg_abs < 0 else ""
        
        col_data, col_btn = st.sidebar.columns([5, 1])
        with col_data:
            st.markdown(f"""<div style="padding: 6px 0; margin-top: -8px; display: flex; justify-content: space-between; font-size: 13px; align-items: center; border-bottom: 1px solid #f9f9f9;">
                <span class="{color_cls}" style="font-weight: 600;">{symbol}</span>
                <span>
                    <span class="{color_cls}" style="font-size: 11px;">{chg_abs:+.2f} {chg_perc:+.2f}% {arrow}</span>
                    <span class="{color_cls}" style="margin-left: 8px; font-weight: 500;">{price:.2f}</span>
                </span>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            if st.button("✖", key=f"del_{symbol}"):
                if symbol in st.session_state.watched_symbols:
                    st.session_state.watched_symbols.remove(symbol)
                    st.rerun()
    
    st.sidebar.divider()
    
    st.sidebar.markdown("<div style='padding: 0 16px;'><strong style='font-size:12px;color:#666;'>AGENT CONTROLS</strong></div>", unsafe_allow_html=True)
    fully_autonomous = st.sidebar.toggle("Autonomous Execution", help="Agent will trade automatically on strong sentiment signals")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
    
    st.sidebar.divider()
    st.sidebar.markdown(
        """
        <div style='padding: 0 16px;'>
            <strong style='font-size:12px;color:#666;'>SYSTEM CAPABILITIES</strong>
            <ul style='font-size: 11px; color: #777; padding-left: 16px; margin-top: 8px; line-height: 1.5;'>
                <li>Automate sentiment-driven trading decisions</li>
                <li>Monitor market sentiment in real-time</li>
                <li>Adjust portfolio risk dynamically</li>
                <li>Demonstrate agentic trading logic</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )

    return fully_autonomous, auto_refresh

def main():
    st.set_page_config(page_title="Portfolio Tracker AI", layout="wide", initial_sidebar_state="expanded")
    inject_custom_css()

    # Initialize State
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = Portfolio()
        st.session_state.portfolio.price_provider = PriceCache()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "watched_symbols" not in st.session_state:
        st.session_state.watched_symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
            "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
            "BAJFINANCE.NS", "KOTAKBANK.NS", "AXISBANK.NS", "ASIANPAINT.NS", 
            "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", 
            "WIPRO.NS", "NESTLEIND.NS", "HCLTECH.NS", "ONGC.NS", "ADANIENT.NS", 
            "NTPC.NS", "POWERGRID.NS", "M&M.NS", "BAJAJFINSV.NS", "JSWSTEEL.NS", 
            "TATASTEEL.NS", "COALINDIA.NS", "BRITANNIA.NS", "HINDALCO.NS", "TECHM.NS", 
            "INDUSINDBK.NS", "EICHERMOT.NS", "DRREDDY.NS", "CIPLA.NS", "GRASIM.NS"
        ] # Expanded for robust tracker look in Rupees
    port = st.session_state.portfolio
    snap = port.snapshot()

    # Render Header Custom CSS padding
    st.markdown('<div style="margin-top: -30px;"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #333; margin-bottom: 20px;'>SentiraTrader</h1>", unsafe_allow_html=True)

    # Sidebar
    fully_autonomous, auto_refresh = render_sidebar_watchlist(port, st.session_state.watched_symbols)

    # Main Top Navigation
    t_dash, t_holdings, t_orders, t_chatbot, t_positions, t_agent, t_profile = st.tabs(["Overview", "Current Portfolio", "Activity Log", "AI Assistant", "Technical Charts", "Live Sentinel Engine", "Tracker Settings"])

    # -------------------------------------------------------------
    # TAB 1: OVERVIEW
    # -------------------------------------------------------------
    with t_dash:
        st.markdown('<div class="greeting">Portfolio Overview</div>', unsafe_allow_html=True)
        
        # Upper Section: Equity & Commodity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""<div class="kite-card">
    <div class="card-title">⚇ Tracking Summary</div>
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <div class="big-number">{val}</div>
            <div class="sub-label">Total Tracked Value</div>
        </div>
        <div style="width: 200px;">
            <div class="small-metric"><span>Unallocated Cash</span> <strong>{cash}</strong></div>
            <div class="small-metric"><span>Total Activity</span> <strong>{trades} events</strong></div>
        </div>
    </div>
</div>""".format(val=f"₹{snap['total_value']:,.2f}", cash=f"₹{snap['cash']:,.2f}", trades=snap['trades_count']), unsafe_allow_html=True)

        with col2:
             # Repurposing Commodity block for "AI Trade Suggestions & Social Sentiment"
             st.markdown('<div class="kite-card">', unsafe_allow_html=True)
             st.markdown('<div class="card-title">🤖 AI Trade Suggestions & Social Sentiment</div>', unsafe_allow_html=True)
             
             try:
                 with open("data/social_media.txt", "r") as f:
                     social_chat = f.readlines()[-3:] # get latest 3
             except:
                 social_chat = ["[10:00 AM] @market_bot: Waiting for data stream..."]
                 
             st.markdown('<div style="font-size: 13px; color: #666; font-weight: 500; margin-bottom: 8px;">Latest Social Chatter:</div>', unsafe_allow_html=True)
             for chat in social_chat:
                 st.markdown(f'<div style="font-size: 12px; color: #555; background: #f9f9f9; padding: 6px; border-left: 2px solid #2196f3; margin-bottom: 4px;">{chat.strip()}</div>', unsafe_allow_html=True)
                 
             st.markdown('<div style="font-size: 13px; color: #666; font-weight: 500; margin-top: 16px; margin-bottom: 8px;">Top AI Conviction Signals:</div>', unsafe_allow_html=True)
             
             # Calculate quick convictions
             convictions = []
             for sym in st.session_state.watched_symbols[:3]: # check top 3
                  score = hash(sym) % 100 / 100.0 * 2 - 1 # deterministic mock score for preview
                  action = "BUY" if score > 0.3 else "SELL" if score < -0.3 else "HOLD"
                  color = "#4caf50" if action == "BUY" else "#e53935" if action == "SELL" else "#9e9e9e"
                  convictions.append(f'<span style="display:inline-block; padding: 2px 8px; border-radius: 2px; font-size: 11px; font-weight: 600; color: white; background: {color}; margin-right: 8px;">{action} {sym}</span>')
             
             st.markdown(" ".join(convictions), unsafe_allow_html=True)
             st.markdown('</div>', unsafe_allow_html=True)

        # Lower Section: Holdings Summary
        num_holdings = len(snap['positions'])
        total_inv = 0
        total_curr = 0
        
        pie_data = [] # Data for interactive chart
        
        for sym, shares in snap['positions'].items():
            price = port.get_price(sym)
            val = shares * price
            total_curr += val
            total_inv += val * 1.05  
            pie_data.append({"Symbol": sym, "Value": val})
            
        pnl = total_curr - total_inv
        pnl_perc = (pnl / total_inv * 100) if total_inv > 0 else 0
        pnl_class = "pnl-profit" if pnl >= 0 else "pnl-loss"
        pnl_sign = "+" if pnl > 0 else ""

        st.markdown(f"""<div class="kite-card" style="margin-bottom: 0;">
    <div class="card-title">💼 Holdings ({num_holdings})</div>
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <span class="big-number {pnl_class}">{pnl_sign}{pnl:,.2f}</span>
            <span class="{pnl_class}" style="font-size: 14px; margin-left:8px;">{pnl_sign}{pnl_perc:.2f}%</span>
            <div class="sub-label" style="margin-top:8px;">P&L</div>
        </div>
        <div style="width: 300px;">
            <div class="small-metric" style="border:none; margin-bottom:4px; padding-bottom:0;">
                <span>Current value</span> <strong>{total_curr/1000:.2f}k</strong>
            </div>
            <div class="small-metric" style="border:none; margin-bottom:0; padding-bottom:0;">
                <span>Investment</span> <strong style="color:#888;">{total_inv/1000:.2f}k</strong>
            </div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
        
        # Interactive Asset Allocation Chart using Plotly
        if pie_data:
            df_pie = pd.DataFrame(pie_data)
            fig = px.pie(
                df_pie, 
                values='Value', 
                names='Symbol',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            # The Plotly pie chart renders beautifully natively without a wrapper
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


    # -------------------------------------------------------------
    # TAB 2: ACTIVITY LOG (Trade History mapped here)
    # -------------------------------------------------------------
    with t_orders:
        if not port.trades:
            st.info("No tracking activity recorded today")
        else:
            trades = port.get_trades(limit=50)
            df_trades = pd.DataFrame(trades)
            df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp']).dt.strftime('%H:%M:%S')
            df_trades['action'] = df_trades['action'].str.upper()
            df_trades['Status'] = "COMPLETE"
            
            # Reorder for display
            df_display = df_trades[['timestamp', 'action', 'symbol', 'quantity', 'price', 'Status']]
            df_display.columns = ['Time', 'Type', 'Instrument', 'Qty.', 'Avg. Price', 'Status']
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=400,
                column_config={
                    "Type": st.column_config.TextColumn("Type"),
                    "Qty.": st.column_config.NumberColumn("Qty.", format="%.2f"),
                    "Avg. Price": st.column_config.NumberColumn("Avg. Price", format="₹%.2f")
                }
            )
        # Removed dangling div


    # -------------------------------------------------------------
    # TAB 4: CHATBOT ASSISTANT
    # -------------------------------------------------------------
    with t_chatbot:
        st.markdown('<div class="kite-card">', unsafe_allow_html=True)
        st.subheader("💬 Active Trading Co-Pilot")
        st.write("Talk to Gemini 2.5 Flash about your portfolio, market news, or request technical analysis explanations.")
        
        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "How can I help you analyze the market today?"}
            ]

        # Render existing messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Ask Gemini about your positions..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Gemini is thinking..."):
                    try:
                        from google import genai
                        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                        
                        # Provide the LLM with the active portfolio logic so it actually knows the user
                        system_context = f"You are an expert quantitative trader and financial advisor. The user's current portfolio snapshot is: {snap}. Be concise and professional."
                        full_prompt = f"{system_context}\n\nUser Question: {prompt}"
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=full_prompt,
                        )
                        full_response = response.text
                        message_placeholder.markdown(full_response)
                        
                        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        error_msg = f"Sorry, the Gemini API encountered an error: {e}"
                        message_placeholder.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        st.markdown('</div>', unsafe_allow_html=True)


    # -------------------------------------------------------------
    # TAB 5: CURRENT PORTFOLIO
    # -------------------------------------------------------------
    with t_holdings:
        if not snap['positions']:
            st.info("No holdings found")
        else:
            holdings_data = []
            for sym, shares in snap['positions'].items():
                ltp, chg_abs, chg_perc = port.price_provider.get_price_and_change(sym)
                avg_cost = port.positions[sym].cost_basis
                cur_val = shares * ltp
                pnl = (ltp - avg_cost) * shares
                net_chg_perc = (pnl / (avg_cost*shares) * 100) if avg_cost > 0 else 0
                
                holdings_data.append({
                    "Instrument": sym,
                    "Qty.": shares,
                    "Avg. cost": avg_cost,
                    "LTP": ltp,
                    "Cur. val": cur_val,
                    "P&L": pnl,
                    "Net chg.": net_chg_perc,
                    "Day chg.": chg_perc
                })
                
            df_holdings = pd.DataFrame(holdings_data)
            
            st.dataframe(
                df_holdings,
                use_container_width=True,
                hide_index=True,
                height=500,
                column_config={
                    "Qty.": st.column_config.NumberColumn("Qty.", format="%.2f"),
                    "Avg. cost": st.column_config.NumberColumn("Avg. cost", format="₹%.2f"),
                    "LTP": st.column_config.NumberColumn("LTP", format="₹%.2f"),
                    "Cur. val": st.column_config.NumberColumn("Cur. val", format="₹%.2f"),
                    "P&L": st.column_config.NumberColumn("P&L", format="₹%.2f"),
                    "Net chg.": st.column_config.NumberColumn("Net chg.", format="%.2f%%"),
                    "Day chg.": st.column_config.NumberColumn("Day chg.", format="%.2f%%")
                }
            )
        # Removed dangling div


    # -------------------------------------------------------------
    # TAB 4: POSITIONS (Trading View Chart)
    # -------------------------------------------------------------
    with t_positions:
        # Re-using this tab for the advanced TV chart requested earlier
        st.markdown('<div style="font-size:18px; color:#444; margin-bottom:16px;">Technical Analysis</div>', unsafe_allow_html=True)
        tv_symbol = st.selectbox("Select TV Symbol for Chart", st.session_state.watched_symbols, label_visibility="collapsed")
        
        # Safely map Yahoo Finance tickers to TradingView tickers
        # TradingView restricts free widgets from embedding NSE data, but allows BSE data.
        # Since the tickers are identical, we route everything through BSE for charting.
        if tv_symbol.endswith('.NS'):
            chart_symbol = "BSE:" + tv_symbol.replace('.NS', '')
        elif tv_symbol.endswith('.BO'):
            chart_symbol = "BSE:" + tv_symbol.replace('.BO', '')
        else:
            # Assume it's a standard US ticker (like AAPL) that TradingView can auto-resolve
            chart_symbol = "NASDAQ:" + tv_symbol if len(tv_symbol) <= 4 else tv_symbol
        
        st.components.v1.html(f'''
            <div class="tradingview-widget-container" style="aspect-ratio: 2 / 1; width: 100%;">
              <div id="tradingview_chart" style="height: 100%; width: 100%;"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
              "autosize": true,
              "symbol": "{chart_symbol}",
              "interval": "D",
              "timezone": "Etc/UTC",
              "theme": "light",
              "style": "1",
              "locale": "en",
              "enable_publishing": false,
              "backgroundColor": "#ffffff",
              "gridColor": "#f1f3f6",
              "hide_top_toolbar": false,
              "hide_legend": false,
              "save_image": false,
              "container_id": "tradingview_chart"
            }}
              );
              </script>
            </div>
        ''', height=900)
        
        st.markdown('<div class="kite-card" style="margin-top: 16px;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧠 AI Chart Confluence & Next Move</div>', unsafe_allow_html=True)
        st.write(f"Generate an on-demand AI prediction for **{tv_symbol}** based on live news flow and momentum.")
        
        if st.button(f"Generate AI Suggestion for {tv_symbol}", type="primary", use_container_width=True):
            with st.spinner(f"Gemini analyzing {tv_symbol}..."):
                # Fetch recent news context
                news_data = fetch_live_news_sentiments([tv_symbol])
                context_str = news_data.get(tv_symbol, "No recent news found. Analyzing purely on momentum.")
                
                # Force Gemini to output a definitive directional move
                ltp, _, _ = port.price_provider.get_price_and_change(tv_symbol)
                prompt = f"The stock {tv_symbol} is currently trading at {ltp}. Recent news context: '{context_str}'. Synthesize this data and provide a strict recommendation. You MUST start your response with exactly one of these words: [BUY], [SELL], or [HOLD], followed by a 2-sentence explanation of why."
                
                try:
                    from google import genai
                    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    
                    ans = response.text.strip()
                    
                    # Parse color formatting based on string start
                    color = "#555"
                    bg = "#f5f5f5"
                    if ans.upper().startswith("[BUY]") or ans.upper().startswith("BUY"):
                        color = "#4caf50"
                        bg = "#e8f5e9"
                    elif ans.upper().startswith("[SELL]") or ans.upper().startswith("SELL"):
                        color = "#e53935"
                        bg = "#ffebee"
                        
                    st.markdown(f'<div style="padding: 16px; border-radius: 4px; border-left: 4px solid {color}; background-color: {bg}; color: #333; font-weight: 500; font-size: 14px;">Next Move Suggestion:<br><br>{ans}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"AI API Error: {e}")
                    
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 5: AI SENTIMENT ENGINE (Logic controls)
    # -------------------------------------------------------------
    with t_agent:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown('<div class="kite-card">', unsafe_allow_html=True)
            st.subheader("📰 Live Market Sentiment Feed")
            st.write("Aggregates real-time news for watchlist and scores sentiment.")
            
            st.markdown('<div class="kite-card" style="background: #fff9e6; border-left: 4px solid #ffbc00;">', unsafe_allow_html=True)
            auto_scan = st.checkbox("🤖 Enable Autonomous AI News Sentinel", value=False, help="When enabled alongside the 30s auto-refresh, the Agent will continuously scan live feeds in the background.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if auto_scan or st.button("Fetch & Analyze Single Batch", type="primary", use_container_width=True):
                import random
                # Randomly sample 2 symbols to respect the Gemini API rate limits on auto-refresh loops
                scan_symbols = random.sample(st.session_state.watched_symbols, min(2, len(st.session_state.watched_symbols)))
                
                with st.spinner(f"Agent actively scraping feeds for {', '.join(scan_symbols)}..."):
                    news_data = fetch_live_news_sentiments(scan_symbols)
                    
                    if not news_data:
                        st.info("No fresh news available right now.")
                    else:
                        for symbol, content in news_data.items():
                            if content and "Mock market news" not in content:
                                # Score the news via live Gemini API
                                result = analyze_text(content)
                                score = result.get("score", 0.0)
                                summary = result.get("summary", "")
                                
                                # Process the Portfolio Risk Engine adjustments
                                st.session_state.portfolio.update_risk(score)
                                
                                # Determine coloring schema for UI badge
                                badge_class = "sentiment-bullish" if score > 0.3 else "sentiment-bearish" if score < -0.3 else "sentiment-neutral"
                                badge_text = "Bullish" if score > 0.3 else "Bearish" if score < -0.3 else "Neutral"
                                
                                # Render Professional Card output
                                html = f"""<div class="news-card">
    <div class="news-header">
        <span class="news-symbol">{symbol}</span>
        <span class="sentiment-badge {badge_class}">{badge_text} ({score:.2f})</span>
    </div>
    <div class="news-snippet" style="font-weight: 500; margin-bottom: 8px;">Agent Summary: {summary}</div>
    <div class="news-snippet">{content[:250]}...</div>
    <div class="news-action">
        <span style="color:#888;">Live Gemini Flash Execution</span>
    </div>
</div>"""
                                st.markdown(html, unsafe_allow_html=True)
                                
                                # Auto Execute logic
                                order = st.session_state.portfolio.draft_order(symbol, score)
                                price = st.session_state.portfolio.get_price(symbol)
                                
                                if order["action"] != "hold":
                                    auto_exec = fully_autonomous and abs(score) >= 0.7
                                    if auto_exec:
                                        st.session_state.portfolio.apply_order(order, sentiment_score=score)
                                        snap = st.session_state.portfolio.snapshot()
                                        snap["timestamp"] = time.time()
                                        snap["sentiment"] = score
                                        st.session_state.history.append(snap)
                                        st.success(f"🤖 AUTO-TRACK: {order['action'].upper()} {order['quantity']:.2f} {symbol}")
                                    else:
                                        if st.button(f"Record {order['action'].upper()} {symbol} (LTP ₹{price:.2f})", key=f"ex_{symbol}_{time.time()}"):
                                            st.session_state.portfolio.apply_order(order, sentiment_score=score)
                                            snap = st.session_state.portfolio.snapshot()
                                            snap["timestamp"] = time.time()
                                            snap["sentiment"] = score
                                            st.session_state.history.append(snap)
                                            st.success(f"Recorded {order['action']} on {symbol}")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="kite-card">', unsafe_allow_html=True)
            st.subheader("🐦 Social Media Sentiment Stream")
            st.write("Stream unstructured social data (X/Discord) directly into the LLM logic engine.")
            # Read all social media lines and display them concurrently
            try:
                with open("data/social_media.txt", "r", encoding="utf-8") as f:
                    social_feed = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                social_feed = []
            
            if not social_feed:
                st.warning("No social media feed data found in data/social_media.txt")
            else:
                if "grouped_social_feed" not in st.session_state:
                    st.session_state.grouped_social_feed = None
                    
                col_btn1, col_btn2 = st.columns([2,1])
                with col_btn1:
                    if st.button("Analyze & Group Entire Feed via Gemini", type="primary", use_container_width=True):
                        with st.spinner("Aggregating sentiment streams..."):
                            grouped_data = {}
                            
                            for current_post in social_feed:
                                result = analyze_text(current_post)
                                score = result.get("score", 0.0)
                                summary = result.get("summary", "")
                                
                                mentioned_symbols = []
                                for symbol in st.session_state.watched_symbols:
                                    ticker = symbol.split('.')[0]
                                    if f"${ticker}" in current_post or ticker in current_post:
                                        mentioned_symbols.append(symbol)
                                
                                if not mentioned_symbols:
                                    mentioned_symbols = ["GENERAL MARKET"]
                                    
                                for symbol in mentioned_symbols:
                                    if symbol not in grouped_data:
                                        grouped_data[symbol] = {'posts': [], 'total_score': 0.0, 'count': 0}
                                    grouped_data[symbol]['posts'].append({'text': current_post, 'score': score, 'summary': summary})
                                    grouped_data[symbol]['total_score'] += score
                                    grouped_data[symbol]['count'] += 1
                            
                            st.session_state.grouped_social_feed = grouped_data
                            st.rerun()
                with col_btn2:
                    if st.session_state.grouped_social_feed is not None:
                        if st.button("Reset Feed Data"):
                            st.session_state.grouped_social_feed = None
                            st.rerun()

                if st.session_state.grouped_social_feed is not None:
                    for symbol, data in st.session_state.grouped_social_feed.items():
                        avg_score = data['total_score'] / data['count']
                        st.session_state.portfolio.update_risk(avg_score)
                        
                        badge_text = "Bullish" if avg_score > 0.3 else "Bearish" if avg_score < -0.3 else "Neutral"
                        badge_color = "#4caf50" if avg_score > 0.3 else "#e53935" if avg_score < -0.3 else "#777"
                        
                        with st.expander(f"📊 {symbol} | Combined Sentiment: {badge_text} ({avg_score:.2f})", expanded=True):
                            for p in data['posts']:
                                st.markdown(f"**Intercept:** {p['text']}<br><span style='color:#666;font-size:12px;'>*Agent Summary:* {p['summary']} (Score: {p['score']:.2f})</span>", unsafe_allow_html=True)
                                st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)
                            
                            if symbol != "GENERAL MARKET":
                                order = st.session_state.portfolio.draft_order(symbol, avg_score)
                                price = st.session_state.portfolio.get_price(symbol)
                                
                                if order["action"] != "hold":
                                    st.markdown(f"<strong style='color:{badge_color}'>Aggregated Draft: {order['action'].upper()} {order['quantity']:.2f} shares @ ₹{price:.2f}</strong>", unsafe_allow_html=True)
                                    if st.button(f"Record {order['action'].upper()} {symbol}", key=f"soc_exec_{symbol}_agg"):
                                        st.session_state.portfolio.apply_order(order, sentiment_score=avg_score)
                                        st.success(f"Executed aggregated {order['action']} on {symbol}")
                else:
                    st.write("Raw Feed Pending Analysis:")
                    for current_post in social_feed:
                        st.markdown(f'<div style="font-size: 13px; color: #555; background: #f9f9f9; padding: 8px; border-left: 3px solid #ccc; margin-bottom: 8px;">{current_post}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="kite-card">', unsafe_allow_html=True)
            st.subheader("Agent Risk Posture")
            current_ema = st.session_state.portfolio.raw_sentiment_ema
            st.metric("EMA Global Sentiment", f"{current_ema:.2f}")
            st.metric("Aggregate Risk Exposure Level", f"{st.session_state.portfolio.risk_level:.0%}")
            
            # Simple progress bar replacement using custom HTML
            risk_pct = st.session_state.portfolio.risk_level * 100
            st.markdown(f'''<div style="width: 100%; background-color: #f1f1f1; border-radius: 4px; height: 16px; margin-top: 8px;">
    <div style="width: {risk_pct}%; background-color: #ff5722; height: 100%; border-radius: 4px; transition: width 0.3s;"></div>
</div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 6: TRACKER SETTINGS
    # -------------------------------------------------------------
    with t_profile:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="kite-card">', unsafe_allow_html=True)
            st.subheader("⚙️ AI Signal Aggressiveness")
            st.write("Manually override the AI's baseline signal required to trigger an actionable tracking event.")
            
            # Risk Slider
            current_risk = st.session_state.portfolio.risk_level
            new_risk = st.slider("Base Risk Level", min_value=0.0, max_value=1.0, value=current_risk, step=0.05, format="%.2f")
            
            if st.button("Update Risk Posture", type="primary", use_container_width=True):
                st.session_state.portfolio.set_base_risk_level(new_risk)
                st.success(f"Base risk updated to {new_risk:.0%}")
                
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="kite-card">', unsafe_allow_html=True)
            st.subheader("💼 Manual Trading Desk")
            st.write("Execute custom Buy or Sell orders to manually manage your portfolio.")
            
            m_sym = st.selectbox("Instrument Symbol", st.session_state.watched_symbols)
            
            c1, c2 = st.columns(2)
            with c1:
                m_qty = st.number_input("Quantity", min_value=0.01, step=1.0)
            with c2:
                m_price = st.number_input("Execution Price (₹)", min_value=0.01, step=1.0)
                
            col_buy, col_sell = st.columns(2)
            
            with col_buy:
                if st.button("Record Manual Buy", type="secondary", use_container_width=True):
                    if m_sym and m_qty > 0:
                        order = {"symbol": m_sym, "action": "buy", "quantity": m_qty}
                        # Route through apply_order with the manual_price override
                        st.session_state.portfolio.apply_order(order, sentiment_score=0.0, manual_price=m_price)
                        st.success(f"Bought {m_qty} shares of {m_sym} @ ₹{m_price:.2f}")
                    else:
                        st.error("Invalid symbol or quantity.")
                        
            with col_sell:
                if st.button("Record Manual Sell", type="primary", use_container_width=True):
                    if m_sym and m_qty > 0:
                        port = st.session_state.portfolio
                        if m_sym not in port.positions or port.positions[m_sym].shares < m_qty:
                            st.error(f"Cannot sell {m_qty}. Insufficient shares.")
                        else:
                            order = {"symbol": m_sym, "action": "sell", "quantity": m_qty}
                            port.apply_order(order, sentiment_score=0.0, manual_price=m_price)
                            st.success(f"Sold {m_qty} shares of {m_sym} @ ₹{m_price:.2f}")
                    else:
                        st.error("Invalid symbol or quantity.")
                    
            st.markdown('</div>', unsafe_allow_html=True)

        # Full width Data Export row
        st.markdown('<div class="kite-card" style="margin-top: 16px;">', unsafe_allow_html=True)
        st.subheader("💾 Data Export")
        st.write("Download your active tracking portfolio and cost basis data as a spreadsheet.")
        
        try:
            with open("data/holdings.csv", "rb") as file:
                btn = st.download_button(
                    label="Download Holdings CSV",
                    data=file,
                    file_name="portfolio_holdings.csv",
                    mime="text/csv",
                    type="primary"
                )
        except FileNotFoundError:
            st.info("No tracking data available yet. Initialize a position to generate the CSV.")
            st.download_button("Download Holdings CSV", data="", disabled=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
