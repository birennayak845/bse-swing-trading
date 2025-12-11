# BSE Swing Trading Analysis Platform

A web-based platform that fetches real-time BSE stock data and identifies the top 10 stocks most favorable for swing trading (long positions) using advanced technical analysis.

## Features

- **Real-Time BSE Data**: Fetches current stock prices and historical data from Yahoo Finance
- **Technical Analysis**: Uses multiple indicators:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Support/Resistance Levels
  - Simple Moving Averages (SMA)
  - Average True Range (ATR)

- **Swing Trading Setup**: Calculates optimal entry prices, stop losses, and target prices with risk-reward ratios
- **Probability Scoring**: Determines the likelihood of hitting target prices based on:
  - Historical pattern matching
  - Technical indicator signals
  - Mean reversion analysis
  - Risk-reward ratio optimization

- **Top 10 Rankings**: Automatically ranks stocks by favorability for swing trading
- **Interactive Dashboard**: Beautiful web interface to view and analyze stocks
- **Watchlist Management**: Save stocks for later analysis

## Project Structure

```
swing_trading_app/
├── app.py                          # Flask backend application
├── data_fetcher.py                 # BSE data fetching module
├── swing_analyzer.py               # Technical analysis engine
├── probability_scorer.py           # Probability calculation system
├── ranker.py                       # Stock ranking and filtering
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Frontend HTML template
└── static/
    ├── style.css                   # CSS styles
    └── script.js                   # Frontend JavaScript
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Navigate to the project directory**:
   ```bash
   cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start at `http://localhost:5000`

### Production Mode

Using Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app.py
```

## API Endpoints

### Get Top 10 Stocks
```
GET /api/top-stocks?min_probability=40&refresh=false
```

**Parameters:**
- `min_probability` (optional): Minimum probability threshold (0-100, default: 40)
- `refresh` (optional): Force refresh data (true/false, default: false)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "RELIANCE.BO",
      "name": "Reliance Industries",
      "sector": "Energy",
      "current_price": "₹2500.00",
      "entry_price": "₹2500.00",
      "stop_loss": "₹2450.00",
      "target_price": "₹2600.00",
      "risk": "₹50.00",
      "reward": "₹100.00",
      "rr_ratio": "2.00:1",
      "entry_time": "Immediate (at support)",
      "swing_score": "75.5",
      "probability_score": "72.3%",
      ...
    }
  ],
  "timestamp": "2024-12-11T10:30:00",
  "from_cache": false
}
```

### Get Stock Analysis
```
GET /api/stock/<ticker>
```

**Example:**
```
GET /api/stock/RELIANCE
```

### Watchlist Management
```
GET /api/watchlist              # Get watchlist
POST /api/watchlist             # Add to watchlist
DELETE /api/watchlist           # Remove from watchlist
```

## Understanding the Analysis

### Swing Score (0-100)
Composite score based on:
- **RSI Oversold Signal** (30 weight): Lower RSI indicates potential bounce
- **MACD Signals** (25 weight): Bullish crossovers indicate momentum
- **Bollinger Bands** (20 weight): Price near lower band suggests reversal
- **Volatility** (15 weight): Optimal ATR range for swing trading
- **Trend** (10 weight): Overall bullish alignment

### Probability Score (0-100%)
Calculated using:
- **Pattern Matching** (35%): Historical similar patterns' success rate
- **Swing Score** (35%): Technical indicator strength
- **Risk-Reward Ratio** (30%): Favorable risk-reward expectations

### Trade Setup
- **Entry Price**: Current market price (or at support level)
- **Stop Loss**: Calculated using ATR (1.5x) or support level
- **Target Price**: Calculated using 2.5x ATR above entry
- **Risk-Reward Ratio**: Reward/Risk ratio for position sizing

## Key Technical Indicators Explained

### RSI (Relative Strength Index)
- **Below 30**: Oversold (potential bounce)
- **30-70**: Neutral zone
- **Above 70**: Overbought

### MACD
- **Signal**: Crossover above signal line indicates bullish momentum
- **Histogram**: MACD minus signal line (positive = bullish)

### Bollinger Bands
- **Upper Band**: Resistance level (2 std dev above SMA)
- **Lower Band**: Support level (2 std dev below SMA)
- **Price near lower band**: Mean reversion opportunity

### ATR (Average True Range)
- Measures volatility
- Used for stop loss and profit target calculation
- Larger ATR = more price movement potential

## Configuration

### Adjustable Parameters (in swing_analyzer.py)

```python
# RSI thresholds
self.min_rsi_oversold = 30           # RSI oversold level
self.max_rsi_overbought = 70         # RSI overbought level

# Stop loss multiplier
atr_multiplier = 1.5                 # Stop loss = Entry - (ATR × 1.5)

# Profit target multiplier
profit_target = entry + (ATR × 2.5)  # Target = Entry + (ATR × 2.5)
```

## Data Sources

- **Real-time & Historical Data**: Yahoo Finance (via yfinance)
- **Update Frequency**: Cache refreshes every 15 minutes
- **Historical Period**: 3 months (90 days) for analysis

## Risk Disclaimer

⚠️ **IMPORTANT DISCLAIMER** ⚠️

This tool is for **educational and analytical purposes only**. It is NOT financial advice.

- Past performance does not guarantee future results
- Stock market trading involves substantial risk
- You can lose more than your initial investment
- Always conduct your own research
- Consult with a licensed financial advisor before trading
- Use proper risk management and position sizing
- Stop-losses help limit losses but don't eliminate them
- Emotional discipline is crucial in trading

## Limitations

1. **Historical Data Only**: Analysis based on past price action
2. **Market Events**: Cannot predict unexpected news or events
3. **Gap Moves**: Large overnight gaps can invalidate stop losses
4. **Execution Risk**: Actual entry/exit prices may differ
5. **Sample Bias**: Limited historical data may skew probabilities

## Troubleshooting

### Issue: "Unable to fetch data for ticker"
- Check internet connection
- Verify ticker symbol is correct
- Wait a few moments and try again

### Issue: "Insufficient data for stock"
- Stock may be newly listed
- Try with a larger historical period
- Check if ticker symbol requires suffix (.BO)

### Issue: Slow performance
- Reduce number of stocks analyzed
- Increase cache duration
- Use background worker processes

## Contributing

To add new technical indicators or modify the analysis:

1. Edit `swing_analyzer.py` to add new indicator calculations
2. Update `probability_scorer.py` to factor in new signals
3. Modify UI in `templates/index.html` and `static/style.css`

## Dependencies

See `requirements.txt` for full list:
- Flask: Web framework
- yfinance: Stock data fetching
- pandas: Data manipulation
- numpy: Numerical computations
- ta: Technical analysis indicators
- Flask-CORS: Cross-Origin Resource Sharing
- requests: HTTP library
- python-dotenv: Environment configuration
- gunicorn: WSGI HTTP server

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, refer to:
- yfinance documentation: https://github.com/ranaroussi/yfinance
- TA library documentation: https://github.com/bukosabino/ta
- Flask documentation: https://flask.palletsprojects.com

---

**Last Updated**: December 11, 2024
