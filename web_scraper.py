"""
Web Scraper for BSE Stock Data
Fetches real-time and historical data from multiple sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import re
import json
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for BSE stock data from multiple sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
    
    def scrape_moneycontrol(self, symbol):
        """
        Scrape current price and data from Moneycontrol
        Symbol format: RELIANCE (without .BO)
        """
        try:
            logger.info(f"Scraping Moneycontrol for {symbol}...")
            
            url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol}"
            
            response = self.session.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find price in different locations
                price_text = None
                
                # Method 1: Look for price in span with specific class
                price_span = soup.find('span', {'class': re.compile(r'.*price.*', re.I)})
                if price_span:
                    price_text = price_span.get_text(strip=True)
                
                # Method 2: Look in main content
                if not price_text:
                    main_price = soup.find('div', {'class': re.compile(r'.*main.*price.*', re.I)})
                    if main_price:
                        price_text = main_price.get_text(strip=True)
                
                if price_text:
                    # Extract numeric value
                    price_match = re.search(r'₹\s*([\d,\.]+)', price_text)
                    if price_match:
                        current_price = float(price_match.group(1).replace(',', ''))
                        logger.info(f"✓ Moneycontrol: {symbol} = ₹{current_price:.2f}")
                        
                        return {
                            'source': 'moneycontrol',
                            'symbol': symbol,
                            'current_price': current_price,
                            'timestamp': datetime.now().isoformat()
                        }
        
        except Exception as e:
            logger.warning(f"Moneycontrol scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_bseindia(self, symbol):
        """
        Scrape from BSE India official website
        Symbol format: RELIANCE (without .BO)
        """
        try:
            logger.info(f"Scraping BSE India for {symbol}...")
            
            # BSE search endpoint
            url = "https://www.bseindia.com/markets/commoditiesearch/commsearch.aspx"
            
            params = {
                'scripcode': symbol,
                'Group': 'EQ'
            }
            
            response = self.session.get(url, params=params, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for price data in tables
                price_data = {}
                
                # Find all tables with price information
                for table in soup.find_all('table'):
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            label = cols[0].get_text(strip=True).lower()
                            value = cols[1].get_text(strip=True)
                            
                            if 'last traded price' in label or 'ltp' in label or 'current price' in label:
                                price_match = re.search(r'([\d,\.]+)', value)
                                if price_match:
                                    current_price = float(price_match.group(1).replace(',', ''))
                                    logger.info(f"✓ BSE India: {symbol} = ₹{current_price:.2f}")
                                    
                                    return {
                                        'source': 'bseindia',
                                        'symbol': symbol,
                                        'current_price': current_price,
                                        'timestamp': datetime.now().isoformat()
                                    }
        
        except Exception as e:
            logger.warning(f"BSE India scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_economictimes(self, symbol):
        """
        Scrape from Economic Times
        Symbol format: RELIANCE (without .BO)
        """
        try:
            logger.info(f"Scraping Economic Times for {symbol}...")
            
            url = f"https://economictimes.indiatimes.com/markets/stocks/{symbol.lower()}.cms"
            
            response = self.session.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for price in various locations
                price_patterns = [
                    r'Current Price.*?₹([\d,\.]+)',
                    r'LTP.*?₹([\d,\.]+)',
                    r'Last Traded.*?₹([\d,\.]+)'
                ]
                
                page_text = soup.get_text()
                
                for pattern in price_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        current_price = float(match.group(1).replace(',', ''))
                        logger.info(f"✓ Economic Times: {symbol} = ₹{current_price:.2f}")
                        
                        return {
                            'source': 'economictimes',
                            'symbol': symbol,
                            'current_price': current_price,
                            'timestamp': datetime.now().isoformat()
                        }
        
        except Exception as e:
            logger.warning(f"Economic Times scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_nseindia_table(self, symbol):
        """
        Scrape NSE India website directly
        Symbol format: RELIANCE (without .BO)
        """
        try:
            logger.info(f"Scraping NSE website for {symbol}...")
            
            url = f"https://www.nseindia.com/cgi-bin/response_master.php?key={symbol}"
            
            response = self.session.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for price in table data
                for td in soup.find_all('td'):
                    text = td.get_text(strip=True)
                    if 'Last Traded Price' in text or 'LTP' in text:
                        next_td = td.find_next('td')
                        if next_td:
                            price_text = next_td.get_text(strip=True)
                            price_match = re.search(r'([\d,\.]+)', price_text)
                            if price_match:
                                current_price = float(price_match.group(1).replace(',', ''))
                                logger.info(f"✓ NSE Website: {symbol} = ₹{current_price:.2f}")
                                
                                return {
                                    'source': 'nsewebsite',
                                    'symbol': symbol,
                                    'current_price': current_price,
                                    'timestamp': datetime.now().isoformat()
                                }
        
        except Exception as e:
            logger.warning(f"NSE website scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_trading_view(self, symbol):
        """
        Scrape chart data from TradingView
        Symbol format: NSE:RELIANCE
        """
        try:
            logger.info(f"Scraping TradingView for {symbol}...")
            
            tv_symbol = f"NSE:{symbol}" if not symbol.startswith('NSE:') else symbol
            
            url = f"https://www.tradingview.com/symbols/{tv_symbol}/"
            
            response = self.session.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for price data in the page
                page_text = soup.get_text()
                
                price_match = re.search(r'Last.*?([\d,\.]+)', page_text)
                if price_match:
                    current_price = float(price_match.group(1).replace(',', ''))
                    logger.info(f"✓ TradingView: {symbol} = ₹{current_price:.2f}")
                    
                    return {
                        'source': 'tradingview',
                        'symbol': symbol,
                        'current_price': current_price,
                        'timestamp': datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.warning(f"TradingView scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_historical_data_investing(self, symbol, days=100):
        """
        Scrape historical data from Investing.com
        Symbol format: RELIANCE (without .BO)
        """
        try:
            logger.info(f"Scraping historical data from Investing.com for {symbol}...")
            
            # Investing.com URL structure
            url = f"https://in.investing.com/equities/{symbol.lower()}-stock-historical-data"
            
            response = self.session.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                historical_data = []
                
                # Find historical price table
                for table in soup.find_all('table'):
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            try:
                                date_str = cols[0].get_text(strip=True)
                                close = float(cols[1].get_text(strip=True).replace(',', ''))
                                open_price = float(cols[2].get_text(strip=True).replace(',', ''))
                                high = float(cols[3].get_text(strip=True).replace(',', ''))
                                low = float(cols[4].get_text(strip=True).replace(',', ''))
                                
                                historical_data.append({
                                    'date': date_str,
                                    'open': open_price,
                                    'high': high,
                                    'low': low,
                                    'close': close
                                })
                            except (ValueError, IndexError):
                                continue
                    
                    if historical_data:
                        logger.info(f"✓ Got {len(historical_data)} days of historical data")
                        return pd.DataFrame(historical_data)
        
        except Exception as e:
            logger.warning(f"Historical data scrape failed: {str(e)[:100]}")
        
        return None
    
    def scrape_all_sources(self, symbol):
        """
        Try all sources and return first successful result
        Symbol format: RELIANCE (without .BO)
        """
        logger.info(f"Attempting to scrape {symbol} from all sources...")
        
        sources = [
            self.scrape_moneycontrol,
            self.scrape_economictimes,
            self.scrape_nseindia_table,
            self.scrape_bseindia,
            self.scrape_trading_view
        ]
        
        for scraper in sources:
            try:
                result = scraper(symbol)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Scraper error: {str(e)[:50]}")
        
        logger.warning(f"All scrapers failed for {symbol}")
        return None
    
    def generate_recommendation(self, symbol, current_price, historical_data=None):
        """
        Generate trading recommendation based on scraped data and analysis
        """
        recommendation = {
            'symbol': symbol,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'analysis': {},
            'recommendation': 'HOLD',
            'confidence': 0,
            'reasoning': []
        }
        
        try:
            # If we have historical data, do technical analysis
            if historical_data is not None and len(historical_data) > 20:
                prices = historical_data['close'].values
                
                # Calculate RSI
                from swing_analyzer import RSI
                rsi = RSI.calculate(pd.Series(prices), period=14)[-1]
                recommendation['analysis']['rsi'] = rsi
                
                # Determine recommendation based on RSI
                if rsi < 30:
                    recommendation['recommendation'] = 'BUY'
                    recommendation['confidence'] = min(100, (30 - rsi) * 3 + 70)
                    recommendation['reasoning'].append(f"RSI {rsi:.2f} indicates oversold condition")
                elif rsi > 70:
                    recommendation['recommendation'] = 'SELL'
                    recommendation['confidence'] = min(100, (rsi - 70) * 3 + 70)
                    recommendation['reasoning'].append(f"RSI {rsi:.2f} indicates overbought condition")
                else:
                    recommendation['recommendation'] = 'HOLD'
                    recommendation['confidence'] = 50
                    recommendation['reasoning'].append(f"RSI {rsi:.2f} is neutral")
                
                # Calculate moving averages
                sma_20 = prices[-20:].mean()
                sma_50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
                
                recommendation['analysis']['sma_20'] = sma_20
                recommendation['analysis']['sma_50'] = sma_50
                
                if current_price > sma_20 > sma_50:
                    recommendation['reasoning'].append("Price above both 20-day and 50-day SMAs (bullish)")
                    recommendation['confidence'] += 10
                elif current_price < sma_20 < sma_50:
                    recommendation['reasoning'].append("Price below both 20-day and 50-day SMAs (bearish)")
                    if recommendation['recommendation'] == 'HOLD':
                        recommendation['recommendation'] = 'SELL'
                
                # Price trend
                trend_change = ((current_price - prices[-10]) / prices[-10]) * 100
                recommendation['analysis']['trend_10day'] = trend_change
                
                if trend_change > 5:
                    recommendation['reasoning'].append(f"10-day uptrend: +{trend_change:.2f}%")
                elif trend_change < -5:
                    recommendation['reasoning'].append(f"10-day downtrend: {trend_change:.2f}%")
            else:
                recommendation['recommendation'] = 'HOLD'
                recommendation['confidence'] = 30
                recommendation['reasoning'].append("Insufficient historical data for detailed analysis")
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return recommendation
    
    def analyze_multiple_stocks(self, symbols, include_historical=True):
        """
        Analyze multiple stocks and generate recommendations
        symbols: List of stock symbols (e.g., ['RELIANCE', 'TCS', 'HDFCBANK'])
        """
        results = []
        
        for symbol in symbols:
            try:
                # Scrape current price
                price_data = self.scrape_all_sources(symbol)
                
                if not price_data:
                    logger.warning(f"Could not fetch price for {symbol}")
                    continue
                
                current_price = price_data['current_price']
                
                # Try to get historical data
                historical_data = None
                if include_historical:
                    historical_data = self.scrape_historical_data_investing(symbol, days=100)
                
                # Generate recommendation
                recommendation = self.generate_recommendation(
                    symbol, 
                    current_price, 
                    historical_data
                )
                
                results.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
        
        return results


# Example usage and testing
if __name__ == "__main__":
    scraper = WebScraper()
    
    # Test scraping multiple stocks
    stocks = ['RELIANCE', 'TCS', 'HDFCBANK']
    
    print("\n" + "="*70)
    print("WEB SCRAPER: Fetching and Analyzing BSE Stocks")
    print("="*70 + "\n")
    
    results = scraper.analyze_multiple_stocks(stocks, include_historical=True)
    
    for result in results:
        print(f"\n{'─'*70}")
        print(f"Stock: {result['symbol']}")
        print(f"Current Price: ₹{result['current_price']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']:.1f}%")
        
        if result['analysis']:
            print(f"\nAnalysis:")
            for key, value in result['analysis'].items():
                print(f"  {key}: {value:.2f}")
        
        if result['reasoning']:
            print(f"\nReasoning:")
            for reason in result['reasoning']:
                print(f"  • {reason}")
