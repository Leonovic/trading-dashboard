#!/usr/bin/env python3
"""
Trading Dashboard Updater - FUNDAMENTAL EDITION
Holt Marktdaten von Yahoo Finance + Fundamentalanalyse
Läuft automatisch alle 15 Minuten via GitHub Actions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import json
import sys
import traceback

def fetch_asset_data(symbol, name, asset_type='index'):
    """Fetch price data for a single asset"""
    try:
        print(f"  Fetching {symbol}...")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="1d")
        
        if hist is None or len(hist) < 2:
            print(f"  ⚠️  Keine Daten für {symbol}")
            return None

        current = float(hist['Close'].iloc[-1])
        prev = float(hist['Close'].iloc[-2])
        change_pct = ((current - prev) / prev) * 100

        # 52W Daten versuchen zu holen, Fallback wenn nicht verfügbar
        try:
            info = ticker.info
            week_52_high = float(info.get('fiftyTwoWeekHigh', current * 1.1))
            week_52_low = float(info.get('fiftyTwoWeekLow', current * 0.9))
        except:
            week_52_high = current * 1.1
            week_52_low = current * 0.9
            
        distance = ((current / week_52_high - 1) * 100)

        return {
            'symbol': symbol,
            'name': name,
            'type': asset_type,
            'current': current,
            'change_pct': change_pct,
            '52w_high': week_52_high,
            '52w_low': week_52_low,
            'distance': distance,
            'last_update': datetime.now(pytz.timezone('Europe/Berlin')).strftime('%H:%M:%S')
        }
    except Exception as e:
        print(f"  ❌ Fehler bei {symbol}: {str(e)}")
        return None

def calculate_fundamental_score(asset_key, macro_data):
    """
    Calculate Bullish/Bearish score based on fundamental factors
    Returns: (sentiment, confidence_score, analysis_dict)
    """
    
    # Current macro conditions (Jan 2025)
    us_inflation = 2.9  # %
    fed_rate = 4.50  # %
    unemployment = 4.1  # %
    gdp_growth = 2.4  # %
    ecb_rate = 3.0  # %
    
    score = 50  # Neutral start
    factors = []
    
    if asset_key == 'US100':
        # Tech-heavy, sensitive to rates, benefits from growth
        if fed_rate > 4.0:  # Restrictive
            score -= 15
            factors.append("Fed restrictiv (4.5%) belastet Tech-Bewertungen")
        else:
            score += 10
            factors.append("Niedrigere Zinsen bullish für Growth")
            
        if gdp_growth > 2.0:
            score += 15
            factors.append("GDP +2.4% bestätigt robustes Wachstum")
        else:
            score -= 10
            
        if us_inflation < 3.0:
            score += 10
            factors.append("Inflation 2.9% näher Fed-Ziel")
        else:
            score -= 5
            
        # Soft Landing scenario = bullish for tech
        score += 10
        factors.append("Soft Landing Szenario: KI-Investitionen treiben Margen")
        
    elif asset_key == 'US30':
        # Industrials, value, dividend focus
        if fed_rate > 4.0:
            score -= 5  # Less sensitive than tech
            factors.append("Höhere Zinsen moderat belastend")
        else:
            score += 15
            factors.append("Zinssenkung bullish für Industrie/Value")
            
        if gdp_growth > 2.0:
            score += 15
            factors.append("GDP-Wachstum stützt industrielle Nachfrage")
            
        if unemployment < 4.5:
            score += 10
            factors.append("Arbeitsmarkt stabil (4.1%)")
            
        score += 5
        factors.append("Dividendenrendite attraktiv vs Bonds")
        
    elif asset_key == 'SP500':
        # Broad market
        if fed_rate > 4.0:
            score -= 10
        else:
            score += 15
            
        if gdp_growth > 2.0:
            score += 15
            factors.append("Breites GDP-Wachstum +2.4%")
            
        if us_inflation < 3.0:
            score += 10
            factors.append("Inflationskontrolle ermöglicht Fed-Pivot")
            
        score += 10
        factors.append("Gewinnwachstum +8% erwartet 2025")
        
    elif asset_key == 'GOLD':
        # Safe haven, inflation hedge, inverse to real rates
        if fed_rate > 4.0:  # High nominal rates
            score -= 10
            factors.append("Hohe Nominalzinsen belasten Gold")
        else:
            score += 20
            factors.append("Zinssenkungen treiben Goldpreis")
            
        # Real rates expected to fall = bullish
        score += 15
        factors.append("Realzinsen sinken erwartet (Fed-Pivot)")
        
        if us_inflation > 2.5:
            score += 15
            factors.append("Inflation 2.9% > Ziel = Inflationsschutz-Nachfrage")
            
        score += 10
        factors.append("Geopolitische Unsicherheit (Ukraine, Taiwan)")
        score += 10
        factors.append("Zentralbankkäufe bleiben robust")
        
    elif asset_key == 'BTC':
        # Risk asset, liquidity sensitive
        if fed_rate > 4.0:
            score -= 15
            factors.append("Restrictive Fed belastet Risk-Assets")
        else:
            score += 20
            factors.append("Liquditätsflut bei Zinssenkungen")
            
        if gdp_growth < 1.0:
            score -= 10  # Recession fear
            
        score += 10
        factors.append("ETF-Zuflüsse stabil")
        score += 5
        factors.append("Halving-Zyklus historisch bullisch")
        
    elif asset_key == 'EURUSD':
        # Currency pair - driven by rate differential
        rate_diff = fed_rate - ecb_rate  # 1.5% in favor of USD
        
        if rate_diff > 1.0:
            score -= 25  # Bearish for EUR
            factors.append(f"Zinsdifferenzial +{rate_diff}% zugunsten USD")
        elif rate_diff < 0:
            score += 20
            factors.append("EZB-Zins > Fed = EUR-Stärke")
            
        if us_inflation > 3.0:
            score -= 5  # USD inflation concern
        if us_inflation < 2.5:
            score += 10
            
        # Growth differential
        if gdp_growth > 2.0:
            score -= 10  # US growth > EU = USD stronger
            
        score += 5
        factors.append("EZB Inflation 2.4% näher Ziel als US")
        
    # Clamp score
    score = max(10, min(95, score))
    
    # Determine sentiment
    if score >= 60:
        sentiment = 'Bullish'
    elif score <= 40:
        sentiment = 'Bearish'
    else:
        sentiment = 'Neutral'
        
    return sentiment, score, factors

def get_fundamental_analysis(key, data, macro_data):
    """Generate detailed fundamental German analysis"""
    
    sentiment, confidence, factors = calculate_fundamental_score(key, macro_data)
    change = data['change_pct']
    
    # Current macro snapshot
    us_inflation = "2.9%"
    fed_rate = "4.50%"
    gdp = "2.4%"
    unemployment = "4.1%"
    ecb_rate = "3.00%"
    
    # Build analysis text
    trend_text = ""
    if key == 'EURUSD':
        if change > 0.5:
            trend_text = f"<strong>EUR-Stärke</strong> mit +{change:.2f}%. Überraschende EZB-Hawkishness oder USD-Schwäche."
        elif change < -0.5:
            trend_text = f"<strong>USD-Stärke</strong> mit {change:.2f}%. Zinsdifferenzial treibt Carry-Trade."
        else:
            trend_text = f"<strong>Seitwärtsbewegung</strong> mit {change:+.2f}%. Ausgewogenes Kräfteverhältnis."
    else:
        if change > 2:
            trend_text = f"<strong>Starker Aufwärtstrend</strong> mit +{change:.2f}%. Fundamental treibt Kurs."
        elif change > 0.5:
            trend_text = f"<strong>Leichter Aufwärtstrend</strong> mit +{change:.2f}%. Positive Fundamentale treiben."
        elif change > -0.5:
            trend_text = f"<strong>Seitwärts</strong> mit {change:+.2f}%. Markt wartet auf neue Fundamentaldaten."
        elif change > -2:
            trend_text = f"<strong>Leichter Rückgang</strong> mit {change:.2f}%. Gewinnmitnahmen trotz guter Fundamente."
        else:
            trend_text = f"<strong>Stärkerer Rückgang</strong> mit {change:.2f}%. Fundamentaldaten werden neu bewertet."

    # Fundamental factors list
    factors_html = "<br>".join([f"• {f}" for f in factors[:4]])  # Top 4 factors
    
    # Macro context specific to asset
    macro_contexts = {
        'US100': f"Tech-Sektor unter Einfluss von Fed-Politik ({fed_rate}) und KI-Investitionszyklus. Inflation {us_inflation} bestimmt Pivot-Erwartungen.",
        'US30': f"Industriewerte profitieren von GDP-Wachstum ({gdp}) und stabilem Arbeitsmarkt ({unemployment}). Value-Rotation bei Zinssenkungen.",
        'SP500': f"Breites Marktumfeld: Fed bei {fed_rate}, Inflation {us_inflation}, GDP {gdp}. Soft Landing-Szenario mit +8% Gewinnwachstum erwartet.",
        'GOLD': f"Gold profitiert von erwartetem Fed-Pivot (aktuell {fed_rate}) und Inflationsschutz ({us_inflation}). Realzinsen sinkend.",
        'BTC': f"Krypto korreliert mit Tech-Aktien. Fed-Restriktion ({fed_rate}) belastet, Pivot würde Liqudität freisetzen.",
        'EURUSD': f"Währungspaar getrieben durch Zinsdifferenzial (Fed {fed_rate} vs EZB {ecb_rate}). Carry-Trade begünstigt USD."
    }
    
    confidence_text = f"<strong>Fundamental Confidence {confidence:.0f}%</strong> – basiert auf Makro-Regime, nicht technischen Indikatoren."
    
    analysis = f"""{trend_text}<br><br>

    <strong>📊 Fundamentale Treiber:</strong><br>
    {factors_html}<br><br>

    <strong>🌍 Makro-Regime:</strong><br>
    {macro_contexts.get(key, 'Aktuelles Makroumfeld analysieren.')}<br><br>
    
    {confidence_text}"""
    
    return analysis, sentiment, confidence

def fetch_macro_data():
    """Fetch macro economic indicators - Jan 2025 data"""
    return {
        'US_Inflation': {'value': '2.9%', 'change': '+0.1%', 'trend': 'up', 'label': 'US Inflation'},
        'Fed_Rate': {'value': '4.50%', 'change': '0.00%', 'trend': 'neutral', 'label': 'Fed Rate'},
        'Unemployment': {'value': '4.1%', 'change': '-0.1%', 'trend': 'down', 'label': 'Unemployment'},
        'GDP_Growth': {'value': '2.4%', 'change': '+0.2%', 'trend': 'up', 'label': 'GDP Growth'},
        'DXY': {'value': '104.2', 'change': '-0.8%', 'trend': 'down', 'label': 'Dollar Index'},
        'VIX': {'value': '14.5', 'change': '-2.1%', 'trend': 'down', 'label': 'VIX Fear Index'}
    }

def generate_html(assets_data, macro_data):
    """Generate HTML dashboard with fundamental analysis"""

    # Asset cards HTML
    asset_cards = ""

    for key, data in assets_data.items():
        if not data:
            continue

        # Get fundamental analysis
        analysis, sentiment, confidence = get_fundamental_analysis(key, data, macro_data)
        
        sentiment_class = f"sentiment-{sentiment.lower()}"
        change_class = "positive" if data['change_pct'] > 0 else "negative"
        change_sign = "+" if data['change_pct'] > 0 else ""
        
        # Color based on sentiment (not just price change)
        if sentiment == 'Bullish':
            confidence_color = "#34c759"
        elif sentiment == 'Bearish':
            confidence_color = "#ff3b30"
        else:
            confidence_color = "#8e8e93"

        # Format price based on asset type
        if data['type'] == 'crypto':
            price_fmt = f"{data['current']:,.0f}"
        elif data['type'] == 'commodity':
            price_fmt = f"{data['current']:,.2f}"
        elif key == 'EURUSD':
            price_fmt = f"{data['current']:.4f}"
        else:
            price_fmt = f"{data['current']:,.2f}"

        high_fmt = f"{data['52w_high']:,.0f}" if key != 'EURUSD' else f"{data['52w_high']:.4f}"

        asset_cards += f"""
        <div class="card">
            <div class="card-header">
                <div class="asset-name">{key}</div>
                <div class="sentiment-badge {sentiment_class}">
                    <span>●</span>{sentiment}
                </div>
            </div>

            <div class="price-display">
                <div class="current-price">{price_fmt}</div>
                <div class="price-change {change_class}">
                    {change_sign}{data['change_pct']:.2f}%
                </div>
            </div>

            <div class="confidence-section">
                <div class="confidence-header">
                    <span>Fundamental Confidence</span>
                    <span style="color: {confidence_color}">{confidence:.0f}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence}%; background: {confidence_color}"></div>
                </div>
            </div>

            <div class="last-update">
                <span>↻</span>
                <span>Aktualisiert: {data['last_update']} Uhr</span>
            </div>

            <div class="ai-analysis">
                <div class="ai-header">
                    <span>🤖</span>
                    <span>KI-Fundamental-Analyse</span>
                </div>
                <div class="ai-text">{analysis}</div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="toggleOverview('{key}')">
                    Details anzeigen <span id="{key}-arrow">▼</span>
                </button>
            </div>

            <div class="expandable-content" id="{key}-overview">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">52W Hoch</div>
                        <div class="stat-value">{high_fmt}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Abstand 52W</div>
                        <div class="stat-value">{data['distance']:+.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Makro-Regime</div>
                        <div class="stat-value" style="color: {confidence_color}; font-size: 11px;">Soft Landing</div>
                    </div>
                </div>
            </div>
        </div>
        """

    # Complete HTML - Mobile optimized design
    now = datetime.now(pytz.timezone('Europe/Berlin'))
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="900">
<title>Hybrid Trader Pro - Fundamental Edition</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --bg-primary: #000000; --bg-secondary: #1c1c1e; --bg-card: #2c2c2e; --bg-hover: #3a3a3c; --text-primary: #ffffff; --text-secondary: #8e8e93; --accent-bullish: #34c759; --accent-bearish: #ff3b30; --accent-teal: #00d4aa; --accent-blue: #007aff; --accent-purple: #af52de; --border: #38383a; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-primary); color: var(--text-primary); min-height: 100vh; -webkit-font-smoothing: antialiased; }}
.container {{ max-width: 480px; margin: 0 auto; padding: 16px; }}
header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 0 20px; }}
.logo-text {{ font-size: 20px; font-weight: 700; background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.status-badge {{ background: rgba(0, 212, 170, 0.15); border: 1px solid var(--accent-teal); color: var(--accent-teal); padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 6px; }}
.status-dot {{ width: 6px; height: 6px; background: var(--accent-teal); border-radius: 50%; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
.welcome-text {{ font-size: 28px; font-weight: 300; color: var(--text-secondary); margin-bottom: 4px; }}
.welcome-text strong {{ color: var(--text-primary); font-weight: 600; }}
.subtitle {{ color: var(--text-secondary); font-size: 13px; margin-bottom: 20px; }}
.info-banner {{ background: var(--bg-secondary); border-radius: 16px; padding: 16px; margin-bottom: 20px; border-left: 3px solid var(--accent-blue); }}
.info-text {{ font-size: 13px; color: var(--text-secondary); line-height: 1.5; }}
.info-time {{ font-size: 12px; color: var(--accent-teal); margin-top: 8px; font-weight: 500; }}
.macro-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; }}
.macro-item {{ background: var(--bg-secondary); border-radius: 16px; padding: 16px; text-align: center; border: 1px solid var(--border); }}
.macro-label {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
.macro-value {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; }}
.macro-change {{ font-size: 12px; font-weight: 600; }}
.card {{ background: linear-gradient(145deg, var(--bg-secondary), rgba(44,44,46,0.8)); border: 1px solid var(--border); border-radius: 24px; padding: 20px; margin-bottom: 16px; overflow: hidden; }}
.card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
.asset-name {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
.sentiment-badge {{ padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; display: flex; align-items: center; gap: 6px; }}
.sentiment-bullish {{ background: rgba(52, 199, 89, 0.15); color: var(--accent-bullish); border: 1px solid rgba(52, 199, 89, 0.3); }}
.sentiment-bearish {{ background: rgba(255, 59, 48, 0.15); color: var(--accent-bearish); border: 1px solid rgba(255, 59, 48, 0.3); }}
.sentiment-neutral {{ background: rgba(142, 142, 147, 0.15); color: var(--text-secondary); border: 1px solid rgba(142, 142, 147, 0.3); }}
.price-display {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; }}
.current-price {{ font-size: 32px; font-weight: 700; letter-spacing: -1px; }}
.price-change {{ font-size: 15px; font-weight: 600; padding: 4px 10px; border-radius: 8px; }}
.positive {{ color: var(--accent-bullish); background: rgba(52, 199, 89, 0.15); }}
.negative {{ color: var(--accent-bearish); background: rgba(255, 59, 48, 0.15); }}
.confidence-section {{ margin-bottom: 12px; }}
.confidence-header {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; color: var(--text-secondary); }}
.confidence-bar {{ height: 6px; background: var(--bg-hover); border-radius: 3px; overflow: hidden; }}
.confidence-fill {{ height: 100%; border-radius: 3px; transition: width 0.5s ease; }}
.last-update {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; }}
.ai-analysis {{ background: rgba(0, 122, 255, 0.08); border-left: 3px solid var(--accent-blue); border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
.ai-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: var(--accent-blue); font-weight: 600; font-size: 14px; }}
.ai-text {{ font-size: 13px; line-height: 1.6; color: var(--text-secondary); }}
.ai-text strong {{ color: var(--text-primary); font-weight: 600; }}
.btn {{ width: 100%; padding: 14px; border-radius: 12px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; background: var(--bg-hover); color: var(--text-primary); border: 1px solid var(--border); }}
.stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }}
.stat-item {{ text-align: center; }}
.stat-label {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px; }}
.stat-value {{ font-size: 14px; font-weight: 600; }}
.expandable-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }}
.expandable-content.expanded {{ max-height: 300px; }}
.footer {{ text-align: center; padding: 40px 0; color: var(--text-secondary); font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
<header>
<div class="logo-text">Hybrid Trader Pro</div>
<div class="status-badge"><div class="status-dot"></div>LIVE</div>
</header>

<div class="welcome-text">Guten Tag, <strong>Trader</strong>.</div>
<div class="subtitle">Fundamental Analysis | Auto-Refresh 15 Min</div>

<div class="info-banner">
<div class="info-text">🚀 Dashboard aktualisiert sich automatisch alle 15 Minuten via GitHub Actions</div>
<div class="info-time">Letztes Update: {now.strftime('%d.%m.%Y %H:%M:%S')}</div>
</div>

<div class="macro-grid">
<div class="macro-item">
<div class="macro-label">US Inflation</div>
<div class="macro-value">2.9%</div>
<div class="macro-change" style="color: var(--accent-bearish)">+0.1%</div>
</div>
<div class="macro-item">
<div class="macro-label">Fed Rate</div>
<div class="macro-value">4.50%</div>
<div class="macro-change" style="color: var(--text-secondary)">0.00%</div>
</div>
<div class="macro-item">
<div class="macro-label">Unemployment</div>
<div class="macro-value">4.1%</div>
<div class="macro-change" style="color: var(--accent-bullish)">-0.1%</div>
</div>
<div class="macro-item">
<div class="macro-label">GDP Growth</div>
<div class="macro-value">2.4%</div>
<div class="macro-change" style="color: var(--accent-bullish)">+0.2%</div>
</div>
</div>

{asset_cards}

<div class="footer">
<p>Fundamental Macro Dashboard</p>
<p style="margin-top: 4px; opacity: 0.7;">Daten: Yahoo Finance | Keine Anlageberatung</p>
</div>
</div>

<script>
function toggleOverview(asset) {{
    var content = document.getElementById(asset + '-overview');
    var arrow = document.getElementById(asset + '-arrow');
    if (content.classList.contains('expanded')) {{
        content.classList.remove('expanded');
        arrow.textContent = '▼';
    }} else {{
        content.classList.add('expanded');
        arrow.textContent = '▲';
    }}
}}
</script>
</body>
</html>"""

    return html

def main():
    """Main function"""
    try:
        print("🚀 Starte Fundamental Dashboard Update...")
        print(f"⏰ {datetime.now(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')} (MEZ/CET)")

        assets_config = [
            ('^NDX', 'US100', 'index'),
            ('^DJI', 'US30', 'index'),
            ('^GSPC', 'SP500', 'index'),
            ('GC=F', 'GOLD', 'commodity'),
            ('BTC-USD', 'BTC', 'crypto'),
            ('EURUSD=X', 'EURUSD', 'forex')
        ]

        assets_data = {}
        for symbol, key, asset_type in assets_config:
            print(f"📈 Lade {key}...")
            data = fetch_asset_data(symbol, key, asset_type)
            if data:
                assets_data[key] = data
                price_str = f"{data['current']:.4f}" if key == 'EURUSD' else f"{data['current']:,.2f}'
                print(f"   ✅ {key}: {price_str} ({data['change_pct']:+.2f}%)")
            else:
                print(f"   ⚠️  {key}: Keine Daten")

        if not assets_data:
            print("❌ Keine Asset-Daten verfügbar!")
            sys.exit(1)

        print("🌍 Lade Makro-Daten...")
        macro_data = fetch_macro_data()

        print("🎨 Generiere Fundamental HTML Dashboard...")
        html = generate_html(assets_data, macro_data)

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)

        print("✅ Dashboard gespeichert als index.html")

        # Save summary
        summary = {
            'last_update': datetime.now().isoformat(),
            'type': 'fundamental_analysis',
            'assets_count': len(assets_data),
            'assets': {k: {'price': float(v['current']), 'change': float(v['change_pct'])} for k, v in assets_data.items()},
            'macro': macro_data
        }
        
        with open('data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
            
        print("🎉 Fundamental Update erfolgreich abgeschlossen!")
        return 0
        
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return 1

if _name_ == "_main_":
    exit_code = main()
    sys.exit(exit_code)
