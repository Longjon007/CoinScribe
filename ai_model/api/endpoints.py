"""
API Endpoints for AI Index Prediction
======================================

Flask-based REST API for interacting with the AI model.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict
import logging
import traceback

from ..models.inference.predictor import AIIndexPredictor
from ..data.pipelines.data_loader import MarketDataLoader
from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_obj=None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_obj: Configuration object (uses global config if None)
        
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_obj is None:
        config_obj = config
    
    # Enable CORS
    cors_origins = config_obj.get('api.cors_origins', ['*'])
    CORS(app, origins=cors_origins)
    
    # Initialize components
    try:
        model_path = config_obj.get('serving.model_path', 'ai_model/models/checkpoints/best_model.pth')
        predictor = AIIndexPredictor(
            model_path=model_path,
            config=config_obj._config
        )
        data_loader = MarketDataLoader(config_obj._config)
        
        app.predictor = predictor
        app.data_loader = data_loader
        
        logger.info("API components initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing API components: {str(e)}")
        app.predictor = None
        app.data_loader = None
    
    # Define routes
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint.

        Returns:
            tuple: JSON response and status code.
        """
        return jsonify({
            'status': 'healthy',
            'model_loaded': app.predictor is not None,
            'version': '0.1.0'
        }), 200
    
    @app.route('/api/model/info', methods=['GET'])
    def model_info():
        """
        Get model information.

        Returns:
            tuple: JSON response with model info and status code.
        """
        try:
            if app.predictor is None:
                return jsonify({
                    'error': 'Model not loaded'
                }), 500
            
            info = app.predictor.get_model_info()
            return jsonify(info), 200
            
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/api/predict/indices', methods=['POST'])
    def predict_indices():
        """
        Predict AI indices based on market data.
        
        Request body:
        {
            "symbols": ["BTC-USD", "ETH-USD"],  // Optional, uses config default if not provided
            "period": "1mo",  // Optional
            "interval": "1h"  // Optional
        }
        
        Returns:
            tuple: JSON response with predictions and status code.

        Response example:
        {
            "indices": [0.75, 0.82, ...],
            "index_names": ["Index_1", "Index_2", ...],
            "confidence": 0.85,
            "symbols": ["BTC-USD", "ETH-USD"],
            "timestamp": "2024-01-01 12:00:00"
        }
        """
        try:
            if app.predictor is None or app.data_loader is None:
                return jsonify({
                    'error': 'Model or data loader not initialized'
                }), 500
            
            # Parse request
            data = request.get_json() or {}
            symbols = data.get('symbols', None)
            
            # Make prediction
            result = app.predictor.predict_next_indices(
                symbols=symbols,
                data_loader=app.data_loader
            )
            
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/api/data/fetch', methods=['POST'])
    def fetch_market_data():
        """
        Fetch market data for specified symbols.
        
        Request body:
        {
            "symbols": ["BTC-USD", "ETH-USD"],
            "period": "1mo",
            "interval": "1h"
        }
        
        Returns:
            tuple: JSON response with market data and status code.

        Response example:
        {
            "data": [...],
            "count": 100,
            "symbols": ["BTC-USD", "ETH-USD"]
        }
        """
        try:
            if app.data_loader is None:
                return jsonify({
                    'error': 'Data loader not initialized'
                }), 500
            
            # Parse request
            data = request.get_json() or {}
            symbols = data.get('symbols', app.data_loader.symbols)
            period = data.get('period', app.data_loader.period)
            interval = data.get('interval', app.data_loader.interval)
            
            # Fetch data
            df = app.data_loader.fetch_multiple_symbols(
                symbols=symbols,
                period=period,
                interval=interval
            )
            
            if df.empty:
                return jsonify({
                    'error': 'No data retrieved',
                    'symbols': symbols
                }), 404
            
            # Convert to JSON-serializable format
            result = {
                'data': df.to_dict('records'),
                'count': len(df),
                'symbols': symbols,
                'columns': list(df.columns)
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/api/indices/list', methods=['GET'])
    def list_indices():
        """
        List available AI indices.
        
        Returns:
            tuple: JSON response with indices list and status code.

        Response example:
        {
            "indices": [
                {"name": "Index_1", "description": "..."},
                ...
            ]
        }
        """
        try:
            # This is a placeholder - in production, this would list actual indices
            indices = [
                {
                    'name': f'Index_{i+1}',
                    'description': f'AI-generated investment index {i+1}',
                    'type': 'composite'
                }
                for i in range(10)
            ]
            
            return jsonify({
                'indices': indices,
                'count': len(indices)
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing indices: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """
        Get current API configuration (non-sensitive parts).
        
        Returns:
            tuple: JSON response with configuration and status code.

        Response example:
        {
            "model": {...},
            "data": {...},
            "api": {...}
        }
        """
        try:
            safe_config = {
                'model': {
                    'architecture': config_obj.get('model.architecture'),
                    'input_features': config_obj.get('model.input_features'),
                    'output_size': config_obj.get('model.output_size')
                },
                'data': {
                    'sequence_length': config_obj.get('data.sequence_length'),
                    'features': config_obj.get('data.features')
                },
                'api': {
                    'version': '0.1.0'
                }
            }
            
            return jsonify(safe_config), 200
            
        except Exception as e:
            logger.error(f"Error getting config: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 errors.

        Args:
            error: Error description.

        Returns:
            tuple: JSON response and status code.
        """
        return jsonify({
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 errors.

        Args:
            error: Error description.

        Returns:
            tuple: JSON response and status code.
        """
        return jsonify({
            'error': 'Internal server error'
        }), 500
    
    return app


def run_server(host: str = None, port: int = None, debug: bool = False):
    """
    Run the Flask development server.
    
    Args:
        host: Host address
        port: Port number
        debug: Debug mode
    """
    app = create_app()
    
    host = host or config.get('api.host', '0.0.0.0')
    port = port or config.get('api.port', 5000)
    debug = debug or config.get('api.debug', False)
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
