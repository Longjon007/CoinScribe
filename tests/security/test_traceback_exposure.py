import unittest
from unittest.mock import MagicMock, patch
import sys

# Mocking ALL dependencies including flask for environment without them
mock_modules = {
    'pandas': MagicMock(),
    'numpy': MagicMock(),
    'torch': MagicMock(),
    'yfinance': MagicMock(),
    'sklearn': MagicMock(),
    'sklearn.preprocessing': MagicMock(),
    'matplotlib': MagicMock(),
    'matplotlib.pyplot': MagicMock(),
    'yaml': MagicMock(),
    'flask': MagicMock(),
    'flask_cors': MagicMock(),
    'flask.Flask': MagicMock(),
    'flask.request': MagicMock(),
    'flask.jsonify': MagicMock()
}

with patch.dict('sys.modules', mock_modules):
    from ai_model.api.endpoints import create_app

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        self.mock_config_obj = MagicMock()
        self.mock_config_obj._config = {}

        def mock_get(key, default=None):
            if key == 'api.debug':
                return self.debug_val
            if key == 'api.cors_origins':
                return ['*']
            return default

        self.mock_config_obj.get.side_effect = mock_get

        # Setup Flask mock
        self.mock_app = MagicMock()
        mock_modules['flask'].Flask.return_value = self.mock_app

        self.routes = {}
        def route(path, methods=None):
            def decorator(f):
                self.routes[path] = f
                return f
            return decorator
        self.mock_app.route.side_effect = route
        mock_modules['flask'].jsonify.side_effect = lambda x: x

    def test_model_info_traceback_exposure(self):
        # Test Debug OFF
        self.debug_val = False
        app = create_app(self.mock_config_obj)
        app.predictor = MagicMock()
        app.predictor.get_model_info.side_effect = Exception("Model Info Error")

        response = self.routes['/api/model/info']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertNotIn('traceback', response[0])

        # Test Debug ON
        self.debug_val = True
        app = create_app(self.mock_config_obj)
        app.predictor = MagicMock()
        app.predictor.get_model_info.side_effect = Exception("Model Info Error")

        response = self.routes['/api/model/info']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertIn('traceback', response[0])

    def test_predict_indices_traceback_exposure(self):
        # Test Debug OFF
        self.debug_val = False
        app = create_app(self.mock_config_obj)
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.side_effect = Exception("Prediction Error")

        # Mock request.get_json
        mock_modules['flask'].request.get_json.return_value = {}

        response = self.routes['/api/predict/indices']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertNotIn('traceback', response[0])

        # Test Debug ON
        self.debug_val = True
        app = create_app(self.mock_config_obj)
        app.predictor = MagicMock()
        app.data_loader = MagicMock()
        app.predictor.predict_next_indices.side_effect = Exception("Prediction Error")

        response = self.routes['/api/predict/indices']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertIn('traceback', response[0])

    def test_fetch_market_data_traceback_exposure(self):
        # Test Debug OFF
        self.debug_val = False
        app = create_app(self.mock_config_obj)
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.side_effect = Exception("Data Fetch Error")

        # Mock request.get_json
        mock_modules['flask'].request.get_json.return_value = {}

        response = self.routes['/api/data/fetch']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertNotIn('traceback', response[0])

        # Test Debug ON
        self.debug_val = True
        app = create_app(self.mock_config_obj)
        app.data_loader = MagicMock()
        app.data_loader.fetch_multiple_symbols.side_effect = Exception("Data Fetch Error")

        response = self.routes['/api/data/fetch']()
        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0])
        self.assertIn('traceback', response[0])

if __name__ == '__main__':
    unittest.main()
