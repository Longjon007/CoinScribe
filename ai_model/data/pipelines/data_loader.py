"""
Market Data Loader
===================

Loads historical market data from various sources for training the AI model.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataLoader:
    """Loads and manages market data for AI model training."""
    
    def __init__(self, config: Dict):
        """
        Initialize the data loader.
        
        Args:
            config: Configuration dictionary containing data source settings
        """
        self.config = config
        self.symbols = config.get('data_sources', {}).get('market_data', {}).get('symbols', [])
        self.interval = config.get('data_sources', {}).get('market_data', {}).get('interval', '1h')
        self.period = config.get('data_sources', {}).get('market_data', {}).get('period', '1y')
    
    def fetch_market_data(
        self,
        symbol: str,
        period: str = None,
        interval: str = None
    ) -> pd.DataFrame:
        """
        Fetch market data for a single symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD')
            period: Data period (e.g., '1y', '6mo')
            interval: Data interval (e.g., '1h', '1d')
            
        Returns:
            DataFrame with market data
        """
        period = period or self.period
        interval = interval or self.interval
        
        try:
            logger.info(f"Fetching data for {symbol} (period={period}, interval={interval})")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data retrieved for {symbol}")
                return pd.DataFrame()
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Reset index to make datetime a column
            df.reset_index(inplace=True)
            
            logger.info(f"Retrieved {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str] = None,
        period: str = None,
        interval: str = None
    ) -> pd.DataFrame:
        """
        Fetch market data for multiple symbols.
        
        Args:
            symbols: List of trading symbols
            period: Data period
            interval: Data interval
            
        Returns:
            Combined DataFrame with data for all symbols
        """
        symbols = symbols or self.symbols
        dfs = []
        
        for symbol in symbols:
            df = self.fetch_market_data(symbol, period, interval)
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            logger.warning("No data retrieved for any symbol")
            return pd.DataFrame()
        
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Sort by datetime
        combined_df.sort_values('Datetime' if 'Datetime' in combined_df.columns else 'Date', inplace=True)
        
        logger.info(f"Retrieved total of {len(combined_df)} records for {len(symbols)} symbols")
        return combined_df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to market data.
        
        Args:
            df: DataFrame with market data
            
        Returns:
            DataFrame with added technical indicators
        """
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Moving averages
        df['MA_7'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['MA_30'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        
        # Exponential moving averages
        df['EMA_12'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.ewm(span=12, adjust=False).mean()
        )
        df['EMA_26'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.ewm(span=26, adjust=False).mean()
        )
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        
        # RSI (Relative Strength Index)
        df['RSI'] = df.groupby('symbol')['Close'].transform(
            self._calculate_rsi
        )
        
        # Volatility
        df['Volatility'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.rolling(window=30, min_periods=1).std()
        )
        
        # Price change percentage
        df['Price_Change_Pct'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.pct_change()
        )
        
        # Fill NaN values
        df.fillna(method='ffill', inplace=True)
        df.fillna(0, inplace=True)
        
        return df
    
    @staticmethod
    def _calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI indicator.
        
        Args:
            series: Price series
            period: RSI period
            
        Returns:
            RSI values
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def add_sentiment_scores(
        self,
        df: pd.DataFrame,
        sentiment_data: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Add sentiment scores from news data.
        
        Args:
            df: DataFrame with market data
            sentiment_data: Dictionary mapping timestamps to sentiment scores
            
        Returns:
            DataFrame with sentiment scores
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # For now, add placeholder sentiment scores
        # In production, this would integrate with a news sentiment API
        if sentiment_data is None:
            # Generate random sentiment scores as placeholder
            df['sentiment_score'] = np.random.uniform(-1, 1, len(df))
        else:
            # Map sentiment data to dataframe
            # This would be implemented based on actual sentiment API
            df['sentiment_score'] = 0.0
        
        return df
    
    def prepare_training_data(
        self,
        symbols: List[str] = None,
        add_indicators: bool = True
    ) -> pd.DataFrame:
        """
        Prepare complete training dataset.
        
        Args:
            symbols: List of symbols to fetch
            add_indicators: Whether to add technical indicators
            
        Returns:
            Complete training dataset
        """
        # Fetch market data
        df = self.fetch_multiple_symbols(symbols)
        
        if df.empty:
            logger.error("No data available for training")
            return df
        
        # Add technical indicators
        if add_indicators:
            df = self.add_technical_indicators(df)
        
        # Add sentiment scores
        df = self.add_sentiment_scores(df)
        
        return df
