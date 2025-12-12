#!/bin/bash
# Quick Start Script for BSE Swing Trading Platform
# Run this to get the app running locally in 30 seconds

echo "🚀 Starting BSE Swing Trading Platform..."
echo ""

# Navigate to project directory
cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app

# Check if requirements are installed
echo "✓ Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "  Installing requirements..."
    pip install -q -r requirements.txt
else
    echo "  ✓ All dependencies installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Starting Flask Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Open your browser and go to:"
echo "   👉 http://localhost:5000"
echo ""
echo "🔄 Click 'Refresh Data' to fetch real NSE stock data"
echo ""
echo "⏹  Press CTRL+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Flask app
python3 app.py
