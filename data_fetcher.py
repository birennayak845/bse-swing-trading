"""
BSE Stock Data Fetcher Module
Fetches real-time and historical data for BSE stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Top BSE stocks (add .BO suffix for BSE)
BSE_TOP_STOCKS = [
    "RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "INFOSY.BO", "WIPRO.BO",
    "MARUTI.BO", "BAJAJFINSV.BO", "ICICIBANK.BO", "HDFC.BO", "KOTAKBANK.BO",
    "LT.BO", "ITC.BO", "AXISBANK.BO", "DMART.BO", "SUNPHARMA.BO",
    "ASIANPAINT.BO", "BHARTIARTL.BO", "ONGC.BO", "JSWSTEEL.BO", "TATASTEEL.BO",
    "NTPC.BO", "POWERGRID.BO", "SBILIFE.BO", "BAJAJFINSV.BO", "SBIN.BO"
]


class BSEDataFetcher:
    """Fetches and manages BSE stock data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
    
    def fetch_historical_data(self, ticker, period="3mo", interval="1d"):
        """
        Fetch historical stock data
        
        Args:
            ticker (str): Stock ticker with .BO suffix
            period (str): Period for data (e.g., '3mo', '1y', '1mo')
            interval (str): Interval (e.g., '1d', '1h', '5m')
        
        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        try:
            # Check cache
            cache_key = f"{ticker}_{period}_{interval}"
            if cache_key in self.cache:
                if datetime.now() - self.cache_time[cache_key] < self.cache_duration:
                    logger.info(f"Using cached data for {ticker}")
                    return self.cache[cache_key]
            
            logger.info(f"Fetching data for {ticker}...")
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            
            # Cache the data
            self.cache[cache_key] = data
            self.cache_time[cache_key] = datetime.now()
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def fetch_multiple_stocks(self, tickers, period="3mo"):
        """Fetch data for multiple stocks"""
        data_dict = {}
        for ticker in tickers:
            data = self.fetch_historical_data(ticker, period=period)
            if data is not None:
                data_dict[ticker] = data
        return data_dict
    
    def get_current_price(self, ticker):
        """Get current price for a ticker"""
        try:
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if data is not None and len(data) > 0:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            return None
    
    def get_stock_info(self, ticker):
        """Get stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            return {}


if __name__ == "__main__":
    fetcher = BSEDataFetcher()
    # Test fetching data
    data = fetcher.fetch_historical_data("RELIANCE.BO", period="1mo")
    print(data.head())
