# Next.js + Flask Swing Trading Platform - Quick Start Guide

Complete guide to run the full-stack swing trading application with Next.js frontend and Flask backend.

## Architecture

```
┌─────────────────────┐
│   Next.js Frontend  │  Port 3000 (User Interface)
│   (Minimalist UI)   │
└──────────┬──────────┘
           │ HTTP/REST API
           ▼
┌─────────────────────┐
│   Flask Backend     │  Port 5000 (Data & Analysis)
│   (Stock Analysis)  │
└──────────┬──────────┘
           │ yfinance
           ▼
┌─────────────────────┐
│  Yahoo Finance API  │  (Stock Market Data)
└─────────────────────┘
```

## Features

### Frontend (Next.js)
- Clean, minimalist design
- Real-time stock data display
- Configurable number of stocks (5-30)
- Probability filtering (30%-70%)
- Responsive design with dark mode
- Loading states and error handling

### Backend (Flask)
- Stock data fetching from Yahoo Finance
- Technical analysis (RSI, MACD, Bollinger Bands)
- Swing trading score calculation
- Probability prediction algorithm
- Entry/exit/stop-loss recommendations
- 15-minute cache for performance

## Prerequisites

- **Python 3.8+** for Flask backend
- **Node.js 18+** for Next.js frontend
- **Internet connection** for stock data

## Installation

### Step 1: Set Up Python Backend

```bash
# Navigate to project directory
cd swing_trading_app

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Next.js Frontend

```bash
# Navigate to frontend directory
cd frontend

# Fix npm permissions if needed (macOS/Linux)
sudo chown -R $(whoami) ~/.npm

# Install dependencies
npm install --legacy-peer-deps
```

### Step 3: Configure Environment

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Running the Application

### Option 1: Run Both Servers (Recommended)

**Terminal 1 - Flask Backend:**
```bash
cd swing_trading_app
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

**Terminal 2 - Next.js Frontend:**
```bash
cd swing_trading_app/frontend
npm run dev
```

You should see:
```
▲ Next.js 16.0.10
- Local:        http://localhost:3000
- Ready in 2.5s
```

**Access the App:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Option 2: Production Mode

**Backend:**
```bash
cd swing_trading_app
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Frontend:**
```bash
cd swing_trading_app/frontend
npm run build
npm start
```

## Using the Application

1. **Open Browser**: Navigate to http://localhost:3000

2. **Select Parameters**:
   - Choose number of stocks (5, 10, 15, 20, 25, or 30)
   - Set minimum probability threshold (30%, 40%, 50%, 60%, 70%)

3. **View Results**:
   - Stock rankings by probability
   - Entry price recommendations
   - Target prices and stop losses
   - Risk/reward ratios
   - Technical indicators (RSI, Swing Score)

4. **Refresh Data**:
   - Click "Refresh" button to fetch latest data
   - Data is cached for 15 minutes by default

## API Endpoints

### Get Top Stocks
```bash
GET /api/top-stocks?limit=10&min_probability=40&refresh=false
```

**Parameters:**
- `limit`: Number of stocks (1-50, default: 10)
- `min_probability`: Minimum probability (0-100, default: 40)
- `refresh`: Force refresh (true/false, default: false)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "RELIANCE.BO",
      "name": "Reliance Industries",
      "probability_score": "72.3%",
      "entry_price": "₹2500.00",
      "target_price": "₹2600.00",
      "stop_loss": "₹2450.00",
      "swing_score": "75.5",
      ...
    }
  ],
  "timestamp": "2024-12-15T10:30:00",
  "from_cache": false
}
```

### Health Check
```bash
GET /api/health
```

## Project Structure

```
swing_trading_app/
├── frontend/                    # Next.js Application
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Main page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── StockCard.tsx       # Stock display component
│   │   └── LoadingSkeleton.tsx # Loading UI
│   ├── lib/
│   │   └── api.ts              # API integration
│   ├── .env.local              # Environment config
│   └── package.json            # Dependencies
│
├── app.py                       # Flask backend
├── data_fetcher.py             # Stock data fetcher
├── swing_analyzer.py           # Technical analysis
├── probability_scorer.py       # Probability calculations
├── ranker.py                   # Stock ranking
└── requirements.txt            # Python dependencies
```

## Customization

### Change Number of Stocks Analyzed

Edit `ranker.py`:
```python
# Line 111
analyze_count = min(len(BSE_TOP_STOCKS), max(limit * 2, 20))
# Increase multiplier to analyze more stocks
```

### Adjust Cache Duration

Edit `app.py`:
```python
# Line 24
cache_duration = timedelta(minutes=15)
# Change to desired duration
```

### Modify UI Colors

Edit `frontend/app/globals.css`:
```css
:root {
  --background: #ffffff;
  --foreground: #171717;
}
```

### Change Technical Indicators

Edit `swing_analyzer.py`:
```python
# Adjust RSI thresholds
self.min_rsi_oversold = 30
self.max_rsi_overbought = 70

# Adjust stop loss multiplier
atr_multiplier = 1.5
```

## Troubleshooting

### Backend Issues

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**"Address already in use" error:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**"Failed to fetch stocks" error:**
- Verify Flask backend is running on port 5000
- Check `.env.local` has correct API URL
- Look for CORS errors in browser console

**npm install fails:**
```bash
# Clear cache and retry
npm cache clean --force
npm install --legacy-peer-deps
```

**Page shows no data:**
- Check browser console for errors
- Verify backend is returning data: `curl http://localhost:5000/api/health`
- Try refreshing the page

### Data Issues

**No stocks meet criteria:**
- Lower min probability threshold
- Check if market is open
- Verify Yahoo Finance is accessible

**Stocks loading slowly:**
- First load takes 30-60 seconds (analyzing 20+ stocks)
- Subsequent loads use cache (instant)
- Consider reducing number of stocks analyzed

## Performance Tips

1. **Use Cache**: Don't refresh too frequently (data is cached for 15 minutes)
2. **Limit Stocks**: Start with 10 stocks, increase if needed
3. **Production Build**: Use `npm run build && npm start` for better performance
4. **Background Workers**: Increase `num_workers=5` in `ranker.py` for faster analysis

## Deployment

### Deploy Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL`: Your backend URL

### Deploy Backend (Railway/Render)
- Push code to GitHub
- Connect repository to Railway/Render
- Add `requirements.txt` and `app.py`
- Set start command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

## Risk Disclaimer

⚠️ **IMPORTANT**: This tool is for **educational purposes only** and is NOT financial advice.

- Stock trading involves substantial risk
- You can lose your entire investment
- Past performance doesn't guarantee future results
- Always do your own research
- Consult a licensed financial advisor before trading

## Support

### Common Questions

**Q: Can I use this for live trading?**
A: This is an educational tool. Use at your own risk.

**Q: Which stocks are analyzed?**
A: Top BSE stocks defined in `data_fetcher.py`

**Q: How accurate are the predictions?**
A: Predictions are based on technical analysis and historical patterns. No guarantees.

**Q: Can I add my own stocks?**
A: Yes, modify `BSE_TOP_STOCKS` in `data_fetcher.py`

### Resources

- Next.js Docs: https://nextjs.org/docs
- Flask Docs: https://flask.palletsprojects.com
- Technical Analysis: https://github.com/bukosabino/ta
- Yahoo Finance: https://github.com/ranaroussi/yfinance

---

**Version**: 1.0.0
**Last Updated**: December 15, 2024
**Author**: Built with Claude Code
