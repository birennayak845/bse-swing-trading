#!/usr/bin/env python3
"""
Test script for Web Scraper
Demonstrates scraping from multiple sources and generating recommendations
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_scraper import WebScraper
import pandas as pd
from datetime import datetime

def test_web_scraper():
    """Test the web scraper with multiple stocks"""
    
    print("\n" + "="*80)
    print("🕷️  BSE WEB SCRAPER - MULTI-SOURCE ANALYSIS TEST")
    print("="*80 + "\n")
    
    scraper = WebScraper()
    
    # Test stocks
    test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
    
    print(f"📍 Testing {len(test_symbols)} stocks: {', '.join(test_symbols)}\n")
    print("Data sources to be scraped:")
    print("  1. Moneycontrol")
    print("  2. Economic Times")
    print("  3. NSE India Website")
    print("  4. BSE India Official")
    print("  5. TradingView\n")
    
    print("─" * 80 + "\n")
    
    # Test single stock scraping from all sources
    print("STEP 1: Scrape single stock from multiple sources\n")
    
    symbol = 'RELIANCE'
    print(f"Scraping {symbol} from all available sources...\n")
    
    sources_to_try = [
        ('Moneycontrol', scraper.scrape_moneycontrol),
        ('Economic Times', scraper.scrape_economictimes),
        ('NSE Website', scraper.scrape_nseindia_table),
        ('BSE India', scraper.scrape_bseindia),
        ('TradingView', scraper.scrape_trading_view)
    ]
    
    successful_sources = []
    
    for source_name, scraper_func in sources_to_try:
        try:
            print(f"  Trying {source_name}...", end=" ")
            result = scraper_func(symbol)
            if result:
                print(f"✓ SUCCESS - ₹{result['current_price']:.2f}")
                successful_sources.append((source_name, result['current_price']))
            else:
                print("✗ No data found")
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
    
    print(f"\n✓ Successfully scraped from {len(successful_sources)} sources\n")
    
    if successful_sources:
        print("Prices collected:")
        for source, price in successful_sources:
            print(f"  • {source}: ₹{price:.2f}")
        
        avg_price = sum(p for _, p in successful_sources) / len(successful_sources)
        print(f"\n  Average price: ₹{avg_price:.2f}")
    
    print("\n" + "─" * 80 + "\n")
    
    # Test full analysis pipeline
    print("STEP 2: Full analysis with recommendations\n")
    
    results = scraper.analyze_multiple_stocks(test_symbols, include_historical=False)
    
    print(f"✓ Analyzed {len(results)} stocks\n")
    
    for result in results:
        print(f"\n📊 {result['symbol']}")
        print(f"   Current Price: ₹{result['current_price']:.2f}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        
        if result['analysis']:
            print(f"   Technical Indicators:")
            for key, value in result['analysis'].items():
                print(f"     • {key}: {value:.2f}")
        
        if result['reasoning']:
            print(f"   Analysis:")
            for reason in result['reasoning']:
                print(f"     • {reason}")
    
    print("\n" + "="*80)
    print("✅ Web Scraper Test Complete")
    print("="*80 + "\n")

def test_individual_scraper():
    """Test individual scraper function"""
    
    print("\n" + "="*80)
    print("🔍 INDIVIDUAL SCRAPER TEST")
    print("="*80 + "\n")
    
    scraper = WebScraper()
    
    symbol = 'RELIANCE'
    
    print(f"Testing all-sources scraper for {symbol}...\n")
    
    result = scraper.scrape_all_sources(symbol)
    
    if result:
        print(f"✓ Successfully scraped {symbol}")
        print(f"\nData:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print(f"✗ Failed to scrape {symbol}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    # Test both scenarios
    try:
        test_web_scraper()
        test_individual_scraper()
    except KeyboardInterrupt:
        print("\n\n⏹  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
