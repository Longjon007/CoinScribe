#!/usr/bin/env python3
"""
Run CoinScribe AI Model API Server
===================================

This script starts the Flask API server for model inference.

Usage:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 5000 --debug
"""

import argparse
import sys
from pathlib import Path

# Ensure we can import from the current directory
# This allows the script to be run from anywhere
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent))

from ai_model.api.endpoints import run_server
from ai_model.config import config
from ai_model.utils.logger import setup_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run CoinScribe AI Model API Server'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Host address (default: from config)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port number (default: from config)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    return parser.parse_args()


def main():
    """Main server function."""
    args = parse_args()
    
    # Setup logger
    logger = setup_logger(log_file='ai_model/logs/server.log')
    logger.info("=" * 80)
    logger.info("CoinScribe AI Model API Server")
    logger.info("=" * 80)
    
    # Get configuration
    host = args.host or config.get('api.host', '0.0.0.0')
    port = args.port or config.get('api.port', 5000)
    debug = args.debug
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("=" * 80)
    
    # Run server
    run_server(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
