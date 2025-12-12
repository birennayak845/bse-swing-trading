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
            return jsonify({
                'success': False,
                'error': 'Ranker not initialized'
            }), 500
        
        logger.info(f"Fetching top stocks (min_probability={min_probability})...")
        
        # Get fresh data
        top_10 = ranker.get_top_10_stocks(min_probability=min_probability)
        
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
    except Exception as e:
        logger.error(f"Error fetching top stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
