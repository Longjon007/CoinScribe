"""Setup configuration for CoinScribe AI Model."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        'torch>=2.6.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0',
        'yfinance>=0.2.28',
        'requests>=2.31.0',
        'flask>=3.0.0',
        'flask-cors>=4.0.0',
        'pyyaml>=6.0',
        'python-dotenv>=1.0.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'tensorboard>=2.14.0',
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
    ]

setup(
    name='coinscribe-ai',
    version='0.1.0',
    author='CoinScribe Team',
    description='AI Model for CoinScribe Investment Index Creation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Longjon007/CoinScribe',
    packages=find_packages(include=['ai_model', 'ai_model.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'coinscribe-train=train_model:main',
            'coinscribe-serve=run_server:main',
            'coinscribe-example=example_usage:main',
        ],
    },
    include_package_data=True,
    package_data={
        'ai_model': [
            'config/*.yaml',
            'docs/*.md',
        ],
    },
)
