import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from ai_model.api.endpoints import create_app

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

    def test_list_indices(self, client):
        response = client.get('/api/indices/list')
        assert response.status_code == 200
        assert 'indices' in response.json
        assert len(response.json['indices']) == 10

    def test_get_config(self, client, mock_config):
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'model' in response.json
        assert 'data' in response.json
