"""
Functional Testing Suite for CoinScribe Application
===================================================

Tests user-facing features and workflows including:
- Data entry, processing, and output
- End-to-end user flows
- Complete prediction workflow
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.api.endpoints import create_app


class TestFunctionalWorkflows:
    """Test complete user workflows."""
    
    @pytest.fixture
    def app(self, mock_config):
        """Create test Flask app."""
        app = create_app(mock_config)
        app.config.update({"TESTING": True})
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_complete_prediction_workflow(self, client, app, sample_market_data):
        """Test complete workflow: data fetch -> process -> predict."""
        # Mock components
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Step 1: Fetch market data
        app.data_loader.fetch_multiple_symbols.return_value = sample_market_data
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD'],
            'period': '1d',
            'interval': '1h'
        })
        
        assert response.status_code == 200
        assert response.json['count'] > 0
        assert 'data' in response.json
        
        # Step 2: Get model info
        app.predictor.get_model_info.return_value = {
            'model_path': 'test_model.pth',
            'architecture': 'lstm',
            'input_features': 10
        }
        
        response = client.get('/api/model/info')
        assert response.status_code == 200
        assert 'model_path' in response.json
        
        # Step 3: Make prediction
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.75, 0.82, 0.68, 0.91, 0.55, 0.77, 0.88, 0.62, 0.73, 0.85],
            'index_names': [f'Index_{i+1}' for i in range(10)],
            'confidence': 0.85,
            'symbols': ['BTC-USD'],
            'timestamp': '2024-01-01 12:00:00'
        }
        
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        
        assert response.status_code == 200
        assert 'indices' in response.json
        assert len(response.json['indices']) == 10
        assert response.json['confidence'] == 0.85
        assert 'timestamp' in response.json
    
    def test_data_entry_validation(self, client, app):
        """Test data entry with various input validations."""
        app.data_loader = MagicMock()
        
        # Valid input
        app.data_loader.fetch_multiple_symbols.return_value = pd.DataFrame({
            'Close': [100, 101, 102]
        })
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD']
        })
        assert response.status_code == 200
        
        # Empty symbols (should use default)
        response = client.post('/api/data/fetch', json={})
        assert response.status_code == 200
    
    def test_error_handling_workflow(self, client, app):
        """Test error handling in user workflows."""
        # Test with no predictor
        app.predictor = None
        app.data_loader = None
        
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        assert response.status_code == 500
        assert 'error' in response.json
        
        # Test data fetch with no loader
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD']
        })
        assert response.status_code == 500
        assert 'error' in response.json
    
    def test_list_indices_workflow(self, client):
        """Test listing available indices."""
        response = client.get('/api/indices/list')
        
        assert response.status_code == 200
        assert 'indices' in response.json
        assert response.json['count'] == 10
        assert all('name' in idx for idx in response.json['indices'])
        assert all('description' in idx for idx in response.json['indices'])
    
    def test_configuration_access_workflow(self, client):
        """Test accessing configuration through API."""
        response = client.get('/api/config')
        
        assert response.status_code == 200
        assert 'model' in response.json
        assert 'data' in response.json
        assert 'api' in response.json
    
    def test_health_check_workflow(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        assert 'model_loaded' in response.json
        assert 'version' in response.json


class TestDataProcessing:
    """Test data processing workflows."""
    
    def test_market_data_processing(self, sample_market_data, mock_config):
        """Test complete market data processing pipeline."""
        loader = MarketDataLoader(mock_config._config)
        
        # Test adding technical indicators
        processed_df = loader.add_technical_indicators(sample_market_data)
        
        assert 'MA_7' in processed_df.columns
        assert 'MA_30' in processed_df.columns
        assert 'EMA_12' in processed_df.columns
        assert len(processed_df) == len(sample_market_data)
    
    def test_sentiment_analysis_integration(self, sample_market_data, mock_config):
        """Test sentiment analysis integration in data processing."""
        loader = MarketDataLoader(mock_config._config)
        
        # Test adding sentiment scores
        processed_df = loader.add_sentiment_scores(sample_market_data)
        
        assert 'sentiment_score' in processed_df.columns
        assert all(processed_df['sentiment_score'] >= -1.0)
        assert all(processed_df['sentiment_score'] <= 1.0)
    
    def test_training_data_preparation(self, sample_market_data, mock_config):
        """Test preparation of training data."""
        loader = MarketDataLoader(mock_config._config)
        
        # Mock the fetch to return our sample data
        with patch.object(loader, 'fetch_multiple_symbols', return_value=sample_market_data):
            result = loader.prepare_training_data(['BTC-USD'])
        
        # Pipeline completes without errors
        # Result is a prepared DataFrame
        assert result is not None
        assert 'sentiment_score' in result.columns


class TestOutputValidation:
    """Test output formats and validation."""
    
    @pytest.fixture
    def app(self, mock_config):
        """Create test Flask app."""
        from ai_model.api.endpoints import create_app
        app = create_app(mock_config)
        app.config.update({"TESTING": True})
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_prediction_output_format(self, client, app):
        """Test that prediction output has correct format."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        expected_output = {
            'indices': [0.5, 0.6, 0.7, 0.8, 0.5, 0.6, 0.7, 0.8, 0.9, 0.4],
            'index_names': [f'Index_{i+1}' for i in range(10)],
            'confidence': 0.85,
            'symbols': ['BTC-USD', 'ETH-USD'],
            'timestamp': '2024-01-01 12:00:00'
        }
        
        app.predictor.predict_next_indices.return_value = expected_output
        
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD', 'ETH-USD']
        })
        
        assert response.status_code == 200
        result = response.json
        
        # Validate all required fields are present
        assert 'indices' in result
        assert 'confidence' in result
        assert 'symbols' in result
        assert 'timestamp' in result
        
        # Validate data types
        assert isinstance(result['indices'], list)
        assert isinstance(result['confidence'], (int, float))
        assert isinstance(result['symbols'], list)
        assert isinstance(result['timestamp'], str)
        
        # Validate values
        assert len(result['indices']) == 10
        assert 0 <= result['confidence'] <= 1
    
    def test_data_fetch_output_format(self, client, app, sample_market_data):
        """Test that data fetch output has correct format."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = sample_market_data
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD']
        })
        
        assert response.status_code == 200
        result = response.json
        
        # Validate output structure
        assert 'data' in result
        assert 'count' in result
        assert 'symbols' in result
        assert 'columns' in result
        
        # Validate data types
        assert isinstance(result['data'], list)
        assert isinstance(result['count'], int)
        assert isinstance(result['symbols'], list)
        assert isinstance(result['columns'], list)
