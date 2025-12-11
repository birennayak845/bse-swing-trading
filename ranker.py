"""
Stock Ranking and Filtering Engine
Ranks top 10 stocks for swing trading opportunities
"""

import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_fetcher import BSEDataFetcher, BSE_TOP_STOCKS
from swing_analyzer import SwingTradingAnalyzer
from probability_scorer import ProbabilityScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SwingTradingRanker:
    """Ranks stocks for swing trading opportunities"""
    
    def __init__(self, num_workers=5):
        self.fetcher = BSEDataFetcher()
        self.analyzer = SwingTradingAnalyzer()
        self.scorer = ProbabilityScorer()
        self.num_workers = num_workers
    
    def analyze_single_stock(self, ticker):
        """
        Analyze a single stock for swing trading opportunity
        
        Args:
            ticker (str): Stock ticker with .BO suffix
        
        Returns:
            dict: Analysis results
        """
        try:
            logger.info(f"Analyzing {ticker}...")
            
            # Fetch data
            data = self.fetcher.fetch_historical_data(ticker, period="3mo")
            if data is None or len(data) < 50:
                logger.warning(f"Insufficient data for {ticker}")
                return None
            
            # Calculate indicators
            data_with_indicators = self.analyzer.calculate_technical_indicators(data)
            
            # Get swing score
            swing_score_data = self.analyzer.calculate_swing_score(data_with_indicators, ticker)
            
            # Calculate trade levels
            trade_levels = self.analyzer.calculate_trade_levels(data_with_indicators)
            if trade_levels is None:
                return None
            
            # Get entry time recommendation
            entry_time = self.analyzer.get_entry_time(data_with_indicators)
            
            # Calculate probability
            probability = self.scorer.calculate_overall_probability(
                data_with_indicators,
                trade_levels['entry_price'],
                trade_levels['target_price'],
                trade_levels['stop_loss'],
                swing_score_data['score'],
                trade_levels['rr_ratio']
            )
            
            # Get stock info
            stock_info = self.fetcher.get_stock_info(ticker)
            
            return {
                'ticker': ticker,
                'name': stock_info.get('name', 'N/A'),
                'sector': stock_info.get('sector', 'N/A'),
                'current_price': trade_levels['entry_price'],
                'entry_price': trade_levels['entry_price'],
                'stop_loss': trade_levels['stop_loss'],
                'target_price': trade_levels['target_price'],
                'risk': trade_levels['risk'],
                'reward': trade_levels['reward'],
                'rr_ratio': trade_levels['rr_ratio'],
                'support': trade_levels['support'],
                'resistance': trade_levels['resistance'],
                'entry_time': entry_time,
                'swing_score': swing_score_data['score'],
                'swing_score_reasons': swing_score_data['reasons'],
                'probability_score': probability,
                'rsi': swing_score_data['rsi'],
                'macd': swing_score_data['macd'],
                'pe_ratio': stock_info.get('pe_ratio', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            return None
    
    def get_top_10_stocks(self, stock_list=None, min_probability=40):
        """
        Get top 10 stocks for swing trading
        
        Args:
            stock_list (list): List of tickers to analyze (default: BSE_TOP_STOCKS)
            min_probability (float): Minimum probability threshold
        
        Returns:
            list: Top 10 stocks sorted by probability and swing score
        """
        if stock_list is None:
            stock_list = BSE_TOP_STOCKS[:20]  # Analyze top 20 to get top 10
        
        results = []
        
        # Use thread pool for faster analysis
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_ticker = {
                executor.submit(self.analyze_single_stock, ticker): ticker 
                for ticker in stock_list
            }
            
            for future in as_completed(future_to_ticker):
                try:
                    result = future.result()
                    if result and result['probability_score'] >= min_probability:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error in thread: {str(e)}")
        
        # Sort by probability score (descending) and then by swing score
        results.sort(key=lambda x: (x['probability_score'], x['swing_score']), reverse=True)
        
        # Return top 10
        return results[:10]
    
    def format_for_display(self, stock_data):
        """
        Format stock data for web display
        
        Args:
            stock_data (dict): Stock analysis data
        
        Returns:
            dict: Formatted data
        """
        return {
            'ticker': stock_data['ticker'],
            'name': stock_data['name'],
            'sector': stock_data['sector'],
            'current_price': f"₹{stock_data['current_price']:.2f}",
            'entry_price': f"₹{stock_data['entry_price']:.2f}",
            'stop_loss': f"₹{stock_data['stop_loss']:.2f}",
            'target_price': f"₹{stock_data['target_price']:.2f}",
            'risk': f"₹{stock_data['risk']:.2f}",
            'reward': f"₹{stock_data['reward']:.2f}",
            'rr_ratio': f"{stock_data['rr_ratio']:.2f}:1",
            'support': f"₹{stock_data['support']:.2f}",
            'resistance': f"₹{stock_data['resistance']:.2f}",
            'entry_time': stock_data['entry_time'],
            'swing_score': f"{stock_data['swing_score']:.1f}",
            'probability_score': f"{stock_data['probability_score']:.1f}%",
            'rsi': f"{stock_data['rsi']:.1f}" if stock_data['rsi'] else 'N/A',
            'macd': f"{stock_data['macd']:.4f}" if stock_data['macd'] else 'N/A',
            'pe_ratio': stock_data['pe_ratio'],
            'reasons': stock_data['swing_score_reasons'],
        }


if __name__ == "__main__":
    ranker = SwingTradingRanker()
    top_10 = ranker.get_top_10_stocks()
    
    print("\n" + "="*100)
    print("TOP 10 STOCKS FOR SWING TRADING (LONG)")
    print("="*100)
    
    for i, stock in enumerate(top_10, 1):
        formatted = ranker.format_for_display(stock)
        print(f"\n{i}. {formatted['ticker']} - {formatted['name']}")
        print(f"   Sector: {formatted['sector']}")
        print(f"   Current Price: {formatted['current_price']}")
        print(f"   Entry: {formatted['entry_price']} | SL: {formatted['stop_loss']} | Target: {formatted['target_price']}")
        print(f"   Risk/Reward: {formatted['risk']}/{formatted['reward']} ({formatted['rr_ratio']})")
        print(f"   Entry Time: {formatted['entry_time']}")
        print(f"   Swing Score: {formatted['swing_score']}/100")
        print(f"   Win Probability: {formatted['probability_score']}")
