#!/usr/bin/env python3
"""
Comprehensive local test script for BSE swing trading data fetcher
Tests all data sources and provides detailed diagnostics
"""

import os
import sys
import time
import requests
from datetime import datetime
import pandas as pd

print("\n" + "="*70)
print("BSE SWING TRADING DATA FETCHER - LOCAL TEST SUITE")
print("="*70)

# Test 1: Network connectivity
print("\n[TEST 1] Network Connectivity")
print("-" * 70)

test_urls = [
    ("Yahoo Finance", "https://finance.yahoo.com"),
    ("NSE India", "https://www.nseindia.com"),
    ("Google", "https://www.google.com"),
    ("GitHub", "https://github.com"),
]

for name, url in test_urls:
    try:
        response = requests.get(url, timeout=5)
        status = "✓" if response.status_code == 200 else f"✗ ({response.status_code})"
        print(f"  {status} {name}: {response.status_code}")
    except Exception as e:
        print(f"  ✗ {name}: {type(e).__name__}")

# Test 2: yfinance direct test
print("\n[TEST 2] yfinance Direct Download")
print("-" * 70)

try:
    import yfinance as yf
    print("  ✓ yfinance imported")
    
    print("  Attempting to download RELIANCE.BO...")
    start = time.time()
    
    # Try with SSL verification disabled
    import requests
    requests.packages.urllib3.disable_warnings()
    
    data = yf.download(
        'RELIANCE.BO',
        period='1d',
        progress=False,
        timeout=10
    )
    
    elapsed = time.time() - start
    
    if data is not None and len(data) > 0:
        print(f"  ✓ Downloaded in {elapsed:.2f}s")
        print(f"    Last close: ₹{data['Close'].iloc[-1]:.2f}")
        print(f"    Data shape: {data.shape}")
    else:
        print(f"  ✗ Downloaded but got empty data in {elapsed:.2f}s")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")

# Test 3: Web scraping from Yahoo Finance
print("\n[TEST 3] Web Scraping Yahoo Finance")
print("-" * 70)

try:
    from bs4 import BeautifulSoup
    print("  ✓ BeautifulSoup imported")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("  Attempting to scrape RELIANCE.BO data...")
    start = time.time()
    
    url = "https://in.finance.yahoo.com/quote/RELIANCE.BO"
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    
    elapsed = time.time() - start
    
    print(f"  Status: {response.status_code} in {elapsed:.2f}s")
    
    if response.status_code == 200:
        print(f"  ✓ Got HTML ({len(response.content)} bytes)")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find price information
        price_spans = soup.find_all('span')
        print(f"  Found {len(price_spans)} span elements")
        
        # Look for numeric content
        numeric_spans = [s.text for s in price_spans if any(c.isdigit() for c in s.text)][:10]
        if numeric_spans:
            print(f"  Sample text content: {numeric_spans}")
    else:
        print(f"  ✗ Got status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")

# Test 4: Data fetcher module
print("\n[TEST 4] Data Fetcher Module")
print("-" * 70)

try:
    from data_fetcher import BSEDataFetcher
    print("  ✓ data_fetcher imported")
    
    fetcher = BSEDataFetcher()
    print("  ✓ BSEDataFetcher instantiated")
    
    print("  Attempting to fetch TCS.BO historical data...")
    start = time.time()
    
    data = fetcher.fetch_historical_data('TCS.BO', period='3mo')
    
    elapsed = time.time() - start
    
    if data is not None and len(data) > 0:
        print(f"  ✓ Fetched in {elapsed:.2f}s")
        print(f"    Shape: {data.shape}")
        print(f"    Columns: {list(data.columns)}")
        print(f"    Date range: {data.index[0]} to {data.index[-1]}")
    else:
        print(f"  ✗ No data returned in {elapsed:.2f}s")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")
    import traceback
    traceback.print_exc()

# Test 5: Swing Analyzer
print("\n[TEST 5] Swing Trading Analyzer")
print("-" * 70)

try:
    from swing_analyzer import SwingTradingAnalyzer
    print("  ✓ SwingTradingAnalyzer imported")
    
    analyzer = SwingTradingAnalyzer()
    print("  ✓ SwingTradingAnalyzer instantiated")
    
    if data is not None and len(data) > 0:
        print("  Calculating technical indicators...")
        start = time.time()
        
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        
        elapsed = time.time() - start
        print(f"  ✓ Indicators calculated in {elapsed:.2f}s")
        print(f"    New columns: {len(data_with_indicators.columns)}")
        print(f"    Last RSI: {data_with_indicators['RSI'].iloc[-1]:.2f}" if 'RSI' in data_with_indicators else "    (No RSI)")
    else:
        print("  ⊘ Skipping (no data from test 4)")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")

# Test 6: Ranker
print("\n[TEST 6] Ranker Initialization")
print("-" * 70)

try:
    from ranker import SwingTradingRanker
    print("  ✓ SwingTradingRanker imported")
    
    print("  Initializing ranker...")
    start = time.time()
    
    ranker = SwingTradingRanker(num_workers=1)
    
    elapsed = time.time() - start
    print(f"  ✓ Ranker initialized in {elapsed:.2f}s")
    
    print("  Analyzing single stock (WIPRO.BO)...")
    start = time.time()
    
    result = ranker.analyze_single_stock('WIPRO.BO')
    
    elapsed = time.time() - start
    
    if result:
        print(f"  ✓ Analysis complete in {elapsed:.2f}s")
        print(f"    Ticker: {result['ticker']}")
        print(f"    Probability: {result['probability_score']:.1f}%")
        print(f"    Swing Score: {result['swing_score']}")
    else:
        print(f"  ✗ No result after {elapsed:.2f}s")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")
    import traceback
    traceback.print_exc()

# Test 7: Full pipeline (get_top_10_stocks)
print("\n[TEST 7] Full Pipeline - Get Top 10 Stocks")
print("-" * 70)

try:
    if 'ranker' in locals():
        print("  Starting top 10 stocks analysis...")
        start = time.time()
        
        stocks = ranker.get_top_10_stocks(stock_list=['RELIANCE.BO', 'TCS.BO', 'WIPRO.BO'], min_probability=0)
        
        elapsed = time.time() - start
        
        if stocks:
            print(f"  ✓ Got {len(stocks)} stocks in {elapsed:.2f}s")
            for i, stock in enumerate(stocks[:3], 1):
                print(f"    {i}. {stock['ticker']}: {stock['probability_score']:.1f}% prob, {stock['swing_score']} score")
        else:
            print(f"  ✗ No stocks returned in {elapsed:.2f}s")
    else:
        print("  ⊘ Skipping (ranker not available)")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}")
    print(f"     {str(e)[:100]}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST SUITE COMPLETE")
print("="*70 + "\n")
