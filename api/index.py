from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import sys
import os
import json

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

# Import modules (lazy initialization to avoid cold-start timeout)
try:
    from ranker import SwingTradingRanker
    ranker = None  # Will be initialized on first request
    logger.info("✓ Ranker module imported successfully (lazy init)")
except Exception as import_error:
    logger.error(f"✗ Error importing ranker module: {str(import_error)}")
    ranker = None

def get_ranker():
    """Lazy initialization of ranker - only initialize when needed"""
    global ranker
    if ranker is None:
        try:
            logger.info("Initializing ranker on first request...")
            ranker = SwingTradingRanker(num_workers=3)
            logger.info("✓ Ranker initialized successfully")
        except Exception as init_error:
            logger.error(f"✗ Error initializing ranker: {str(init_error)}")
            logger.error(f"  Error type: {type(init_error).__name__}")
            logger.error(f"  This likely means data fetching is timing out in serverless")
            return None
    return ranker

# Cache system with persistence
cache_file = '/tmp/stocks_cache.json'
cache = {
    'data': None,
    'timestamp': None,
    'count': 10
}

# Load cached data from disk if available
def load_cache():
    global cache
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                cache['data'] = cached.get('data')
                cache['timestamp'] = cached.get('timestamp')
                cache['count'] = cached.get('count', 10)
                logger.info("✓ Loaded cached stocks from disk")
    except Exception as e:
        logger.error(f"Error loading cache: {str(e)}")

# Save cache to disk
def save_cache():
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
            logger.info("✓ Saved stocks to cache")
    except Exception as e:
        logger.error(f"Error saving cache: {str(e)}")

# Load cache on startup
load_cache()


# ==================== ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'ranker_available': ranker is not None or get_ranker() is not None,
        'cached_data_available': cache['data'] is not None,
        'last_fetch': cache['timestamp']
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
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #202124; color: #fff; }
                .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
                h1 { color: #fff; }
                .status { padding: 15px; margin: 10px 0; border-radius: 4px; background: #35363a; border-left: 4px solid #4285f4; }
                a { color: #4285f4; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 BSE Swing Trading Platform</h1>
                <div class="status">
                    <strong>✓ Server is running</strong>
                </div>
                <p>The API is operational. Available endpoints:</p>
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
    """Get top stocks for swing trading with caching"""
    global cache
    
    try:
        min_probability = request.args.get('min_probability', 40, type=float)
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        num_stocks = request.args.get('count', 10, type=int)
        
        # Validate count
        if num_stocks < 1 or num_stocks > 100:
            num_stocks = 10
        
        logger.info(f"Request: refresh={refresh}, count={num_stocks}, min_prob={min_probability}")
        
        # If not refresh and we have cached data, return it
        if not refresh and cache['data'] is not None:
            logger.info(f"✓ Returning cached data ({len(cache['data'])} stocks)")
            # Return requested number of stocks from cache
            stocks_to_return = cache['data'][:num_stocks]
            return jsonify({
                'success': True,
                'data': stocks_to_return,
                'timestamp': cache['timestamp'],
                'from_cache': True,
                'total_cached': len(cache['data']),
                'count': len(stocks_to_return)
            })
        
        # Try to fetch fresh data
        current_ranker = get_ranker()
        if current_ranker is None:
            logger.error("Ranker initialization failed")
            if cache['data']:
                logger.info("Returning cached data due to ranker initialization error")
                stocks_to_return = cache['data'][:num_stocks]
                return jsonify({
                    'success': True,
                    'data': stocks_to_return,
                    'timestamp': cache['timestamp'],
                    'from_cache': True,
                    'total_cached': len(cache['data']),
                    'count': len(stocks_to_return)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Data fetcher initialization failed. Please wait a moment and try again. If the problem persists, the market data service may be temporarily unavailable.',
                    'timestamp': datetime.now().isoformat()
                }), 503
        
        logger.info("Fetching fresh data from market...")
        
        try:
            # Get more stocks than requested to have flexibility
            top_stocks = current_ranker.get_top_10_stocks(
                min_probability=min_probability,
                stock_list=None  # Use default list
            )
            
            if not top_stocks:
                logger.error("No stocks returned from ranker")
                if cache['data']:
                    logger.info("Returning cached data - ranker returned empty")
                    stocks_to_return = cache['data'][:num_stocks]
                    return jsonify({
                        'success': True,
                        'data': stocks_to_return,
                        'timestamp': cache['timestamp'],
                        'from_cache': True,
                        'total_cached': len(cache['data']),
                        'count': len(stocks_to_return)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to fetch market data. No cached data available.',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            
            # Format results
            formatted_results = [current_ranker.format_for_display(stock) for stock in top_stocks]
            
            # Update cache
            cache['data'] = formatted_results
            cache['timestamp'] = datetime.now().isoformat()
            cache['count'] = len(formatted_results)
            save_cache()
            
            logger.info(f"✓ Fetched {len(formatted_results)} stocks successfully")
            
            # Return requested number
            stocks_to_return = formatted_results[:num_stocks]
            return jsonify({
                'success': True,
                'data': stocks_to_return,
                'timestamp': cache['timestamp'],
                'from_cache': False,
                'total_fetched': len(formatted_results),
                'count': len(stocks_to_return)
            })
            
        except Exception as ranker_error:
            logger.error(f"Ranker fetch error: {str(ranker_error)}")
            if cache['data']:
                logger.info("Returning cached data due to fetch error")
                stocks_to_return = cache['data'][:num_stocks]
                return jsonify({
                    'success': True,
                    'data': stocks_to_return,
                    'timestamp': cache['timestamp'],
                    'from_cache': True,
                    'total_cached': len(cache['data']),
                    'count': len(stocks_to_return),
                    'note': f'Using cached data from {cache["timestamp"]}'
                })
            else:
                error_msg = f"Failed to fetch market data: {str(ranker_error)}"
                logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }), 500
                
    except Exception as e:
        logger.error(f"Top stocks error: {str(e)}")
        if cache['data']:
            logger.info("Returning cached data due to general error")
            stocks_to_return = cache['data'][:num_stocks]
            return jsonify({
                'success': True,
                'data': stocks_to_return,
                'timestamp': cache['timestamp'],
                'from_cache': True,
                'count': len(stocks_to_return)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_analysis(ticker):
    """Get detailed analysis for a specific stock"""
    try:
        # Add .BO suffix if not present
        if not ticker.endswith('.BO'):
            ticker = f"{ticker}.BO"
        
        current_ranker = get_ranker()
        if current_ranker is None:
            return jsonify({'success': False, 'error': 'Ranker not initialized'}), 503
        
        logger.info(f"Analyzing {ticker}...")
        
        # Get analysis
        analysis = current_ranker.analyze_single_stock(ticker)
        
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
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
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ==================== WSGI ENTRY POINT ====================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
