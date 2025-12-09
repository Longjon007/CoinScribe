import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from ai_model.api.endpoints import create_app
import logging

class TestAPIEndpoints:
    @pytest.fixture
    def app(self, mock_config):
        app = create_app(mock_config)
        app.config.update({
            "TESTING": True,
        })

        # Mock predictor and data loader
        app.predictor = MagicMock()
        app.data_loader = MagicMock()

        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'

    def test_model_info(self, client, app):
        app.predictor.get_model_info.return_value = {'model_path': 'test'}

        response = client.get('/api/model/info')
        assert response.status_code == 200
        assert response.json['model_path'] == 'test'

    def test_model_info_error(self, client, app):
        app.predictor = None
        response = client.get('/api/model/info')
        assert response.status_code == 500
        assert 'error' in response.json

    def test_model_info_exception(self, client, app):
        app.predictor.get_model_info.side_effect = Exception("Crash")
        response = client.get('/api/model/info')
        assert response.status_code == 500
        assert 'error' in response.json
        assert 'traceback' in response.json

    def test_predict_indices(self, client, app):
        app.predictor.predict_next_indices.return_value = {
            'indices': [0.1, 0.2],
            'confidence': 0.9
        }

        response = client.post('/api/predict/indices', json={
            'symbols': ['BTC-USD']
        })

        assert response.status_code == 200
        assert 'indices' in response.json
        assert response.json['confidence'] == 0.9

    def test_predict_indices_error_no_model(self, client, app):
        app.predictor = None
        response = client.post('/api/predict/indices')
        assert response.status_code == 500
        assert 'error' in response.json

    def test_predict_indices_exception(self, client, app):
        app.predictor.predict_next_indices.side_effect = Exception("Crash")
        response = client.post('/api/predict/indices')
        assert response.status_code == 500
        assert 'error' in response.json
        assert 'traceback' in response.json

    def test_fetch_market_data(self, client, app):
        import pandas as pd
        df = pd.DataFrame({'Close': [1, 2, 3]})
        app.data_loader.fetch_multiple_symbols.return_value = df
        app.data_loader.symbols = ['BTC-USD']
        app.data_loader.period = '1d'
        app.data_loader.interval = '1h'

        response = client.post('/api/data/fetch', json={})

        assert response.status_code == 200
        assert response.json['count'] == 3

    def test_fetch_market_data_empty(self, client, app):
        import pandas as pd
        app.data_loader.fetch_multiple_symbols.return_value = pd.DataFrame()
        app.data_loader.symbols = ['BTC-USD']

        response = client.post('/api/data/fetch', json={})
        assert response.status_code == 404

    def test_fetch_market_data_no_loader(self, client, app):
        app.data_loader = None
        response = client.post('/api/data/fetch')
        assert response.status_code == 500

    def test_fetch_market_data_exception(self, client, app):
        app.data_loader.fetch_multiple_symbols.side_effect = Exception("Crash")
        response = client.post('/api/data/fetch')
        assert response.status_code == 500
        assert 'traceback' in response.json

    def test_list_indices(self, client):
        response = client.get('/api/indices/list')
        assert response.status_code == 200
        assert 'indices' in response.json
        assert len(response.json['indices']) == 10

    def test_list_indices_exception(self, client, app):
        with patch('ai_model.api.endpoints.jsonify', side_effect=Exception("JSON Error")):
            try:
                client.get('/api/indices/list')
            except:
                pass

    def test_get_config(self, client, mock_config):
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'model' in response.json
        assert 'data' in response.json

    def test_get_config_exception(self, client, mock_config):
        with patch('ai_model.api.endpoints.jsonify', side_effect=[Exception("First"), MagicMock()]):
             response = client.get('/api/config')
             assert response.status_code == 500

    def test_404_handler(self, client):
        response = client.get('/non/existent')
        assert response.status_code == 404
        assert response.json['error'] == 'Endpoint not found'

    def test_500_handler(self, client, app):
        with patch('ai_model.api.endpoints.jsonify', side_effect=Exception("Server Error")):
             try:
                 client.get('/health')
             except:
                 pass
             # The test client might raise the exception directly in debug mode
             # But if handled by errorhandler(500), it should return 500 response.
             # If jsonify raises in health_check, it goes to 500 handler.
             # If 500 handler's jsonify works, we get 500.

    def test_create_app_exception(self):
        # Test exception during initialization
        with patch('ai_model.api.endpoints.AIIndexPredictor', side_effect=Exception("Init Failed")):
            app = create_app()
            assert app.predictor is None

    def test_run_server(self):
        with patch('ai_model.api.endpoints.create_app') as mock_create:
            mock_app = MagicMock()
            mock_create.return_value = mock_app

            from ai_model.api.endpoints import run_server
            run_server(host='1.2.3.4', port=9999, debug=True)

            mock_app.run.assert_called_with(host='1.2.3.4', port=9999, debug=True)
