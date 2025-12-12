# Running BSE Swing Trading Locally

## Quick Start (5 minutes)

### 1. Navigate to Project
```bash
cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Flask Server
```bash
python3 app.py
```

### 4. Open in Browser
```
http://localhost:5000
```

That's it! You now have the full app running locally with real NSE data.

---

## Detailed Setup

### Step 1: Create Python Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or on Windows:
# venv\Scripts\activate
```

### Step 2: Install All Requirements
```bash
pip install -r requirements.txt
```

Expected packages:
- Flask 3.0.0 - Web framework
- pandas - Data manipulation
- numpy - Numerical computing
- requests - HTTP requests (for NSE API)
- beautifulsoup4 - Web scraping fallback
- yfinance 0.2.32 - Stock data (will fail gracefully)
- flask-cors - CORS support

### Step 3: Start the Server

#### Option A: Simple Start (Recommended)
```bash
python3 app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

#### Option B: With Flask CLI
```bash
export FLASK_APP=app.py
flask run
```

#### Option C: With Debug Mode (See errors in real-time)
```bash
export FLASK_ENV=development
python3 app.py
```

### Step 4: Access the Web App

**Open in your browser:**
```
http://localhost:5000
```

You should see:
- Dark-themed dashboard
- "Refresh Data" button
- Real-time stock analysis
- Technical indicators (RSI, MACD, Bollinger Bands)

---

## Testing Different Components

### Test 1: Check Data Fetcher (Real NSE Prices)

```bash
python3 << 'EOF'
from data_fetcher import BSEDataFetcher

print("Testing NSE Data Fetcher...")
fetcher = BSEDataFetcher()

stocks = ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO"]
for stock in stocks:
    data = fetcher.fetch_historical_data(stock, period="3mo")
    if data is not None and len(data) > 0:
        current_price = data['Close'].iloc[-1]
        print(f"✅ {stock}: ₹{current_price:.2f} (REAL from NSE)")
    else:
        print(f"❌ {stock}: Failed to fetch")
EOF
```

### Test 2: Check Full Analysis Pipeline

```bash
python3 << 'EOF'
from ranker import SwingTradingRanker

print("Testing Full Analysis Pipeline...")
ranker = SwingTradingRanker(num_workers=2)

stocks = ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO"]
for stock in stocks:
    result = ranker.analyze_single_stock(stock)
    if result:
        print(f"\n✅ {stock}")
        print(f"   Current Price: ₹{result['current_price']:.2f}")
        print(f"   Swing Probability: {result['probability']:.1%}")
        print(f"   Entry: ₹{result['entry_price']:.2f}")
        print(f"   Target: ₹{result['target_price']:.2f}")
    else:
        print(f"❌ {stock}: Failed")
EOF
```

### Test 3: Check API Endpoints

```bash
# In one terminal, start Flask:
python3 app.py

# In another terminal:

# Test health check
curl http://localhost:5000/api/health

# Test top stocks
curl http://localhost:5000/api/top-stocks | python3 -m json.tool

# Test single stock
curl http://localhost:5000/api/stock/RELIANCE.BO | python3 -m json.tool
```

---

## File Structure

```
swing_trading_app/
├── app.py                      # Main Flask app (run this!)
├── api/
│   └── index.py               # API endpoints
├── data_fetcher.py            # NSE API data fetching
├── swing_analyzer.py          # Technical indicators
├── probability_scorer.py      # Swing probability calculation
├── ranker.py                  # Stock ranking engine
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── style.css              # Styling
│   └── script.js              # Frontend logic
└── requirements.txt           # Python dependencies
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Install requirements
```bash
pip install -r requirements.txt
```

### Issue 2: "Address already in use"

**Solution:** Port 5000 is in use. Use different port:
```bash
python3 app.py --port 8080
```

Or kill the process:
```bash
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Then try again
python3 app.py
```

### Issue 3: "Failed to initialize data fetcher" Error

**Possible causes:**
- NSE API is down (test: `curl https://www.nseindia.com/api/quote-equity?symbol=RELIANCE`)
- No internet connection
- Outside market hours (NSE closed, use cached data)

**Solution:** Check internet and NSE status, then try again

### Issue 4: "SSL certificate problem"

**Expected & OK!** 
- yfinance fails with SSL error (expected)
- NSE API fallback kicks in (working ✅)
- Don't worry, this is part of the design

---

## How It Works Locally

### Data Flow
```
1. You open http://localhost:5000
2. Flask app loads the website
3. Click "Refresh Data" button
4. JavaScript calls /api/top-stocks
5. Backend fetches real NSE data
6. Technical analysis runs
7. Results displayed on your screen
```

### Real-Time Updates

**Automatic caching (5 minutes):**
```bash
# First request: fetches fresh data from NSE
# Next requests (within 5 minutes): uses cached data
# After 5 minutes: fetches fresh again
```

**Manual refresh:**
- Click "Refresh Data" button on the website
- Or API call: `http://localhost:5000/api/top-stocks?refresh=true`

---

## Advanced Testing

### Run All Tests
```bash
python3 -m pytest tests/ -v
```

### Test with Specific Parameters

```bash
# Get top 5 stocks with 70% min probability
curl "http://localhost:5000/api/top-stocks?count=5&min_probability=70"

# Force refresh (ignore cache)
curl "http://localhost:5000/api/top-stocks?refresh=true"
```

### Check Technical Indicators for Specific Stock

```bash
python3 << 'EOF'
from data_fetcher import BSEDataFetcher
from swing_analyzer import SwingTradingAnalyzer

fetcher = BSEDataFetcher()
analyzer = SwingTradingAnalyzer()

data = fetcher.fetch_historical_data("RELIANCE.BO", period="3mo")
if data is not None:
    data_with_indicators = analyzer.calculate_technical_indicators(data)
    
    latest = data_with_indicators.iloc[-1]
    print(f"RELIANCE.BO - Latest Indicators:")
    print(f"  Close: ₹{latest['Close']:.2f}")
    print(f"  RSI(14): {latest['RSI']:.2f}")
    print(f"  MACD: {latest['MACD']:.2f}")
    print(f"  Signal: {latest['MACD_signal']:.2f}")
    print(f"  BB Upper: {latest['BB_upper']:.2f}")
    print(f"  BB Lower: {latest['BB_lower']:.2f}")
EOF
```

---

## Performance Tips

### For Faster Loading

```bash
# Reduce number of workers (fewer stocks analyzed simultaneously)
# Edit ranker.py line 22:
self.ranker = SwingTradingRanker(num_workers=2)  # Default: 3
```

### For More Detailed Analysis

```bash
# Increase analysis period
curl "http://localhost:5000/api/top-stocks?period=6mo"
```

---

## Keep It Running

### Option 1: Terminal (Simple)
Keep terminal open while using the app
```bash
python3 app.py
```

### Option 2: Background Process
```bash
# macOS/Linux
nohup python3 app.py > app.log &

# Check if running
ps aux | grep app.py

# Stop it
pkill -f "python3 app.py"
```

### Option 3: Use Supervisor/PM2 (Production)
```bash
# Install PM2
npm install -g pm2

# Start app
pm2 start app.py --name "bse-trading"

# View logs
pm2 logs bse-trading

# Stop app
pm2 stop bse-trading
```

---

## Next Steps

1. **Run locally:** `python3 app.py`
2. **Open browser:** `http://localhost:5000`
3. **Click "Refresh Data"** to see real NSE data
4. **Analyze results** in the dashboard
5. **Test API** endpoints for integration

---

## Need Help?

**Check logs while app is running:**
```bash
# Terminal output shows real-time errors
python3 app.py
```

**Test NSE API directly:**
```bash
curl "https://www.nseindia.com/api/quote-equity?symbol=RELIANCE" 2>&1 | python3 -m json.tool | head -20
```

**Verify Flask is working:**
```bash
curl http://localhost:5000/api/health
```

---

**Last Updated:** 2025-12-12  
**Status:** ✅ Ready to Run Locally
