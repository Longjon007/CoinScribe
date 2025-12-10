#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for CoinScribe
==============================================

Runs all test categories and generates comprehensive reports.

Usage:
    python run_comprehensive_tests.py
    python run_comprehensive_tests.py --category functional
    python run_comprehensive_tests.py --verbose
"""

import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def run_tests(category=None, verbose=False, coverage=False):
    """
    Run comprehensive test suite.
    
    Args:
        category: Specific test category to run (optional)
        verbose: Enable verbose output
        coverage: Enable coverage reporting
    """
    print("="*80)
    print("CoinScribe Comprehensive Test Suite")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory or specific category
    if category:
        test_files = {
            'functional': 'tests/test_functional.py',
            'integration': 'tests/test_integration.py',
            'unit': 'tests/ai_model/',
            'performance': 'tests/test_performance.py',
            'security': 'tests/test_security.py',
            'workflow': 'tests/test_workflow.py',
            'crossplatform': 'tests/test_cross_platform.py',
            'results': 'tests/test_results_logger.py',
        }
        
        if category not in test_files:
            print(f"Error: Unknown category '{category}'")
            print(f"Available categories: {', '.join(test_files.keys())}")
            return 1
        
        cmd.append(test_files[category])
        print(f"Running {category.upper()} tests only")
    else:
        cmd.append('tests/')
        print("Running ALL test categories")
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-v')  # Default to verbose
    
    # Add coverage
    if coverage:
        cmd.extend(['--cov=ai_model', '--cov-report=html', '--cov-report=term'])
    
    # Add color output
    cmd.append('--color=yes')
    
    # Add test summary
    cmd.append('--tb=short')
    
    print("="*80)
    print(f"Command: {' '.join(cmd)}")
    print("="*80)
    print()
    
    # Run tests
    result = subprocess.run(cmd)
    
    print()
    print("="*80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run CoinScribe comprehensive test suite'
    )
    
    parser.add_argument(
        '--category',
        choices=[
            'functional', 'integration', 'unit', 'performance',
            'security', 'workflow', 'crossplatform', 'results', 'all'
        ],
        help='Run specific test category'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    
    args = parser.parse_args()
    
    # Run all categories if 'all' specified
    if args.category == 'all':
        args.category = None
    
    return run_tests(
        category=args.category,
        verbose=args.verbose,
        coverage=args.coverage
    )


if __name__ == '__main__':
    sys.exit(main())
