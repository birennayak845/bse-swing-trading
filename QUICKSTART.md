# Quick Start Guide - BSE Swing Trading Platform

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd swing_trading_app
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Visit: `http://localhost:5000`

---

## Full Setup Instructions

### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Test the System
```bash
python test_system.py
```

This will test:
- All modules can be imported
- Data fetching from BSE works
- Technical analysis calculations work
- Probability scoring works
- Stock ranking works

### Step 4: Start the Server
```bash
python app.py
```

### Step 5: Access the Dashboard
- Open browser to `http://localhost:5000`
- Click "Refresh Data" to load top 10 stocks
- Adjust "Min Probability" slider to filter results
- Click "Details" on any stock to see full analysis

---

## Understanding the Dashboard

### Main Table Columns

| Column | Meaning |
|--------|---------|
| Rank | Position in top 10 ranking |
| Ticker | Stock symbol (BSE) |
| Company Name | Full company name |
| Sector | Industry sector |
| Current Price | Latest stock price |
| Entry Price | Recommended entry price |
| Stop Loss | Loss limit to minimize risk |
| Target Price | Profit goal price |
| Risk/Reward | Risk-to-reward ratio (higher = better) |
| Entry Time | When to enter the position |
| Swing Score | Overall quality score (0-100) |
| Win Probability | Likelihood of hitting target (%) |

### Color Coding

- **Green prices**: Target prices (potential gains)
- **Red prices**: Stop losses (potential losses)
- **Green badges** (70%+): High probability
- **Yellow badges** (50-70%): Medium probability
- **Red badges** (<50%): Lower probability

### Swing Score Breakdown

The score considers:
- **RSI Level**: Is price oversold?
- **MACD**: Is momentum turning positive?
- **Bollinger Bands**: Is price near support?
- **Volatility**: Is there good potential movement?
- **Trend**: Are we in an uptrend?

---

## Example Trade

Let's say RELIANCE is listed with:
- **Entry**: ₹2500
- **Stop Loss**: ₹2450
- **Target**: ₹2600
- **Probability**: 72%

**What this means:**
- Enter when price reaches ₹2500
- If wrong, exit at ₹2450 (max loss: ₹50)
- Goal is to hit ₹2600 (potential gain: ₹100)
- Ratio is 2:1 (good odds)
- 72% chance of hitting target

**Position Size Example:**
- If risking ₹5000: Buy 100 shares (₹5000 ÷ ₹50 risk per share)
- If hits target: Gain ₹10,000 (₹5000 × 2)
- If hits stop loss: Lose ₹5,000

---

## API Endpoints

### Get Top 10 Stocks
```bash
curl "http://localhost:5000/api/top-stocks?min_probability=40"
```

### Get Specific Stock
```bash
curl "http://localhost:5000/api/stock/RELIANCE"
```

### Health Check
```bash
curl "http://localhost:5000/api/health"
```

---

## Tips for Using the Platform

### For New Traders
1. Start with high-probability stocks (70%+)
2. Follow the suggested stop losses strictly
3. Take profits at targets or exit at stop loss
4. Never add to losing positions
5. Trade only with capital you can afford to lose

### For Experienced Traders
1. Use this as a scanner, not a signal generator
2. Combine with your own analysis
3. Adjust stop loss and targets based on personal risk tolerance
4. Consider volume and liquidity before trading
5. Track trades to validate the probability scoring

### General Best Practices
- Start small (micro trades) to learn
- Never risk more than 1-2% per trade
- Wait for confirmation at entry levels
- Use market orders or limit orders wisely
- Keep emotions out of trading decisions
- Review trades weekly to improve

---

## Troubleshooting

### Data Won't Load
- Check internet connection
- Wait 30 seconds and try again
- Restart the app

### Slow Performance
- Close other applications
- Reduce browser tabs
- Wait for initial data load

### Port Already in Use
```bash
# Use different port
export FLASK_PORT=5001
python app.py
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Advanced Usage

### Modify Analysis Parameters

Edit `swing_analyzer.py`:
```python
# Change RSI levels
self.min_rsi_oversold = 25  # Lower = more aggressive
self.max_rsi_overbought = 75

# Change profit targets
profit_target = entry_price + (current['ATR'] * 3)  # Higher multiplier = bigger targets
```

### Add More Stocks

Edit `data_fetcher.py`:
```python
BSE_TOP_STOCKS = [
    "RELIANCE.BO", "TCS.BO",  # ... add more tickers
    "YOUR_STOCK.BO"  # BSE ticker
]
```

### Change Analysis Period

Edit `ranker.py`:
```python
# Analyze more/fewer stocks
top_10 = ranker.get_top_10_stocks(
    stock_list=BSE_TOP_STOCKS[:30],  # Analyze top 30
    min_probability=50  # Minimum probability threshold
)
```

---

## Important Reminders

⚠️ **This is NOT Financial Advice**
- Do your own research
- Consult financial advisors
- Never invest money you can't afford to lose
- Past performance ≠ future results
- Market can move against you in seconds
- Use stop losses religiously
- Keep emotions in check

---

## Next Steps

1. **Test with paper trading** first
2. **Run the system for 2 weeks** and track recommended trades
3. **Compare results** with actual market movement
4. **Adjust parameters** based on your experience
5. **Start small** when live trading

---

## Support

- Check README.md for detailed documentation
- Review test_system.py output for issues
- Check Flask logs for error messages
- Ensure all dependencies installed correctly

---

**Happy Trading! Remember: The goal is consistent profitability, not quick riches.**
