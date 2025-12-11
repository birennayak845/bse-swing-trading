"""
Flask Backend for Swing Trading Analysis
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
from ranker import SwingTradingRanker
import json
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ranker
ranker = SwingTradingRanker(num_workers=5)

# Cache for results
cache = {}
cache_duration = timedelta(minutes=15)


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/top-stocks', methods=['GET'])
def get_top_stocks():
    """
    Get top 10 stocks for swing trading
    
    Query params:
    - min_probability: Minimum probability threshold (default: 40)
    - refresh: Force refresh data (default: False)
    """
    try:
        min_probability = request.args.get('min_probability', 40, type=float)
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        cache_key = f'top_stocks_{min_probability}'
        
        # Check cache
        if not refresh and cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if datetime.now() - cached_time < cache_duration:
                logger.info("Returning cached results")
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'timestamp': cached_time.isoformat(),
                    'from_cache': True
                })
        
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
        
        logger.info(f"Analyzing {ticker}...")
        result = ranker.analyze_single_stock(ticker)
        
        if result:
            formatted = ranker.format_for_display(result)
            return jsonify({
                'success': True,
                'data': formatted
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Unable to analyze {ticker}'
            }), 404
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def manage_watchlist():
    """Manage watchlist"""
    try:
        watchlist_file = 'watchlist.json'
        
        if request.method == 'GET':
            # Get watchlist
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r') as f:
                    watchlist = json.load(f)
            else:
                watchlist = []
            return jsonify({'success': True, 'data': watchlist})
        
        elif request.method == 'POST':
            # Add to watchlist
            data = request.json
            ticker = data.get('ticker')
            
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
            # Remove from watchlist
            data = request.json
            ticker = data.get('ticker')
            
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r') as f:
                    watchlist = json.load(f)
                
                if ticker in watchlist:
                    watchlist.remove(ticker)
                    with open(watchlist_file, 'w') as f:
                        json.dump(watchlist, f)
            
            return jsonify({'success': True, 'data': watchlist})
    except Exception as e:
        logger.error(f"Watchlist error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
