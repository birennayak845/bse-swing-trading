#!/usr/bin/env python3
"""
Test script to diagnose data fetching issues
Mimics what happens in Vercel serverless environment
"""

import sys
import os
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("DATA FETCHER DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Check imports
print("\n[TEST 1] Checking imports...")
try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except ImportError as e:
    print(f"✗ yfinance import failed: {e}")
    print("  Installing yfinance...")
    os.system("pip install yfinance==0.2.32 -q")
    import yfinance as yf
    print("✓ yfinance installed and imported")

try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    from data_fetcher import BSEDataFetcher
    print("✓ data_fetcher module imported successfully")
except ImportError as e:
    print(f"✗ data_fetcher import failed: {e}")
    sys.exit(1)

# Test 2: Simple yfinance call
print("\n[TEST 2] Testing yfinance.download() with timeout...")
try:
    logger.info("Starting yfinance download for RELIANCE.BO...")
    start_time = time.time()
    
    data = yf.download(
        'RELIANCE.BO',
        period='3mo',
        progress=False,
        timeout=10
    )
    
    elapsed = time.time() - start_time
    
    if data is not None and len(data) > 0:
        print(f"✓ yfinance download successful in {elapsed:.2f}s")
        print(f"  Data shape: {data.shape}")
        print(f"  Latest close: {data['Close'].iloc[-1]:.2f}")
    else:
        print(f"✗ yfinance returned empty data in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"✗ yfinance download failed after {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    logger.exception("Full traceback:")

# Test 3: BSEDataFetcher
print("\n[TEST 3] Testing BSEDataFetcher class...")
try:
    logger.info("Creating BSEDataFetcher instance...")
    start_time = time.time()
    
    fetcher = BSEDataFetcher()
    
    elapsed = time.time() - start_time
    print(f"✓ BSEDataFetcher instantiated in {elapsed:.2f}s")
    
    logger.info("Fetching historical data for TCS.BO...")
    start_time = time.time()
    
    data = fetcher.fetch_historical_data('TCS.BO', period='3mo')
    
    elapsed = time.time() - start_time
    
    if data is not None and len(data) > 0:
        print(f"✓ Fetched TCS.BO data in {elapsed:.2f}s")
        print(f"  Data shape: {data.shape}")
        print(f"  Latest close: {data['Close'].iloc[-1]:.2f}")
    else:
        print(f"✗ No data returned for TCS.BO after {elapsed:.2f}s")
        
except Exception as e:
    elapsed = time.time() - start_time
    print(f"✗ BSEDataFetcher test failed after {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    logger.exception("Full traceback:")

# Test 4: Ranker initialization
print("\n[TEST 4] Testing Ranker initialization...")
try:
    logger.info("Importing SwingTradingRanker...")
    from ranker import SwingTradingRanker
    
    logger.info("Creating SwingTradingRanker instance...")
    start_time = time.time()
    
    ranker = SwingTradingRanker(num_workers=3)
    
    elapsed = time.time() - start_time
    print(f"✓ SwingTradingRanker instantiated in {elapsed:.2f}s")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"✗ SwingTradingRanker test failed after {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    logger.exception("Full traceback:")

# Test 5: Get top stocks
print("\n[TEST 5] Testing get_top_10_stocks()...")
try:
    if 'ranker' in locals():
        logger.info("Getting top 10 stocks...")
        start_time = time.time()
        
        top_stocks = ranker.get_top_10_stocks(min_probability=70)
        
        elapsed = time.time() - start_time
        
        if top_stocks:
            print(f"✓ Retrieved {len(top_stocks)} stocks in {elapsed:.2f}s")
            for stock in top_stocks[:3]:
                print(f"  - {stock.get('ticker', 'N/A')}: {stock.get('probability_score', 'N/A')}")
        else:
            print(f"✗ No stocks returned after {elapsed:.2f}s")
    else:
        print("⊘ Skipping (ranker not available)")
        
except Exception as e:
    elapsed = time.time() - start_time
    print(f"✗ get_top_10_stocks() failed after {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    logger.exception("Full traceback:")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
