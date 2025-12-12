#!/usr/bin/env python3
"""
Test alternative BSE data sources
"""

import requests
import json
import pandas as pd
import time

print("\n" + "="*70)
print("TESTING ALTERNATIVE BSE DATA SOURCES")
print("="*70)

# Test 1: NSE API
print("\n[TEST 1] NSE India JSON API")
print("-" * 70)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    # Try NSE API
    url = "https://www.nseindia.com/api/quote-equity?symbol=RELIANCE"
    print(f"  Trying: {url}")
    
    response = requests.get(url, headers=headers, timeout=10)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Got JSON data!")
        print(f"    Keys: {list(data.keys())[:5]}")
    else:
        print(f"  ✗ Status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")

# Test 2: Moneycontrol API
print("\n[TEST 2] Moneycontrol API")
print("-" * 70)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    url = "https://www.moneycontrol.com/mccode/common/pricecharts/index.php?symbol=BSE_RELIANCE&range=1M&type=0"
    print(f"  Trying Moneycontrol...")
    
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"  ✓ Got data ({len(response.text)} bytes)")
        # Check if it contains JSON
        if response.text.startswith('[') or response.text.startswith('{'):
            try:
                data = response.json()
                print(f"    JSON detected!")
            except:
                print(f"    HTML response")
    else:
        print(f"  ✗ Status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")

# Test 3: Alpha Vantage (if available)
print("\n[TEST 3] Alpha Vantage API")
print("-" * 70)

try:
    # Alpha Vantage requires API key
    print("  Requires API key - skipped")
except Exception as e:
    print(f"  Error: {e}")

# Test 4: BSE Direct Website
print("\n[TEST 4] BSE Official Website Scraping")
print("-" * 70)

try:
    from bs4 import BeautifulSoup
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    url = "https://www.bseindia.com/stock/RELIANCE"
    print(f"  Trying: {url}")
    
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for price information
        price_elements = soup.find_all(['span', 'div'], {'class': ['price', 'LTP', 'ltp']})
        print(f"  Found {len(price_elements)} price elements")
        
        # Try to find any numeric data
        all_text = soup.get_text()
        if 'RELIANCE' in all_text:
            print(f"  ✓ Found stock name in HTML")
            # Find lines with numbers
            lines = all_text.split('\n')
            price_lines = [l for l in lines if any(c.isdigit() for c in l) and len(l) < 100]
            if price_lines:
                print(f"  Sample data lines:")
                for line in price_lines[:3]:
                    if line.strip():
                        print(f"    {line.strip()[:80]}")
    else:
        print(f"  ✗ Status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")

# Test 5: TradingView embed data
print("\n[TEST 5] TradingView Data")
print("-" * 70)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    url = "https://www.tradingview.com/symbols/NSE-RELIANCE/"
    print(f"  Trying TradingView...")
    
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        # Look for JSON embedded in HTML
        if 'json' in response.text.lower():
            print(f"  ✓ Found JSON in response")
        else:
            print(f"  Response contains HTML")
    else:
        print(f"  ✗ Status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")

# Test 6: Groww API (reverse engineered)
print("\n[TEST 6] Groww.in API")
print("-" * 70)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    # Groww uses internal API
    url = "https://api.groww.in/v1/stock/quote/?q=RELIANCE&exchange=NSE"
    print(f"  Trying Groww API...")
    
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Got JSON!")
        print(f"    Keys: {list(data.keys())}")
        if 'data' in data:
            print(f"    Data keys: {list(data['data'].keys())[:10]}")
    else:
        print(f"  ✗ Status {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
