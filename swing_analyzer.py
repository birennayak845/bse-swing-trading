"""
Swing Trading Analysis Engine
Identifies swing trading opportunities using technical indicators
"""

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, MACD
from ta.volatility import BollingerBands
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SwingTradingAnalyzer:
    """Analyzes stocks for swing trading opportunities"""
    
    def __init__(self):
        self.min_rsi_oversold = 30
        self.max_rsi_overbought = 70
        self.support_resistance_periods = 20
    
    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators for the stock
        
        Args:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            pd.DataFrame: DataFrame with indicators
        """
        try:
            df = df.copy()
            
            # RSI
            rsi = RSIIndicator(close=df['Close'], window=14)
            df['RSI'] = rsi.rsi()
            
            # MACD
            macd = MACD(close=df['Close'], window_fast=12, window_slow=26, window_sign=9)
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            df['MACD_diff'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
            df['BB_upper'] = bb.bollinger_hband()
            df['BB_middle'] = bb.bollinger_mavg()
            df['BB_lower'] = bb.bollinger_lband()
            
            # SMA (Simple Moving Average)
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # ATR (Average True Range)
            df['TR'] = np.maximum(
                df['High'] - df['Low'],
                np.maximum(
                    abs(df['High'] - df['Close'].shift()),
                    abs(df['Low'] - df['Close'].shift())
                )
            )
            df['ATR'] = df['TR'].rolling(window=14).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return df
    
    def identify_support_resistance(self, df, lookback=20):
        """
        Identify support and resistance levels
        
        Args:
            df (pd.DataFrame): OHLCV data with Close prices
            lookback (int): Number of periods to look back
        
        Returns:
            tuple: (support_level, resistance_level)
        """
        try:
            recent_data = df.tail(lookback)
            
            # Support: local minimum
            support = recent_data['Low'].min()
            
            # Resistance: local maximum
            resistance = recent_data['High'].max()
            
            return support, resistance
        except Exception as e:
            logger.error(f"Error identifying support/resistance: {str(e)}")
            return None, None
    
    def calculate_swing_score(self, df, ticker):
        """
        Calculate overall swing trading favorability score (0-100)
        
        Args:
            df (pd.DataFrame): DataFrame with indicators
            ticker (str): Stock ticker
        
        Returns:
            dict: Score and reasoning
        """
        try:
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            score = 0
            reasons = []
            
            # RSI Analysis (30 weight)
            if current['RSI'] < self.min_rsi_oversold:
                score += 30
                reasons.append(f"RSI oversold ({current['RSI']:.2f})")
            elif self.min_rsi_oversold <= current['RSI'] <= 40:
                score += 20
                reasons.append(f"RSI approaching oversold ({current['RSI']:.2f})")
            elif 60 <= current['RSI'] <= self.max_rsi_overbought:
                score += 10
                reasons.append(f"RSI in neutral zone ({current['RSI']:.2f})")
            
            # MACD Analysis (25 weight)
            if current['MACD'] > current['MACD_signal'] and previous['MACD'] <= previous['MACD_signal']:
                score += 25
                reasons.append("MACD bullish crossover")
            elif current['MACD'] > current['MACD_signal']:
                score += 15
                reasons.append("MACD above signal line")
            elif current['MACD_diff'] > 0:
                score += 10
                reasons.append("MACD histogram positive")
            
            # Bollinger Bands Analysis (20 weight)
            if current['Close'] < current['BB_lower']:
                score += 20
                reasons.append("Price below lower BB")
            elif current['Close'] < current['BB_middle']:
                score += 10
                reasons.append("Price approaching lower BB")
            
            # Volatility Analysis (15 weight)
            if pd.notna(current['ATR']):
                atr_pct = (current['ATR'] / current['Close']) * 100
                if 1 < atr_pct < 5:  # Optimal volatility range
                    score += 15
                    reasons.append(f"Optimal volatility ({atr_pct:.2f}%)")
                elif atr_pct > 0.5:
                    score += 8
                    reasons.append(f"Good volatility ({atr_pct:.2f}%)")
            
            # Trend Analysis (10 weight)
            if current['Close'] > current['SMA_20'] > current['SMA_50']:
                score += 5
                reasons.append("Bullish trend")
            
            return {
                'score': min(score, 100),
                'reasons': reasons,
                'rsi': current['RSI'],
                'macd': current['MACD'],
                'close': current['Close']
            }
        except Exception as e:
            logger.error(f"Error calculating swing score: {str(e)}")
            return {'score': 0, 'reasons': [str(e)], 'rsi': None, 'macd': None, 'close': None}
    
    def calculate_trade_levels(self, df, atr_multiplier=1.5):
        """
        Calculate entry price, stop loss, and target price
        
        Args:
            df (pd.DataFrame): DataFrame with indicators
            atr_multiplier (float): Multiplier for ATR-based stop loss
        
        Returns:
            dict: Trade levels (entry, stop_loss, target)
        """
        try:
            current = df.iloc[-1]
            
            # Entry price = current close
            entry_price = current['Close']
            
            # Stop loss based on support level or ATR
            support, resistance = self.identify_support_resistance(df)
            
            # Use ATR for stop loss calculation
            if pd.notna(current['ATR']):
                atr_stop = current['ATR'] * atr_multiplier
                stop_loss = entry_price - atr_stop
            else:
                stop_loss = support if support else entry_price * 0.95
            
            # Target price based on resistance or 2xATR profit
            if pd.notna(current['ATR']):
                profit_target = entry_price + (current['ATR'] * 2.5)
            else:
                profit_target = entry_price * 1.05
            
            # Risk-reward ratio
            risk = entry_price - stop_loss
            reward = profit_target - entry_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            return {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target_price': profit_target,
                'risk': risk,
                'reward': reward,
                'rr_ratio': rr_ratio,
                'support': support,
                'resistance': resistance
            }
        except Exception as e:
            logger.error(f"Error calculating trade levels: {str(e)}")
            return None
    
    def get_entry_time(self, df):
        """
        Determine optimal entry time based on recent price action
        
        Returns:
            str: Time recommendation
        """
        try:
            current = df.iloc[-1]
            recent_low = df['Low'].tail(5).min()
            
            if current['Close'] <= recent_low * 1.02:  # Within 2% of recent low
                return "Immediate (at support)"
            else:
                return "On dip to support level"
        except Exception as e:
            logger.error(f"Error getting entry time: {str(e)}")
            return "Analyze further"


if __name__ == "__main__":
    from data_fetcher import BSEDataFetcher
    
    fetcher = BSEDataFetcher()
    analyzer = SwingTradingAnalyzer()
    
    # Test
    data = fetcher.fetch_historical_data("RELIANCE.BO", period="3mo")
    if data is not None:
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        score = analyzer.calculate_swing_score(data_with_indicators, "RELIANCE.BO")
        levels = analyzer.calculate_trade_levels(data_with_indicators)
        print(f"Swing Score: {score['score']}")
        print(f"Trade Levels: {levels}")
