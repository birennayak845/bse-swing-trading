from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import sys
import os

# Setup paths for serverless environment
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_path)

template_folder = os.path.join(base_path, 'templates')
static_folder = os.path.join(base_path, 'static')

# Create Flask app with correct paths
app = Flask(__name__, 
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path='/static')

CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modules
try:
    from ranker import SwingTradingRanker
    ranker = SwingTradingRanker(num_workers=3)
    logger.info("✓ Ranker initialized successfully")
except Exception as e:
    logger.error(f"✗ Error initializing ranker: {str(e)}")
    ranker = None

import json

# Cache system
cache = {}
cache_duration = timedelta(minutes=15)


def get_demo_stocks():
    """Return demo stock data for testing"""
    from datetime import datetime
    now = datetime.now()
    return [
        {
            'ticker': 'RELIANCE.BO',
            'name': 'Reliance Industries',
            'current_price': '₹2,835.50',
            'entry_price': '₹2,800.00',
            'stop_loss': '₹2,750.00',
            'target_price': '₹2,950.00',
            'risk': '₹50.00',
            'reward': '₹150.00',
            'rr_ratio': '1:3',
            'support': '₹2,750.00',
            'resistance': '₹2,900.00',
            'entry_time': 'Market Open',
            'swing_score': '78.5',
            'probability_score': '72.3%',
            'rsi': '65.2',
            'macd': '0.0234',
            'pe_ratio': '23.4',
            'reasons': ['Strong uptrend', 'RSI bullish', 'Above SMA200']
        },
        {
            'ticker': 'TCS.BO',
            'name': 'Tata Consultancy Services',
            'current_price': '₹3,845.25',
            'entry_price': '₹3,820.00',
            'stop_loss': '₹3,750.00',
            'target_price': '₹3,980.00',
            'risk': '₹70.00',
            'reward': '₹160.00',
            'rr_ratio': '1:2.3',
            'support': '₹3,750.00',
            'resistance': '₹3,950.00',
            'entry_time': '10:30 AM',
            'swing_score': '75.2',
            'probability_score': '68.9%',
            'rsi': '62.1',
            'macd': '0.0189',
            'pe_ratio': '28.1',
            'reasons': ['Breakout confirmed', 'Volume increase', 'Bollinger upper']
        },
        {
            'ticker': 'HDFCBANK.BO',
            'name': 'HDFC Bank',
            'current_price': '₹1,945.80',
            'entry_price': '₹1,920.00',
            'stop_loss': '₹1,880.00',
            'target_price': '₹2,050.00',
            'risk': '₹40.00',
            'reward': '₹130.00',
            'rr_ratio': '1:3.25',
            'support': '₹1,880.00',
            'resistance': '₹2,000.00',
            'entry_time': 'Market Open',
            'swing_score': '81.3',
            'probability_score': '75.6%',
            'rsi': '68.5',
            'macd': '0.0312',
            'pe_ratio': '21.2',
            'reasons': ['Strong momentum', 'Support hold', 'Ascending triangle']
        },
        {
            'ticker': 'INFOSY.BO',
            'name': 'Infosys Limited',
            'current_price': '₹1,725.40',
            'entry_price': '₹1,700.00',
            'stop_loss': '₹1,665.00',
            'target_price': '₹1,820.00',
            'risk': '₹35.00',
            'reward': '₹120.00',
            'rr_ratio': '1:3.4',
            'support': '₹1,665.00',
            'resistance': '₹1,800.00',
            'entry_time': '11:15 AM',
            'swing_score': '72.8',
            'probability_score': '66.2%',
            'rsi': '59.7',
            'macd': '0.0156',
            'pe_ratio': '26.8',
            'reasons': ['Consolidation break', 'MACD positive', 'EMA crossover']
        },
        {
            'ticker': 'WIPRO.BO',
            'name': 'Wipro Limited',
            'current_price': '₹428.35',
            'entry_price': '₹420.00',
            'stop_loss': '₹405.00',
            'target_price': '₹450.00',
            'risk': '₹15.00',
            'reward': '₹30.00',
            'rr_ratio': '1:2',
            'support': '₹405.00',
            'resistance': '₹440.00',
            'entry_time': 'Market Open',
            'swing_score': '69.5',
            'probability_score': '61.8%',
            'rsi': '55.3',
            'macd': '0.0098',
            'pe_ratio': '18.9',
            'reasons': ['Reversal pattern', 'Volume confirmation', 'RSI bounce']
        },
        {
            'ticker': 'MARUTI.BO',
            'name': 'Maruti Suzuki',
            'current_price': '₹10,245.60',
            'entry_price': '₹10,150.00',
            'stop_loss': '₹10,000.00',
            'target_price': '₹10,500.00',
            'risk': '₹150.00',
            'reward': '₹350.00',
            'rr_ratio': '1:2.33',
            'support': '₹10,000.00',
            'resistance': '₹10,400.00',
            'entry_time': '10:45 AM',
            'swing_score': '76.9',
            'probability_score': '70.4%',
            'rsi': '64.8',
            'macd': '0.0267',
            'pe_ratio': '8.5',
            'reasons': ['Flag breakout', 'OBV positive', 'Above 50 SMA']
        },
        {
            'ticker': 'ICICIBANK.BO',
            'name': 'ICICI Bank',
            'current_price': '₹1,085.25',
            'entry_price': '₹1,065.00',
            'stop_loss': '₹1,035.00',
            'target_price': '₹1,150.00',
            'risk': '₹30.00',
            'reward': '₹85.00',
            'rr_ratio': '1:2.83',
            'support': '₹1,035.00',
            'resistance': '₹1,120.00',
            'entry_time': 'Market Open',
            'swing_score': '74.1',
            'probability_score': '67.9%',
            'rsi': '61.2',
            'macd': '0.0201',
            'pe_ratio': '16.3',
            'reasons': ['Channel breakup', 'RSI overbought exit', 'Trend confirmation']
        },
        {
            'ticker': 'HDFC.BO',
            'name': 'Housing Development Finance',
            'current_price': '₹3,295.80',
            'entry_price': '₹3,250.00',
            'stop_loss': '₹3,180.00',
            'target_price': '₹3,450.00',
            'risk': '₹70.00',
            'reward': '₹200.00',
            'rr_ratio': '1:2.86',
            'support': '₹3,180.00',
            'resistance': '₹3,400.00',
            'entry_time': '11:00 AM',
            'swing_score': '73.6',
            'probability_score': '64.5%',
            'rsi': '58.9',
            'macd': '0.0178',
            'pe_ratio': '24.7',
            'reasons': ['Gartley pattern', 'MACD crossover', 'Volume spike']
        },
        {
            'ticker': 'KOTAKBANK.BO',
            'name': 'Kotak Mahindra Bank',
            'current_price': '₹1,765.45',
            'entry_price': '₹1,740.00',
            'stop_loss': '₹1,700.00',
            'target_price': '₹1,880.00',
            'risk': '₹40.00',
            'reward': '₹140.00',
            'rr_ratio': '1:3.5',
            'support': '₹1,700.00',
            'resistance': '₹1,850.00',
            'entry_time': 'Market Open',
            'swing_score': '79.2',
            'probability_score': '73.1%',
            'rsi': '66.7',
            'macd': '0.0289',
            'pe_ratio': '19.8',
            'reasons': ['Bull pennant', 'RSI strength', 'Above 200 SMA']
        },
        {
            'ticker': 'LT.BO',
            'name': 'Larsen & Toubro',
            'current_price': '₹3,145.65',
            'entry_price': '₹3,100.00',
            'stop_loss': '₹3,030.00',
            'target_price': '₹3,300.00',
            'risk': '₹70.00',
            'reward': '₹200.00',
            'rr_ratio': '1:2.86',
            'support': '₹3,030.00',
            'resistance': '₹3,250.00',
            'entry_time': '10:30 AM',
            'swing_score': '75.8',
            'probability_score': '69.7%',
            'rsi': '63.4',
            'macd': '0.0224',
            'pe_ratio': '27.5',
            'reasons': ['Double bottom', 'Volume confirmation', 'Above EMA200']
        }
    ]


# ==================== ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'ranker_initialized': ranker is not None
    })


@app.route('/', methods=['GET'])
def index():
    """Serve the main dashboard page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        # Fallback HTML
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BSE Swing Trading Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                h1 { color: #333; }
                .status { padding: 15px; margin: 10px 0; border-radius: 4px; }
                .ok { background: #d4edda; color: #155724; }
                .error { background: #f8d7da; color: #721c24; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 BSE Swing Trading Platform</h1>
                <div class="status ok">
                    <strong>✓ Server is running!</strong>
                </div>
                <p>The API is operational and ready to serve requests.</p>
                <h3>Available APIs:</h3>
                <ul>
                    <li><a href="/api/health">Health Check</a></li>
                    <li><a href="/api/top-stocks">Top Stocks</a></li>
                </ul>
            </div>
        </body>
        </html>
        """


@app.route('/api/top-stocks', methods=['GET'])
def get_top_stocks():
    """Get top 10 stocks for swing trading"""
    try:
        min_probability = request.args.get('min_probability', 40, type=float)
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        cache_key = f'top_stocks_{min_probability}'
        
        # Check cache
        if not refresh and cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if datetime.now() - cached_time < cache_duration:
                logger.info("✓ Returning cached results")
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'timestamp': cached_time.isoformat(),
                    'from_cache': True
                })
        
        if ranker is None:
            logger.warning("Ranker not initialized - returning demo data")
            demo_data = get_demo_stocks()
            return jsonify({
                'success': True,
                'data': demo_data,
                'timestamp': datetime.now().isoformat(),
                'demo_mode': True,
                'count': len(demo_data)
            })
        
        logger.info(f"Fetching top stocks (min_probability={min_probability})...")
        
        # Get fresh data
        try:
            top_10 = ranker.get_top_10_stocks(min_probability=min_probability)
            
            if not top_10:
                logger.warning("No stocks returned - using demo data")
                demo_data = get_demo_stocks()
                return jsonify({
                    'success': True,
                    'data': demo_data,
                    'timestamp': datetime.now().isoformat(),
                    'demo_mode': True,
                    'count': len(demo_data)
                })
            
            # Format for display
            formatted_results = [ranker.format_for_display(stock) for stock in top_10]
            
            # Cache results
            cache[cache_key] = (formatted_results, datetime.now())
            
            return jsonify({
                'success': True,
                'data': formatted_results,
                'timestamp': datetime.now().isoformat(),
                'from_cache': False,
                'count': len(formatted_results)
            })
        except Exception as ranker_error:
            logger.error(f"Ranker error: {str(ranker_error)} - returning demo data")
            demo_data = get_demo_stocks()
            return jsonify({
                'success': True,
                'data': demo_data,
                'timestamp': datetime.now().isoformat(),
                'demo_mode': True,
                'note': 'Using demo data due to data fetching issues',
                'count': len(demo_data)
            })
    except Exception as e:
        logger.error(f"Error fetching top stocks: {str(e)}")
        demo_data = get_demo_stocks()
        return jsonify({
            'success': True,
            'data': demo_data,
            'demo_mode': True,
            'note': 'Using demo data',
            'count': len(demo_data)
        })


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_analysis(ticker):
    """Get detailed analysis for a specific stock"""
    try:
        # Add .BO suffix if not present
        if not ticker.endswith('.BO'):
            ticker = f"{ticker}.BO"
        
        cache_key = f'stock_{ticker}'
        
        # Check cache
        if cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if datetime.now() - cached_time < cache_duration:
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'from_cache': True
                })
        
        if ranker is None:
            return jsonify({'success': False, 'error': 'Ranker not initialized'}), 500
        
        # Get analysis
        analysis = ranker.analyze_single_stock(ticker)
        
        if analysis:
            # Cache it
            cache[cache_key] = (analysis, datetime.now())
            
            return jsonify({
                'success': True,
                'data': analysis,
                'from_cache': False
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Could not analyze {ticker}'
            }), 404
    except Exception as e:
        logger.error(f"Error analyzing stock: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def manage_watchlist():
    """Manage user watchlist"""
    try:
        watchlist_file = '/tmp/watchlist.json'
        
        if request.method == 'GET':
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r') as f:
                    watchlist = json.load(f)
            else:
                watchlist = []
            
            return jsonify({'success': True, 'data': watchlist})
        
        elif request.method == 'POST':
            data = request.json
            ticker = data.get('ticker', '').upper()
            
            if not ticker:
                return jsonify({'success': False, 'error': 'Ticker required'}), 400
            
            # Load existing watchlist
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r') as f:
                    watchlist = json.load(f)
            else:
                watchlist = []
            
            if ticker not in watchlist:
                watchlist.append(ticker)
                with open(watchlist_file, 'w') as f:
                    json.dump(watchlist, f)
            
            return jsonify({'success': True, 'data': watchlist})
        
        elif request.method == 'DELETE':
            data = request.json
            ticker = data.get('ticker', '').upper()
            
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r') as f:
                    watchlist = json.load(f)
                
                if ticker in watchlist:
                    watchlist.remove(ticker)
                    with open(watchlist_file, 'w') as f:
                        json.dump(watchlist, f)
            else:
                watchlist = []
            
            return jsonify({'success': True, 'data': watchlist})
    except Exception as e:
        logger.error(f"Watchlist error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ==================== WSGI ENTRY POINT ====================

# For local development
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
