"""
Probability Scoring System
Calculates probability of hitting target price
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProbabilityScorer:
    """Calculates probability scores for swing trading targets"""
    
    def __init__(self):
        self.lookback_period = 20  # Days to look back for pattern analysis
    
    def calculate_pattern_probability(self, df, target_price, stop_loss):
        """
        Calculate probability based on historical pattern matching
        
        Args:
            df (pd.DataFrame): Historical data with indicators
            target_price (float): Target price to hit
            stop_loss (float): Stop loss level
        
        Returns:
            float: Probability (0-100)
        """
        try:
            if len(df) < self.lookback_period:
                return 50  # Default probability if not enough data
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate price movement needed
            price_move_needed = ((target_price - current_price) / current_price) * 100
            
            # Get recent volatility
            recent_returns = df['Close'].pct_change().tail(self.lookback_period)
            volatility = recent_returns.std() * 100
            
            # Calculate similar patterns
            similar_patterns = self._find_similar_patterns(df, current_price)
            win_rate = similar_patterns['win_rate']
            
            # Composite probability
            probability = (win_rate * 0.4) + (self._z_score_probability(price_move_needed, volatility) * 0.4) + \
                         (self._mean_reversion_probability(df) * 0.2)
            
            return max(0, min(100, probability))
        except Exception as e:
            logger.error(f"Error calculating pattern probability: {str(e)}")
            return 50
    
    def _z_score_probability(self, price_move, volatility):
        """
        Calculate probability using Z-score (normal distribution)
        
        Args:
            price_move (float): Price move in percentage
            volatility (float): Volatility in percentage
        
        Returns:
            float: Probability (0-100)
        """
        try:
            if volatility == 0:
                return 50
            
            z_score = abs(price_move) / volatility
            
            # Using normal distribution approximation
            # Z-score of 1 ≈ 68% probability (one standard deviation)
            # Z-score of 2 ≈ 95% probability (two standard deviations)
            
            if z_score <= 1:
                probability = 50 + (z_score * 18)  # 50-68%
            elif z_score <= 2:
                probability = 68 + ((z_score - 1) * 27)  # 68-95%
            else:
                probability = 95 + min(5, (z_score - 2) * 2)  # 95-100%
            
            return probability
        except Exception as e:
            logger.error(f"Error in Z-score calculation: {str(e)}")
            return 50
    
    def _mean_reversion_probability(self, df):
        """
        Calculate probability based on mean reversion theory
        
        Returns:
            float: Probability (0-100)
        """
        try:
            current_price = df['Close'].iloc[-1]
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            bb_upper = df['BB_upper'].iloc[-1]
            bb_lower = df['BB_lower'].iloc[-1]
            
            probability = 50  # Base probability
            
            # If price is below SMA, mean reversion might pull it up
            if current_price < sma_20 and current_price < sma_50:
                probability += 20
            
            # If price is below lower Bollinger Band, strong mean reversion
            if current_price < bb_lower:
                probability += 25
            
            return min(100, probability)
        except Exception as e:
            logger.error(f"Error in mean reversion probability: {str(e)}")
            return 50
    
    def _find_similar_patterns(self, df, current_price):
        """
        Find similar price patterns in history and calculate win rate
        
        Returns:
            dict: Pattern analysis with win_rate
        """
        try:
            # Look for similar RSI levels and MACD patterns
            current_rsi = df['RSI'].iloc[-1]
            
            # Find periods where RSI was similar (within 10 points)
            similar_periods = df[
                (df['RSI'] >= current_rsi - 10) & 
                (df['RSI'] <= current_rsi + 10)
            ].index
            
            if len(similar_periods) < 3:
                return {'win_rate': 50, 'samples': len(similar_periods)}
            
            # Calculate what happened after similar patterns
            wins = 0
            total = 0
            
            # Convert index to integer positions
            for i, idx in enumerate(similar_periods[:-1]):  # Exclude current
                current_pos = df.index.get_loc(idx)
                next_pos = current_pos + 1
                
                if next_pos < len(df) - 1:
                    # Look at next 5-20 days for max price
                    end_pos = min(next_pos + 20, len(df))
                    future_price = df['Close'].iloc[next_pos:end_pos].max()
                    entry_price = df['Close'].iloc[current_pos]
                    
                    if future_price > entry_price * 1.02:  # 2% gain
                        wins += 1
                    total += 1
            
            win_rate = (wins / total * 100) if total > 0 else 50
            return {'win_rate': win_rate, 'samples': total}
        except Exception as e:
            logger.error(f"Error finding similar patterns: {str(e)}")
            return {'win_rate': 50, 'samples': 0}
    
    def calculate_rr_probability(self, risk_reward_ratio):
        """
        Calculate probability based on risk-reward ratio
        Higher RR ratio = higher probability expectation
        
        Args:
            risk_reward_ratio (float): Reward/Risk ratio
        
        Returns:
            float: Probability adjustment
        """
        try:
            # If RR ratio > 2, we expect lower probability but better odds
            # If RR ratio < 1, we expect higher probability but poor odds
            
            if risk_reward_ratio >= 3:
                return 0.6  # 60% probability expected for 3:1 RR
            elif risk_reward_ratio >= 2:
                return 0.65  # 65% for 2:1 RR
            elif risk_reward_ratio >= 1.5:
                return 0.70  # 70% for 1.5:1 RR
            elif risk_reward_ratio >= 1:
                return 0.75  # 75% for 1:1 RR
            else:
                return 0.50  # 50% for poor RR
        except Exception as e:
            logger.error(f"Error calculating RR probability: {str(e)}")
            return 0.5
    
    def calculate_overall_probability(self, df, entry_price, target_price, stop_loss, 
                                     swing_score, rr_ratio):
        """
        Calculate overall probability of hitting target
        
        Args:
            df (pd.DataFrame): Historical data
            entry_price (float): Entry price
            target_price (float): Target price
            stop_loss (float): Stop loss
            swing_score (float): Swing trading favorability score (0-100)
            rr_ratio (float): Risk-reward ratio
        
        Returns:
            float: Overall probability (0-100)
        """
        try:
            # Pattern-based probability
            pattern_prob = self.calculate_pattern_probability(df, target_price, stop_loss)
            
            # Swing score probability (convert score to probability)
            swing_prob = swing_score * 0.8  # Max 80% from swing score
            
            # RR ratio probability
            rr_prob = self.calculate_rr_probability(rr_ratio) * 100
            
            # Composite score with weights
            overall_prob = (pattern_prob * 0.35) + (swing_prob * 0.35) + (rr_prob * 0.30)
            
            return max(0, min(100, overall_prob))
        except Exception as e:
            logger.error(f"Error calculating overall probability: {str(e)}")
            return 50


if __name__ == "__main__":
    from data_fetcher import BSEDataFetcher
    from swing_analyzer import SwingTradingAnalyzer
    
    fetcher = BSEDataFetcher()
    analyzer = SwingTradingAnalyzer()
    scorer = ProbabilityScorer()
    
    # Test
    data = fetcher.fetch_historical_data("RELIANCE.BO", period="3mo")
    if data is not None:
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        levels = analyzer.calculate_trade_levels(data_with_indicators)
        score = analyzer.calculate_swing_score(data_with_indicators, "RELIANCE.BO")
        
        if levels:
            prob = scorer.calculate_overall_probability(
                data_with_indicators,
                levels['entry_price'],
                levels['target_price'],
                levels['stop_loss'],
                score['score'],
                levels['rr_ratio']
            )
            print(f"Overall Probability: {prob:.2f}%")
