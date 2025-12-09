import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from ai_model.data.pipelines.data_loader import MarketDataLoader

class TestMarketDataLoader:
    @pytest.fixture
    def data_loader(self, mock_config_dict):
        return MarketDataLoader(mock_config_dict)

    def test_init(self, data_loader, mock_config_dict):
        assert data_loader.symbols == mock_config_dict['data_sources']['market_data']['symbols']
        assert data_loader.interval == mock_config_dict['data_sources']['market_data']['interval']
        assert data_loader.period == mock_config_dict['data_sources']['market_data']['period']

    @patch('ai_model.data.pipelines.data_loader.yf.Ticker')
    def test_fetch_market_data(self, mock_ticker, data_loader, sample_market_data):
        mock_instance = MagicMock()
        mock_instance.history.return_value = sample_market_data.drop(columns=['symbol', 'Datetime']).set_index(pd.to_datetime(sample_market_data['Datetime']))
        mock_ticker.return_value = mock_instance

        df = data_loader.fetch_market_data('BTC-USD')

        assert not df.empty
        assert 'symbol' in df.columns
        assert df.iloc[0]['symbol'] == 'BTC-USD'
        mock_ticker.assert_called_with('BTC-USD')

    @patch('ai_model.data.pipelines.data_loader.yf.Ticker')
    def test_fetch_market_data_empty(self, mock_ticker, data_loader):
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance

        df = data_loader.fetch_market_data('BTC-USD')
        assert df.empty

    @patch('ai_model.data.pipelines.data_loader.MarketDataLoader.fetch_market_data')
    def test_fetch_multiple_symbols(self, mock_fetch, data_loader, sample_market_data):
        mock_fetch.return_value = sample_market_data

        df = data_loader.fetch_multiple_symbols(['BTC-USD', 'ETH-USD'])

        assert len(df) == 2 * len(sample_market_data)
        assert mock_fetch.call_count == 2

    def test_add_technical_indicators(self, data_loader, sample_market_data):
        # Ensure we have enough data for rolling windows
        df = data_loader.add_technical_indicators(sample_market_data)

        expected_columns = ['MA_7', 'MA_30', 'EMA_12', 'EMA_26', 'MACD', 'RSI', 'Volatility', 'Price_Change_Pct']
        for col in expected_columns:
            assert col in df.columns

    def test_add_sentiment_scores(self, data_loader, sample_market_data):
        df = data_loader.add_sentiment_scores(sample_market_data)
        assert 'sentiment_score' in df.columns

    @patch('ai_model.data.pipelines.data_loader.MarketDataLoader.fetch_multiple_symbols')
    def test_prepare_training_data(self, mock_fetch, data_loader, sample_market_data):
        mock_fetch.return_value = sample_market_data

        df = data_loader.prepare_training_data(['BTC-USD'])

        assert not df.empty
        assert 'sentiment_score' in df.columns
        assert 'MACD' in df.columns
