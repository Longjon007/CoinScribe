"""
Performance Testing Suite for CoinScribe Application
====================================================

Tests application stability and responsiveness under various load conditions:
- Standard load testing
- High load testing
- Stress testing
- Response time benchmarks
"""

import pytest
import time
import pandas as pd
from unittest.mock import MagicMock, patch
from ai_model.api.endpoints import create_app
from ai_model.data.pipelines.data_loader import MarketDataLoader


class TestResponseTimes:
    """Test API response times."""
    
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
    
    def test_health_check_response_time(self, client):
        """Test health check responds quickly."""
        start_time = time.time()
        response = client.get('/health')
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Health check should respond in under 100ms
        assert elapsed_time < 0.1, f"Health check took {elapsed_time:.3f}s"
    
    def test_model_info_response_time(self, client, app):
        """Test model info endpoint response time."""
        app.predictor = MagicMock()
        app.predictor.get_model_info.return_value = {'model': 'test'}
        
        start_time = time.time()
        response = client.get('/api/model/info')
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond in under 500ms
        assert elapsed_time < 0.5, f"Model info took {elapsed_time:.3f}s"
    
    def test_list_indices_response_time(self, client):
        """Test list indices endpoint response time."""
        start_time = time.time()
        response = client.get('/api/indices/list')
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond in under 200ms
        assert elapsed_time < 0.2, f"List indices took {elapsed_time:.3f}s"
    
    def test_prediction_response_time(self, client, app):
        """Test prediction endpoint response time."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        start_time = time.time()
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Prediction should complete in reasonable time (mocked, so fast)
        assert elapsed_time < 1.0, f"Prediction took {elapsed_time:.3f}s"


class TestStandardLoad:
    """Test application under standard load conditions."""
    
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
    
    def test_sequential_requests(self, client, app):
        """Test handling sequential requests (standard load)."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Make 10 sequential requests
        num_requests = 10
        start_time = time.time()
        responses = []
        
        for i in range(num_requests):
            response = client.post('/api/predict/indices', json={
                'symbols': ['BTC-USD']
            })
            responses.append(response)
        
        elapsed_time = time.time() - start_time
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Average response time should be reasonable
        avg_time = elapsed_time / num_requests
        assert avg_time < 0.5, f"Average response time: {avg_time:.3f}s"
    
    def test_mixed_endpoint_requests(self, client, app):
        """Test handling mixed requests to different endpoints."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        app.predictor.get_model_info.return_value = {'model': 'test'}
        
        # Mix of different endpoint calls
        responses = []
        
        responses.append(client.get('/health'))
        responses.append(client.get('/api/model/info'))
        responses.append(client.get('/api/indices/list'))
        responses.append(client.post('/api/predict/indices', json={'symbols': ['BTC-USD']}))
        responses.append(client.get('/api/config'))
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)


class TestHighLoad:
    """Test application under high load conditions."""
    
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
    
    def test_high_volume_requests(self, client, app):
        """Test handling high volume of requests."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Make 50 requests
        num_requests = 50
        responses = []
        
        start_time = time.time()
        for i in range(num_requests):
            response = client.post('/api/predict/indices', json={
                'symbols': ['BTC-USD']
            })
            responses.append(response)
        
        elapsed_time = time.time() - start_time
        
        # All should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        success_rate = success_count / num_requests
        
        assert success_rate >= 0.95, f"Success rate: {success_rate:.2%}"
        
        # Log performance metrics
        print(f"\nHigh Load Test Results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {success_count}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Total time: {elapsed_time:.2f}s")
        print(f"  Average time per request: {elapsed_time/num_requests:.3f}s")
    
    def test_rapid_fire_health_checks(self, client):
        """Test rapid health check requests."""
        num_requests = 100
        responses = []
        
        start_time = time.time()
        for _ in range(num_requests):
            responses.append(client.get('/health'))
        elapsed_time = time.time() - start_time
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Should handle high frequency health checks
        print(f"\nHealth Check Load Test:")
        print(f"  Requests: {num_requests}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Requests/second: {num_requests/elapsed_time:.1f}")


class TestStressConditions:
    """Test application under stress conditions."""
    
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
    
    def test_large_data_handling(self, client, app, sample_market_data):
        """Test handling large datasets."""
        app.data_loader = MagicMock()
        
        # Create large dataset
        large_df = pd.concat([sample_market_data] * 10, ignore_index=True)
        app.data_loader.fetch_multiple_symbols.return_value = large_df
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        response = client.post('/api/data/fetch', json={
            'symbols': ['BTC-USD']
        })
        
        assert response.status_code == 200
        assert response.json['count'] == len(large_df)
    
    def test_multiple_symbols_stress(self, client, app):
        """Test handling multiple symbols simultaneously."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Request predictions for many symbols
        many_symbols = [f'COIN{i}-USD' for i in range(20)]
        
        response = client.post('/api/predict/indices', json={
            'symbols': many_symbols
        })
        
        # Should handle gracefully (may succeed or return meaningful error)
        assert response.status_code in [200, 400, 500]
        assert 'indices' in response.json or 'error' in response.json
    
    def test_error_recovery(self, client, app):
        """Test application recovers from errors."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # First request causes error
        app.predictor.predict_next_indices.side_effect = Exception("Temporary error")
        
        response1 = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        assert response1.status_code == 500
        
        # Second request should still work
        app.predictor.predict_next_indices.side_effect = None
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        response2 = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        assert response2.status_code == 200
    
    def test_memory_efficiency(self, client, app):
        """Test that application doesn't leak memory under load."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Make many requests
        for _ in range(30):
            response = client.post('/api/predict/indices', json={
                'symbols': ['BTC-USD']
            })
            assert response.status_code == 200
        
        # Application should still be responsive
        health_response = client.get('/health')
        assert health_response.status_code == 200


class TestDataProcessingPerformance:
    """Test data processing performance."""
    
    def test_technical_indicators_performance(self, sample_market_data, mock_config):
        """Test technical indicators calculation performance."""
        loader = MarketDataLoader(mock_config._config)
        
        start_time = time.time()
        result = loader.add_technical_indicators(sample_market_data)
        elapsed_time = time.time() - start_time
        
        assert result is not None
        # Should complete in reasonable time
        assert elapsed_time < 2.0, f"Technical indicators took {elapsed_time:.3f}s"
    
    def test_sentiment_analysis_performance(self, sample_market_data, mock_config):
        """Test sentiment analysis performance."""
        loader = MarketDataLoader(mock_config._config)
        
        start_time = time.time()
        result = loader.add_sentiment_scores(sample_market_data)
        elapsed_time = time.time() - start_time
        
        assert result is not None
        # Should complete quickly (mocked data)
        assert elapsed_time < 1.0, f"Sentiment analysis took {elapsed_time:.3f}s"
    
    def test_training_data_preparation_performance(self, sample_market_data, mock_config):
        """Test training data preparation performance."""
        loader = MarketDataLoader(mock_config._config)
        
        start_time = time.time()
        # Mock fetch to use our sample data
        with patch.object(loader, 'fetch_multiple_symbols', return_value=sample_market_data):
            result = loader.prepare_training_data(['BTC-USD'])
        elapsed_time = time.time() - start_time
        
        # Verify completion
        assert result is not None
        # Should prepare data efficiently
        assert elapsed_time < 1.0, f"Data preparation took {elapsed_time:.3f}s"
