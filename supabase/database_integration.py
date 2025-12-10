"""
Example integration of CoinScribe with Supabase database.

This script demonstrates how to connect the AI model with the Supabase database
to store and retrieve coin data, price history, and news sentiment.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

# Note: Install supabase package: pip install supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("Warning: supabase package not installed. Run: pip install supabase")
    SUPABASE_AVAILABLE = False


class CoinScribeDB:
    """Database interface for CoinScribe application."""
    
    def __init__(self, url: str = None, key: str = None):
        """
        Initialize database connection.
        
        Args:
            url: Supabase project URL (default: from SUPABASE_URL env var)
            key: Supabase API key (default: from SUPABASE_KEY env var)
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase package is required. Install with: pip install supabase")
        
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY must be provided or set in environment")
        
        self.client: Client = create_client(self.url, self.key)
    
    def get_coin(self, symbol: str) -> Optional[Dict]:
        """
        Get coin information by symbol.
        
        Args:
            symbol: Coin symbol (e.g., 'BTC-USD')
            
        Returns:
            Coin data dictionary or None if not found
        """
        response = self.client.table('coins').select('*').eq('symbol', symbol).execute()
        return response.data[0] if response.data else None
    
    def get_all_coins(self, active_only: bool = True) -> List[Dict]:
        """
        Get all coins from database.
        
        Args:
            active_only: If True, only return active coins
            
        Returns:
            List of coin dictionaries
        """
        query = self.client.table('coins').select('*')
        if active_only:
            query = query.eq('is_active', True)
        
        response = query.execute()
        return response.data
    
    def update_coin_price(self, symbol: str, price_data: Dict) -> Dict:
        """
        Update current price data for a coin.
        
        Args:
            symbol: Coin symbol
            price_data: Dictionary with price fields (current_price, market_cap, volume_24h, etc.)
            
        Returns:
            Updated coin data
        """
        # Add last_updated timestamp
        price_data['last_updated'] = datetime.utcnow().isoformat()
        
        response = self.client.table('coins').update(price_data).eq('symbol', symbol).execute()
        return response.data[0] if response.data else None
    
    def add_price_history(self, coin_symbol: str, ohlcv_data: Dict) -> Dict:
        """
        Add historical price data point.
        
        Args:
            coin_symbol: Coin symbol
            ohlcv_data: Dictionary with OHLCV data (open, high, low, close, volume, timestamp)
            
        Returns:
            Created price history record
        """
        # Get coin_id from symbol
        coin = self.get_coin(coin_symbol)
        if not coin:
            raise ValueError(f"Coin {coin_symbol} not found")
        
        ohlcv_data['coin_id'] = coin['id']
        
        response = self.client.table('coin_price_history').insert(ohlcv_data).execute()
        return response.data[0] if response.data else None
    
    def get_price_history(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get historical price data for a coin.
        
        Args:
            symbol: Coin symbol
            start_date: Start date for history (optional)
            end_date: End date for history (optional)
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with historical price data
        """
        coin = self.get_coin(symbol)
        if not coin:
            raise ValueError(f"Coin {symbol} not found")
        
        query = self.client.table('coin_price_history')\
            .select('*')\
            .eq('coin_id', coin['id'])\
            .order('timestamp', desc=True)\
            .limit(limit)
        
        if start_date:
            query = query.gte('timestamp', start_date.isoformat())
        if end_date:
            query = query.lte('timestamp', end_date.isoformat())
        
        response = query.execute()
        return pd.DataFrame(response.data)
    
    def add_news_article(self, coin_symbol: str, news_data: Dict) -> Dict:
        """
        Add news article with sentiment analysis.
        
        Args:
            coin_symbol: Coin symbol
            news_data: Dictionary with news fields (title, content, url, sentiment_score, etc.)
            
        Returns:
            Created news record
        """
        coin = self.get_coin(coin_symbol)
        if not coin:
            raise ValueError(f"Coin {coin_symbol} not found")
        
        news_data['coin_id'] = coin['id']
        
        response = self.client.table('coin_news').insert(news_data).execute()
        return response.data[0] if response.data else None
    
    def get_recent_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get recent news for a coin.
        
        Args:
            symbol: Coin symbol
            limit: Number of articles to return
            
        Returns:
            List of news article dictionaries
        """
        coin = self.get_coin(symbol)
        if not coin:
            raise ValueError(f"Coin {symbol} not found")
        
        response = self.client.table('coin_news')\
            .select('*')\
            .eq('coin_id', coin['id'])\
            .order('published_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
    
    def update_ai_prediction(self, symbol: str, index_value: float) -> Dict:
        """
        Update AI prediction index for a coin.
        
        Args:
            symbol: Coin symbol
            index_value: AI-generated index value
            
        Returns:
            Updated coin data
        """
        update_data = {
            'ai_index_value': index_value,
            'last_ai_prediction': datetime.utcnow().isoformat()
        }
        
        response = self.client.table('coins').update(update_data).eq('symbol', symbol).execute()
        return response.data[0] if response.data else None


# Example usage
if __name__ == "__main__":
    print("CoinScribe Database Integration Example")
    print("=" * 50)
    print()
    print("This is an example of how to integrate the database.")
    print("To use this, set environment variables:")
    print("  SUPABASE_URL=your_project_url")
    print("  SUPABASE_KEY=your_api_key")
    print()
    print("Example operations:")
    print()
    print("  # Initialize database connection")
    print("  db = CoinScribeDB()")
    print()
    print("  # Get all active coins")
    print("  coins = db.get_all_coins()")
    print()
    print("  # Get specific coin")
    print("  btc = db.get_coin('BTC-USD')")
    print()
    print("  # Update price data")
    print("  db.update_coin_price('BTC-USD', {")
    print("      'current_price': 45000.50,")
    print("      'market_cap': 850000000000,")
    print("      'volume_24h': 35000000000")
    print("  })")
    print()
    print("  # Add historical data")
    print("  db.add_price_history('BTC-USD', {")
    print("      'timestamp': datetime.utcnow(),")
    print("      'open': 44500,")
    print("      'high': 45200,")
    print("      'low': 44300,")
    print("      'close': 45000,")
    print("      'volume': 2500000000")
    print("  })")
    print()
    print("  # Update AI prediction")
    print("  db.update_ai_prediction('BTC-USD', 7.5)")
    print()
