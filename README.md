# 🚀 AI Macro Desk - Cloud Trading Dashboard

**Automatisch aktualisierendes Trading Dashboard** - Gehostet auf GitHub Pages mit Daten alle 5 Minuten.

![Dashboard Status](https://img.shields.io/badge/status-live-success?style=flat-square)
![Update Frequency](https://img.shields.io/badge/update-every%205%20minutes-blue?style=flat-square)
![Data Source](https://img.shields.io/badge/data-Yahoo%20Finance-orange?style=flat-square)

---

## 📱 Zugriff

Sobald eingerichtet, ist dein Dashboard erreichbar unter:

```
https://DEIN_USERNAME.github.io/trading-dashboard
```

**Funktioniert auf:**
- ✅ iPhone / Android (Safari, Chrome)
- ✅ iPad / Tablet
- ✅ PC / Mac / Laptop
- ✅ Ohne Installation, einfach URL öffnen

---

## ⚡ Features

| Feature | Beschreibung |
|---------|-------------|
| **5 Assets** | US100, US30, S&P 500, Gold, Bitcoin |
| **Makro-Daten** | Inflation, Fed Rate, Arbeitslosigkeit, GDP, DXY, VIX |
| **Technische Analyse** | RSI, Confidence Score, 52W Range |
| **AI-Kommentare** | Automatisch generierte Marktanalysen |
| **Auto-Refresh** | Alle 5 Minuten neue Daten |
| **Mobile-Optimized** | Responsive Design für alle Geräte |
| **LIVE Badge** | Zeigt an wenn Daten aktualisiert werden |

---

## 🛠️ Einrichtung (5 Minuten)

### Schritt 1: GitHub Account erstellen
1. Gehe zu [github.com/signup](https://github.com/signup)
2. Erstelle einen **kostenlosen** Account
3. Verifiziere deine E-Mail

### Schritt 2: Neues Repository erstellen
1. Klicke auf das **+** Symbol oben rechts → "New repository"
2. **Repository name**: `trading-dashboard`
3. **Description**: `AI Macro Desk - Live Trading Dashboard`
4. Wähle **Public** (wichtig für kostenloses Hosting!)
5. Klicke **Create repository**

### Schritt 3: Dateien hochladen
1. In deinem neuen Repository, klicke auf **"Add file"** → **"Upload files"**
2. Lade alle Dateien aus diesem Ordner hoch:
   - `update_dashboard.py`
   - `index.html` (wird generiert, aber initial nötig)
   - `.github/workflows/update_dashboard.yml`
3. Klicke **"Commit changes"**

**Alternative via Drag & Drop:**
1. Entpacke die ZIP-Datei auf deinem Desktop
2. Ziehe alle Dateien in den Browser (GitHub Upload Bereich)

### Schritt 4: GitHub Pages aktivieren
1. Gehe zu **Settings** (oben im Repository)
2. Scrolle zu **Pages** (linke Seitenleiste)
3. Unter **Source**, wähle **Deploy from a branch**
4. Wähle Branch: `main`, Folder: `/ (root)`
5. Klicke **Save**
6. Warte 2-3 Minuten

### Schritt 5: Fertig!
Deine URL ist nun verfügbar:
```
https://DEIN_USERNAME.github.io/trading-dashboard
```

**Beispiel:** Wenn dein GitHub Name "maxtrader" ist:
```
https://maxtrader.github.io/trading-dashboard
```

---

## 🔄 Wie funktioniert die Aktualisierung?

```
Alle 5 Minuten:
┌─────────────────┐
│ GitHub Actions  │  (Cloud Server)
│   startet       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Holt Daten von  │  Yahoo Finance API
│ Yahoo Finance   │  (15-20min delayed)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Berechnet RSI   │  Technische Indikatoren
│ & Confidence    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generiert HTML  │  Neues Dashboard
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deployed zu     │  GitHub Pages
│ GitHub Pages    │  (Deine URL)
└─────────────────┘
```

---

## 📊 Daten-Qualität

| Aspekt | Details |
|--------|---------|
| **Aktualisierungsrate** | Alle 5 Minuten |
| **Marktdaten-Delay** | 15-20 Minuten (Yahoo Finance kostenlos) |
| **Verfügbarkeit** | 99.9% (GitHub SLA) |
| **Kosten** | 100% kostenlos |

**Wichtig:** Das ist kein Echtzeit-Daytrading-Tool! Die 5-Minuten-Aktualisierung ist für fundamentale Analyse und Swing-Trading optimal.

---

## 🚨 Fehlerbehebung

### Problem: Dashboard zeigt keine Daten
**Lösung:**
1. Gehe zu **Actions** Tab in deinem Repository
2. Prüfe ob der Workflow läuft (grüner Haken)
3. Falls rot: Klicke auf den Fehler und wähle "Re-run jobs"

### Problem: Seite nicht erreichbar (404)
**Lösung:**
1. Warte 5 Minuten nach erstem Setup
2. Prüfe Settings → Pages → Source ist auf `main` gesetzt
3. Stelle sicher dass Repository **Public** ist

### Problem: Daten sind alt
**Lösung:**
1. Browser-Cache leeren (Strg+Shift+R oder Cmd+Shift+R)
2. Prüfe im Actions Tab wann letztes Update war
3. Manuelles Update: Actions → Update Dashboard → Run workflow

---

## 📝 Manuelles Update auslösen

Falls du sofort neue Daten willst:

1. Gehe zu **Actions** Tab
2. Wähle **"Update Trading Dashboard"**
3. Klicke **"Run workflow"** → **"Run workflow"**
4. Warte 1-2 Minuten
5. Lade deine Dashboard-URL neu

---

## 🎯 Tipps für Mobile-Nutzung

### iPhone / iPad:
1. Öffne Dashboard in Safari
2. Tippe auf **Teilen-Button** (unten)
3. Wähle **"Zum Home-Bildschirm"**
4. Dashboard erscheint als App-Icon

### Android:
1. Öffne Dashboard in Chrome
2. Menü (3 Punkte) → **"Zum Startbildschirm hinzufügen"**
3. Dashboard erscheint als App-Icon

---

## 🔒 Datenschutz & Sicherheit

- ✅ Keine persönlichen Daten werden gespeichert
- ✅ Keine Login-Daten nötig
- ✅ Keine Cookies oder Tracking
- ✅ Daten kommen nur von Yahoo Finance
- ✅ Open Source - du kontrollierst alles

---

## 🚀 Erweiterungsmöglichkeiten

Du kannst das Dashboard erweitern:

1. **Mehr Assets:** Füge weitere Aktien/ETFs in `update_dashboard.py` hinzu
2. **Alerts:** Integriere Telegram/Discord Benachrichtigungen
3. **Historie:** Speichere Daten in einer CSV für Charts
4. **Indikatoren:** Füge MACD, Bollinger Bands hinzu

---

## 📞 Support

Falls Probleme auftreten:

1. Prüfe die [GitHub Actions Dokumentation](https://docs.github.com/en/actions)
2. Stelle sicher dass alle Dateien korrekt hochgeladen wurden
3. Überprüfe ob das Repository Public ist

---

## 🎉 Fertig!

Dein professionelles Trading Dashboard läuft nun in der Cloud und aktualisiert sich automatisch alle 5 Minuten. Viel Erfolg beim Trading!

**Letztes Update dieser Anleitung:** 2024
