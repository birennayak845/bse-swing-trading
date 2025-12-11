#!/usr/bin/env python
"""
Quick test script to verify the swing trading analysis system
Run this to test if everything is working correctly
"""

import sys
import time
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        from data_fetcher import BSEDataFetcher, BSE_TOP_STOCKS
        print("✓ data_fetcher imported")
        
        from swing_analyzer import SwingTradingAnalyzer
        print("✓ swing_analyzer imported")
        
        from probability_scorer import ProbabilityScorer
        print("✓ probability_scorer imported")
        
        from ranker import SwingTradingRanker
        print("✓ ranker imported")
        
        print("\n✓ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_data_fetching():
    """Test data fetching from BSE"""
    print("Testing data fetching...")
    try:
        from data_fetcher import BSEDataFetcher
        
        fetcher = BSEDataFetcher()
        print("  - Fetching RELIANCE.BO data...")
        data = fetcher.fetch_historical_data("RELIANCE.BO", period="1mo")
        
        if data is not None and len(data) > 0:
            print(f"  ✓ Fetched {len(data)} data points")
            print(f"  - Latest close price: ₹{data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("  ✗ No data returned")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_analysis():
    """Test swing trading analysis"""
    print("\nTesting swing trading analysis...")
    try:
        from data_fetcher import BSEDataFetcher
        from swing_analyzer import SwingTradingAnalyzer
        
        fetcher = BSEDataFetcher()
        analyzer = SwingTradingAnalyzer()
        
        print("  - Fetching data...")
        data = fetcher.fetch_historical_data("RELIANCE.BO", period="3mo")
        
        if data is None:
            print("  ✗ Could not fetch data")
            return False
        
        print("  - Calculating indicators...")
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        
        print("  - Calculating swing score...")
        swing_score = analyzer.calculate_swing_score(data_with_indicators, "RELIANCE.BO")
        print(f"  ✓ Swing score: {swing_score['score']:.1f}/100")
        
        print("  - Calculating trade levels...")
        trade_levels = analyzer.calculate_trade_levels(data_with_indicators)
        if trade_levels:
            print(f"  ✓ Entry: ₹{trade_levels['entry_price']:.2f}")
            print(f"  ✓ SL: ₹{trade_levels['stop_loss']:.2f}")
            print(f"  ✓ Target: ₹{trade_levels['target_price']:.2f}")
            print(f"  ✓ R/R: {trade_levels['rr_ratio']:.2f}:1")
            return True
        else:
            print("  ✗ Could not calculate trade levels")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_probability_scoring():
    """Test probability scoring"""
    print("\nTesting probability scoring...")
    try:
        from data_fetcher import BSEDataFetcher
        from swing_analyzer import SwingTradingAnalyzer
        from probability_scorer import ProbabilityScorer
        
        fetcher = BSEDataFetcher()
        analyzer = SwingTradingAnalyzer()
        scorer = ProbabilityScorer()
        
        print("  - Fetching data...")
        data = fetcher.fetch_historical_data("RELIANCE.BO", period="3mo")
        
        if data is None:
            print("  ✗ Could not fetch data")
            return False
        
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        swing_score = analyzer.calculate_swing_score(data_with_indicators, "RELIANCE.BO")
        trade_levels = analyzer.calculate_trade_levels(data_with_indicators)
        
        if trade_levels is None:
            print("  ✗ Could not get trade levels")
            return False
        
        print("  - Calculating probability...")
        probability = scorer.calculate_overall_probability(
            data_with_indicators,
            trade_levels['entry_price'],
            trade_levels['target_price'],
            trade_levels['stop_loss'],
            swing_score['score'],
            trade_levels['rr_ratio']
        )
        print(f"  ✓ Probability: {probability:.1f}%")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ranking():
    """Test top 10 stock ranking (limited test with 3 stocks)"""
    print("\nTesting stock ranking (analyzing 3 stocks)...")
    try:
        from ranker import SwingTradingRanker
        
        ranker = SwingTradingRanker(num_workers=3)
        print("  - Analyzing stocks...")
        
        # Analyze just a few stocks for testing
        top_stocks = ranker.get_top_10_stocks(
            stock_list=["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO"],
            min_probability=30
        )
        
        if len(top_stocks) > 0:
            print(f"  ✓ Found {len(top_stocks)} promising stocks")
            for i, stock in enumerate(top_stocks, 1):
                print(f"    {i}. {stock['ticker']}: {stock['probability_score']:.1f}% win probability")
            return True
        else:
            print("  ✗ No stocks found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("BSE Swing Trading Analysis - System Test")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    tests = [
        ("Imports", test_imports),
        ("Data Fetching", test_data_fetching),
        ("Technical Analysis", test_analysis),
        ("Probability Scoring", test_probability_scoring),
        ("Stock Ranking", test_ranking),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[test_name] = False
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print(f"Time: {elapsed_time:.2f} seconds")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
