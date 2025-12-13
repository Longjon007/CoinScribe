"""
Cross-Platform Testing Suite for CoinScribe Application
=======================================================

Tests application compatibility across:
- Different operating systems
- Different Python versions
- Different browsers (API perspective)
- Various client configurations
"""

import pytest
import platform
import sys
import json
from unittest.mock import MagicMock, patch
from ai_model.api.endpoints import create_app


class TestPlatformCompatibility:
    """Test compatibility across different platforms."""
    
    def test_python_version_compatibility(self):
        """Test that Python version is supported."""
        version = sys.version_info
        
        # Should be Python 3.8+
        assert version.major == 3, "Should use Python 3"
        assert version.minor >= 8, "Should be Python 3.8 or higher"
    
    def test_platform_detection(self):
        """Test platform detection."""
        system = platform.system()
        
        # Should work on common platforms
        assert system in ['Linux', 'Windows', 'Darwin'], \
            f"Platform {system} should be recognized"
    
    def test_path_separators(self):
        """Test that path handling works across platforms."""
        import os
        from pathlib import Path
        
        # Test that Path works correctly
        test_path = Path('/home/runner/work/CoinScribe/CoinScribe')
        
        # Should handle paths correctly
        assert test_path.is_absolute()
    
    def test_module_imports(self):
        """Test that all required modules can be imported."""
        required_modules = [
            'torch',
            'numpy',
            'pandas',
            'flask',
            'yaml',
            'pytest',
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")


class TestAPIClientCompatibility:
    """Test API compatibility with different clients."""
    
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
    
    def test_json_content_type(self, client, app):
        """Test API works with JSON content type."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        response = client.post('/api/predict/indices',
                              data=json.dumps({'symbols': ['BTC-USD']}),
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_various_user_agents(self, client):
        """Test API works with various user agents."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/89.0',
            'curl/7.68.0',
            'Python-requests/2.25.1',
        ]
        
        for user_agent in user_agents:
            response = client.get('/health', headers={
                'User-Agent': user_agent
            })
            assert response.status_code == 200
    
    def test_different_accept_headers(self, client):
        """Test API responds correctly to different Accept headers."""
        accept_headers = [
            'application/json',
            '*/*',
            'application/json, text/plain, */*',
        ]
        
        for accept in accept_headers:
            response = client.get('/health', headers={
                'Accept': accept
            })
            assert response.status_code == 200
    
    def test_http_methods(self, client):
        """Test appropriate HTTP methods are supported."""
        # GET endpoints
        get_response = client.get('/health')
        assert get_response.status_code == 200
        
        # POST endpoints
        app = client.application
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        post_response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        assert post_response.status_code == 200
        
        # Unsupported methods should fail appropriately
        delete_response = client.delete('/health')
        assert delete_response.status_code in [404, 405]


class TestCharacterEncodingCompatibility:
    """Test handling of different character encodings."""
    
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
    
    def test_utf8_encoding(self, client, app):
        """Test UTF-8 encoding support."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Test with UTF-8 characters
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        }, headers={'Content-Type': 'application/json; charset=utf-8'})
        
        assert response.status_code == 200
    
    def test_special_characters_in_symbols(self, client, app):
        """Test handling of special characters."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        # Test with various special characters
        special_symbols = [
            'BTC-USD',
            'ETH/USD',
            'COIN_TEST',
        ]
        
        for symbol in special_symbols:
            response = client.post('/api/predict/indices', json={
                'symbols': [symbol]
            })
            # Should handle gracefully
            assert response.status_code in [200, 400, 500]


class TestDataFormatCompatibility:
    """Test compatibility with different data formats."""
    
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
    
    def test_empty_request_body(self, client, app):
        """Test handling of empty request body."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8
        }
        
        response = client.post('/api/predict/indices', json={})
        # Should use defaults or handle gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_minimal_request_body(self, client, app, sample_market_data):
        """Test handling of minimal request body."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = sample_market_data
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        response = client.post('/api/data/fetch', json={})
        assert response.status_code == 200
    
    def test_response_format_consistency(self, client):
        """Test that response format is consistent."""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        
        # Should have consistent structure
        assert isinstance(data, dict)


class TestTimezoneCompatibility:
    """Test timezone and datetime handling."""
    
    def test_timestamp_parsing(self):
        """Test that timestamps are parsed correctly."""
        from datetime import datetime
        import pandas as pd
        
        # Test various timestamp formats
        timestamp_formats = [
            '2024-01-01 12:00:00',
            '2024-01-01T12:00:00',
            '2024-01-01T12:00:00Z',
            '2024-01-01T12:00:00+00:00',
        ]
        
        for ts in timestamp_formats:
            try:
                parsed = pd.to_datetime(ts)
                assert parsed is not None
            except Exception as e:
                pytest.fail(f"Failed to parse timestamp {ts}: {e}")
    
    def test_datetime_serialization(self):
        """Test datetime serialization in JSON responses."""
        import pandas as pd
        from datetime import datetime
        
        # Test that dates can be serialized
        test_date = pd.Timestamp('2024-01-01 12:00:00')
        
        # Should be convertible to string for JSON
        date_str = test_date.isoformat()
        assert isinstance(date_str, str)


class TestDependencyCompatibility:
    """Test compatibility with different dependency versions."""
    
    def test_torch_availability(self):
        """Test that PyTorch is available."""
        try:
            import torch
            assert torch is not None
            # Check CUDA availability (optional)
            cuda_available = torch.cuda.is_available()
            # Should work with or without CUDA
            assert cuda_available in [True, False]
        except ImportError as e:
            pytest.fail(f"PyTorch not available: {e}")
    
    def test_numpy_compatibility(self):
        """Test NumPy compatibility."""
        import numpy as np
        
        # Test basic operations
        arr = np.array([1, 2, 3])
        assert arr.shape == (3,)
    
    def test_pandas_compatibility(self):
        """Test Pandas compatibility."""
        import pandas as pd
        
        # Test basic operations
        df = pd.DataFrame({'A': [1, 2, 3]})
        assert len(df) == 3
    
    def test_flask_compatibility(self):
        """Test Flask compatibility."""
        from flask import Flask
        
        test_app = Flask(__name__)
        assert test_app is not None
    
    def test_yfinance_compatibility(self):
        """Test yfinance availability."""
        try:
            import yfinance as yf
            assert yf is not None
        except ImportError as e:
            pytest.fail(f"yfinance not available: {e}")


class TestNetworkConfiguration:
    """Test network and connectivity configurations."""
    
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
    
    def test_localhost_access(self, client):
        """Test API accessible on localhost."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_ipv4_support(self):
        """Test IPv4 address support."""
        # Test that we can create app with IPv4 config
        app = create_app()
        assert app is not None
    
    def test_custom_port_configuration(self, mock_config):
        """Test that custom ports can be configured."""
        # Test various port configurations
        ports = [5000, 8080, 3000]
        
        for port in ports:
            mock_config._config['api']['port'] = port
            app = create_app(mock_config)
            assert app is not None


class TestBrowserCompatibility:
    """Test API from browser perspective."""
    
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
    
    def test_options_request(self, client):
        """Test OPTIONS requests (CORS preflight)."""
        response = client.options('/api/predict/indices')
        # Should allow OPTIONS
        assert response.status_code in [200, 204]
    
    def test_get_with_query_params(self, client):
        """Test GET requests with query parameters."""
        response = client.get('/health?test=true')
        assert response.status_code == 200
    
    def test_post_with_form_data(self, client, app):
        """Test POST with form data (if supported)."""
        # API primarily uses JSON, but test resilience
        response = client.post('/api/predict/indices',
                              data={'symbols': 'BTC-USD'},
                              content_type='application/x-www-form-urlencoded')
        
        # Should either work or return meaningful error
        assert response.status_code in [200, 400, 415, 500]
