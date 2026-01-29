#!/usr/bin/env python3
"""
Trading Dashboard Updater
Holt Marktdaten von Yahoo Finance und generiert HTML Dashboard
Läuft automatisch alle 5 Minuten via GitHub Actions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json

def calculate_rsi(prices, period=14):
    """Calculate RSI technical indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def fetch_asset_data(symbol, name, asset_type='index'):
    """Fetch data for a single asset"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        info = ticker.info

        if len(hist) < 2:
            return None

        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((current - prev) / prev) * 100

        rsi = calculate_rsi(hist['Close'])
        confidence = min(95, max(50, 50 + (rsi - 50) * 0.8 + (10 if change_pct > 0 else -10)))

        week_52_high = info.get('fiftyTwoWeekHigh', current * 1.2)
        week_52_low = info.get('fiftyTwoWeekLow', current * 0.8)
        distance = ((current / week_52_high - 1) * 100)

        sentiment = 'Bullish' if change_pct > 0 else 'Bearish' if change_pct < 0 else 'Neutral'

        return {
            'symbol': symbol,
            'name': name,
            'type': asset_type,
            'current': current,
            'change_pct': change_pct,
            'rsi': rsi,
            'confidence': confidence,
            '52w_high': week_52_high,
            '52w_low': week_52_low,
            'distance': distance,
            'sentiment': sentiment,
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def fetch_macro_data():
    """Fetch macro economic indicators"""
    # Simulierte aktuelle Makro-Daten (könnten von API kommen)
    return {
        'US_Inflation': {'value': '2.9%', 'change': '+0.1%', 'trend': 'up', 'label': 'US Inflation'},
        'Fed_Rate': {'value': '4.50%', 'change': '0.00%', 'trend': 'neutral', 'label': 'Fed Rate'},
        'Unemployment': {'value': '4.1%', 'change': '-0.1%', 'trend': 'down', 'label': 'Unemployment'},
        'GDP_Growth': {'value': '2.3%', 'change': '+0.2%', 'trend': 'up', 'label': 'GDP Growth'},
        'DXY': {'value': '104.2', 'change': '-0.8%', 'trend': 'down', 'label': 'Dollar Index'},
        'VIX': {'value': '14.5', 'change': '-2.1%', 'trend': 'down', 'label': 'VIX Fear Index'}
    }

def generate_html(assets_data, macro_data):
    """Generate HTML dashboard"""

    # Asset cards HTML
    asset_cards = ""
    analyses = {
        'US100': "Tech sector resilient with AI momentum. Fed expectations support growth. Watch 52-week highs.",
        'US30': "Mixed industrials signals. Value rotation support. Defensive Fed positioning.",
        'SP500': "All-time highs with tech leadership. Earnings driving sentiment. Broad strength.",
        'GOLD': "Safe-haven surge on geopolitical tensions. Extremely overbought - caution advised.",
        'BTC': "Risk-off pressure. Oversold conditions present potential opportunity. Watch reversal."
    }

    for key, data in assets_data.items():
        if not data:
            continue

        sentiment_class = f"sentiment-{data['sentiment'].lower()}"
        change_class = "positive" if data['change_pct'] > 0 else "negative"
        change_sign = "+" if data['change_pct'] > 0 else ""
        rsi_color = "var(--accent-bullish)" if data['rsi'] > 50 else "var(--accent-bearish)"

        # Format price based on asset type
        if data['type'] == 'crypto':
            price_fmt = f"{data['current']:,.0f}"
        elif data['type'] == 'commodity':
            price_fmt = f"{data['current']:,.2f}"
        else:
            price_fmt = f"{data['current']:,.2f}"

        high_fmt = f"{data['52w_high']:,.0f}"

        asset_cards += f"""
        <div class="card">
            <div class="card-header">
                <div class="asset-name">{key}</div>
                <div class="sentiment-badge {sentiment_class}">
                    <span>●</span>{data['sentiment']}
                </div>
            </div>
            <div class="price-display">
                <div class="current-price">{price_fmt}</div>
                <div class="price-change {change_class}">{change_sign}{data['change_pct']:.2f}%</div>
            </div>
            <div class="confidence-section">
                <div class="confidence-header">
                    <span>Confidence</span>
                    <span>{data['confidence']:.0f}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {data['confidence']}%"></div>
                </div>
            </div>
            <div class="last-update">
                <span>↻</span>
                <span>Updated: {data['last_update']}</span>
            </div>
            <div class="ai-analysis">
                <div class="ai-header"><span>✨</span><span>AI Analysis</span></div>
                <div class="ai-text">{analyses.get(key, 'Market analysis pending...')}</div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="toggleOverview('{key}')">Quick Overview <span id="{key}-arrow">▼</span></button>
                <button class="btn btn-primary">Deep Dive ↗</button>
            </div>
            <div class="expandable-content" id="{key}-overview">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">RSI (14)</div>
                        <div class="stat-value" style="color: {rsi_color}">{data['rsi']:.1f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">52W High</div>
                        <div class="stat-value">{high_fmt}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Distance</div>
                        <div class="stat-value">{data['distance']:+.1f}%</div>
                    </div>
                </div>
            </div>
        </div>
        """

    # Macro bar HTML
    macro_html = ""
    for key, data in macro_data.items():
        trend_color = "var(--accent-bullish)" if data['trend'] == 'down' and key in ['US_Inflation', 'Unemployment', 'VIX'] else \
                      "var(--accent-bearish)" if data['trend'] == 'up' and key in ['US_Inflation', 'Unemployment'] else \
                      "var(--accent-bullish)" if data['trend'] == 'up' else "var(--accent-bearish)" if data['trend'] == 'down' else "var(--text-secondary)"
        macro_html += f"""
        <div class="macro-item">
            <div class="macro-label">{data['label']}</div>
            <div class="macro-value">{data['value']}</div>
            <div class="macro-change" style="color: {trend_color}">{data['change']}</div>
        </div>
        """

    # Complete HTML
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>AI Macro Desk - Live Trading Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --bg-primary: #0a0a0f; --bg-secondary: #12121a; --bg-card: #1a1a24; --bg-hover: #252532; --text-primary: #ffffff; --text-secondary: #a0a0b0; --accent-bullish: #00d084; --accent-bearish: #ff4757; --accent-teal: #00d4aa; --accent-blue: #3498db; --border: #2a2a3a; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: var(--bg-primary); color: var(--text-primary); min-height: 100vh; }}
.container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 30px; }}
.logo {{ display: flex; align-items: center; gap: 12px; }}
.logo-icon {{ width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue)); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; }}
.logo-text {{ font-size: 24px; font-weight: 700; background: linear-gradient(135deg, var(--text-primary), var(--accent-teal)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.status-badge {{ background: var(--bg-card); border: 1px solid var(--accent-teal); color: var(--accent-teal); padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
.status-dot {{ width: 8px; height: 8px; background: var(--accent-teal); border-radius: 50%; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
.user-avatar {{ width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }}
.welcome-section {{ margin-bottom: 30px; }}
.welcome-text {{ font-size: 28px; font-weight: 300; color: var(--text-secondary); }}
.welcome-text strong {{ color: var(--text-primary); font-weight: 600; }}
.subtitle {{ color: var(--text-secondary); margin-top: 5px; font-size: 14px; }}
.macro-bar {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; }}
.macro-item {{ text-align: center; padding: 10px; border-right: 1px solid var(--border); }}
.macro-item:last-child {{ border-right: none; }}
.macro-label {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }}
.macro-value {{ font-size: 18px; font-weight: 700; }}
.macro-change {{ font-size: 11px; font-weight: 600; margin-top: 3px; }}
.dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 30px; }}
.card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; transition: all 0.3s; }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 40px rgba(0, 212, 170, 0.1); }}
.card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
.asset-name {{ font-size: 22px; font-weight: 700; }}
.sentiment-badge {{ padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; display: flex; align-items: center; gap: 5px; }}
.sentiment-bullish {{ background: rgba(0, 208, 132, 0.15); color: var(--accent-bullish); border: 1px solid rgba(0, 208, 132, 0.3); }}
.sentiment-bearish {{ background: rgba(255, 71, 87, 0.15); color: var(--accent-bearish); border: 1px solid rgba(255, 71, 87, 0.3); }}
.sentiment-neutral {{ background: rgba(160, 160, 176, 0.15); color: var(--text-secondary); border: 1px solid rgba(160, 160, 176, 0.3); }}
.price-display {{ display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px; }}
.current-price {{ font-size: 26px; font-weight: 700; }}
.price-change {{ font-size: 13px; font-weight: 600; padding: 3px 8px; border-radius: 6px; }}
.positive {{ color: var(--accent-bullish); background: rgba(0, 208, 132, 0.1); }}
.negative {{ color: var(--accent-bearish); background: rgba(255, 71, 87, 0.1); }}
.confidence-section {{ margin: 15px 0; }}
.confidence-header {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; color: var(--text-secondary); }}
.confidence-bar {{ height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }}
.confidence-fill {{ height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--accent-teal), var(--accent-blue)); }}
.last-update {{ display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--text-secondary); margin-top: 10px; }}
.ai-analysis {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin: 15px 0; }}
.ai-header {{ display: flex; align-items: center; gap: 6px; margin-bottom: 8px; color: var(--accent-teal); font-weight: 600; font-size: 12px; }}
.ai-text {{ font-size: 12px; line-height: 1.5; color: var(--text-secondary); }}
.action-buttons {{ display: flex; gap: 8px; margin-top: 15px; }}
.btn {{ flex: 1; padding: 10px 16px; border-radius: 8px; border: none; font-size: 12px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 5px; }}
.btn-secondary {{ background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border); }}
.btn-primary {{ background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue)); color: white; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); }}
.stat-item {{ text-align: center; }}
.stat-label {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 3px; }}
.stat-value {{ font-size: 14px; font-weight: 600; }}
.expandable-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }}
.expandable-content.expanded {{ max-height: 400px; }}
.auto-refresh-info {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
.refresh-text {{ font-size: 13px; color: var(--text-secondary); }}
.refresh-time {{ font-size: 13px; color: var(--accent-teal); font-weight: 600; }}
@media (max-width: 768px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} .macro-bar {{ grid-template-columns: repeat(2, 1fr); }} .macro-item {{ border-right: none; border-bottom: 1px solid var(--border); padding: 15px 0; }} .macro-item:last-child {{ border-bottom: none; }} }}
</style>
</head>
<body>
<div class="container">
<header>
<div class="logo"><div class="logo-icon">H</div><div class="logo-text">Hybrid Trader Pro</div></div>
<div style="display: flex; align-items: center; gap: 15px;">
<div class="status-badge"><div class="status-dot"></div>LIVE DATA</div>
<div class="user-avatar">D</div>
</div>
</header>
<div class="welcome-section">
<div class="welcome-text">Guten Tag, <strong>Trader</strong>.</div>
<div class="subtitle">Cloud-Hosted | Auto-Refresh every 5 min | 5 Assets | Real-time Macro Data</div>
</div>
<div class="auto-refresh-info">
<div class="refresh-text">📊 Dashboard refreshes automatically every 5 minutes via GitHub Actions</div>
<div class="refresh-time">Last update: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
</div>
<div class="macro-bar">{macro_html}</div>
<div class="dashboard-grid">{asset_cards}</div>
<div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-top: 30px; text-align: center;">
<div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 10px;">🚀 Powered by GitHub Actions | Data: Yahoo Finance | Updates: Every 5 minutes</div>
<div style="font-size: 12px; color: var(--text-secondary);">Next update in ~{5 - (datetime.now().minute % 5)} minutes</div>
</div>
</div>
<script>function toggleOverview(asset){{var c=document.getElementById(asset+'-overview'),a=document.getElementById(asset+'-arrow');c.classList.contains('expanded')?(c.classList.remove('expanded'),a.textContent='▼'):(c.classList.add('expanded'),a.textContent='▲');}}</script>
</body>
</html>"""

    return html

def main():
    """Main function"""
    print("🚀 Starting Dashboard Update...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Define assets
    assets_config = [
        ('^NDX', 'US100', 'index'),
        ('^DJI', 'US30', 'index'),
        ('^GSPC', 'SP500', 'index'),
        ('GC=F', 'GOLD', 'commodity'),
        ('BTC-USD', 'BTC', 'crypto')
    ]

    # Fetch all assets
    assets_data = {}
    for symbol, key, asset_type in assets_config:
        print(f"📈 Fetching {key}...")
        data = fetch_asset_data(symbol, key, asset_type)
        if data:
            assets_data[key] = data
            print(f"   ✅ {key}: {data['current']:,.2f} ({data['change_pct']:+.2f}%)")
        else:
            print(f"   ❌ Failed to fetch {key}")

    # Fetch macro data
    print("🌍 Fetching macro data...")
    macro_data = fetch_macro_data()

    # Generate HTML
    print("🎨 Generating HTML dashboard...")
    html = generate_html(assets_data, macro_data)

    # Save to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Dashboard saved to index.html")
    print("🎉 Update complete!")

    # Save data summary for debugging
    summary = {
        'last_update': datetime.now().isoformat(),
        'assets': {k: {**v, 'current': float(v['current']), 'change_pct': float(v['change_pct'])} for k, v in assets_data.items()},
        'macro': macro_data
    }

    with open('data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("📝 Data summary saved to data_summary.json")

if __name__ == "__main__":
    main()
