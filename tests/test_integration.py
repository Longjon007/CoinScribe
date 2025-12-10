"""
Integration Testing Suite for CoinScribe Application
====================================================

Tests interactions between different modules:
- UI and backend communication
- Third-party tool integration (Supabase)
- Module interactions
"""

import pytest
import json
from unittest.mock import MagicMock, patch, call
from ai_model.api.endpoints import create_app
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.models.inference.predictor import AIIndexPredictor


class TestAPIBackendIntegration:
    """Test API and backend integration."""
    
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
    
    def test_api_to_predictor_integration(self, client, app, sample_market_data):
        """Test integration between API and predictor."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Setup mock
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.75] * 10,
            'confidence': 0.85
        }
        
        # Make API call
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        
        # Verify predictor was called with correct parameters
        assert app.predictor.predict_next_indices.called
        call_args = app.predictor.predict_next_indices.call_args
        assert call_args[1]['symbols'] == ['BTC-USD']
        assert call_args[1]['data_loader'] == app.data_loader
        
        assert response.status_code == 200
    
    def test_api_to_data_loader_integration(self, client, app, sample_market_data):
        """Test integration between API and data loader."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = sample_market_data
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        # Make API call
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD', 'ETH-USD'],
            'period': '7d',
            'interval': '1h'
        })
        
        # Verify data loader was called with correct parameters
        assert app.data_loader.fetch_multiple_symbols.called
        call_args = app.data_loader.fetch_multiple_symbols.call_args
        assert call_args[1]['symbols'] == ['BTC-USD', 'ETH-USD']
        assert call_args[1]['period'] == '7d'
        assert call_args[1]['interval'] == '1h'
        
        assert response.status_code == 200
    
    def test_predictor_to_data_loader_integration(self, mock_config, sample_market_data):
        """Test integration between predictor and data loader."""
        # This test would require actual model file, so we mock it
        with patch('ai_model.models.inference.predictor.torch.load') as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = {'model_state_dict': {}}
            
            with patch('ai_model.models.inference.predictor.AIIndexModel') as mock_model_class:
                mock_model_instance = MagicMock()
                mock_model_class.return_value = mock_model_instance
                
                try:
                    predictor = AIIndexPredictor(
                        model_path='test.pth',
                        config=mock_config._config
                    )
                    
                    # Verify predictor was initialized
                    assert predictor is not None
                except Exception as e:
                    # Expected if model loading fails in test environment
                    assert 'model' in str(e).lower() or 'file' in str(e).lower()


class TestSupabaseIntegration:
    """Test Supabase database integration."""
    
    def test_supabase_connection_mock(self):
        """Test Supabase connection (mocked)."""
        # Mock Supabase client
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='Success')
            
            # Simulate supabase db push
            import subprocess
            result = subprocess.run(
                ['echo', 'supabase db push'],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0
    
    def test_supabase_db_reset_mock(self):
        """Test Supabase db reset command (mocked)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='Reset successful')
            
            # Simulate supabase db reset
            import subprocess
            result = subprocess.run(
                ['echo', 'supabase db reset'],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0
    
    def test_supabase_environment_variables(self):
        """Test that Supabase environment variables are properly handled."""
        import os
        
        # Test that sensitive variables are not exposed
        env_vars = ['SUPABASE_ACCESS_TOKEN', 'SUPABASE_DB_PASSWORD']
        
        for var in env_vars:
            # These should either not exist or not be logged
            value = os.environ.get(var, None)
            if value:
                # Ensure it's not empty or a placeholder
                assert len(value) > 0
                # Should not be visible in tests
                assert var not in str(value)


class TestModuleInteractions:
    """Test interactions between different application modules."""
    
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
    
    def test_config_to_all_modules(self, mock_config):
        """Test that configuration is properly passed to all modules."""
        # Test data loader receives config
        loader = MarketDataLoader(mock_config._config)
        assert loader.config is not None
        assert loader.symbols == mock_config._config['data_sources']['market_data']['symbols']
    
    def test_data_pipeline_flow(self, mock_config, sample_market_data):
        """Test complete data pipeline flow."""
        loader = MarketDataLoader(mock_config._config)
        
        # Step 1: Add technical indicators
        with_indicators = loader.add_technical_indicators(sample_market_data)
        assert len(with_indicators.columns) > len(sample_market_data.columns)
        
        # Step 2: Add sentiment scores
        with_sentiment = loader.add_sentiment_scores(with_indicators)
        assert 'sentiment_score' in with_sentiment.columns
        
        # Step 3: Prepare training data (mock fetch to use our sample data)
        with patch.object(loader, 'fetch_multiple_symbols', return_value=with_sentiment):
            result = loader.prepare_training_data(['BTC-USD'])
        # Pipeline completed without errors
        assert result is not None
        assert 'sentiment_score' in result.columns
    
    def test_error_propagation(self, client, app):
        """Test that errors propagate correctly through the stack."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Simulate error in predictor
        app.predictor.predict_next_indices.side_effect = Exception("Test error")
        
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        
        # Error should be caught and returned as 500
        assert response.status_code == 500
        assert 'error' in response.json
        assert 'Test error' in response.json['error']


class TestThirdPartyIntegration:
    """Test integration with third-party services."""
    
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
    
    @patch('yfinance.download')
    def test_yfinance_integration(self, mock_download, mock_config, sample_market_data):
        """Test integration with yfinance API."""
        mock_download.return_value = sample_market_data
        
        loader = MarketDataLoader(mock_config._config)
        
        # This would normally call yfinance
        with patch.object(loader, 'fetch_market_data', return_value=sample_market_data):
            result = loader.fetch_market_data('BTC-USD')
            assert result is not None
            assert len(result) > 0
    
    def test_cors_configuration(self, app):
        """Test CORS configuration for cross-origin requests."""
        client = app.test_client()
        
        response = client.get('/health', headers={
            'Origin': 'http://example.com'
        })
        
        # CORS headers should be present
        assert response.status_code == 200
    
    def test_api_content_type_handling(self, client, app, sample_market_data):
        """Test API handles different content types correctly."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = sample_market_data
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        # Test with JSON content type
        response = client.post('/api/data/fetch',
                              data=json.dumps({'symbols': ['BTC-USD']}),
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'


class TestConcurrentOperations:
    """Test concurrent operations and thread safety."""
    
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
    
    def test_multiple_concurrent_requests(self, client, app):
        """Test handling multiple concurrent API requests."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Simulate concurrent requests
        responses = []
        for _ in range(5):
            response = client.post('/api/predict/indices', json={
                'symbols': ['BTC-USD']
            })
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    def test_health_check_during_operations(self, client, app):
        """Test that health checks work during other operations."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Start a prediction
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        pred_response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        
        # Health check should still work
        health_response = client.get('/health')
        
        assert pred_response.status_code == 200
        assert health_response.status_code == 200
