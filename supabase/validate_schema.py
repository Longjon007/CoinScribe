#!/usr/bin/env python3
"""
Validate that the database schema aligns with the application's data requirements.
"""

import yaml
import re
from pathlib import Path
import glob
import os

def get_project_root():
    """Get the project root directory (where supabase/ is located)."""
    # Start from script's directory and go up until we find supabase/
    current = Path(__file__).parent
    while current != current.parent:
        if (current / 'supabase').exists() and (current / 'ai_model').exists():
            return current
        current = current.parent
    # If not found, return script's parent (assume we're in supabase/)
    return Path(__file__).parent.parent

def load_config():
    """Load the application configuration."""
    root = get_project_root()
    config_path = root / "ai_model" / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_latest_migration():
    """Get the most recent migration file."""
    root = get_project_root()
    migrations_dir = root / "supabase" / "migrations"
    migration_files = list(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        raise FileNotFoundError("No migration files found in supabase/migrations/")
    
    # Sort by filename (which includes timestamp)
    return sorted(migration_files)[-1]

def check_schema_file():
    """Check that the schema file contains required tables and columns."""
    schema_path = get_latest_migration()
    print(f"Validating migration: {schema_path.name}")
    
    with open(schema_path, 'r') as f:
        schema_content = f.read()
    
    # Check for required tables
    required_tables = ['coins', 'coin_price_history', 'coin_news']
    missing_tables = []
    
    for table in required_tables:
        if f"CREATE TABLE IF NOT EXISTS public.{table}" not in schema_content:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"❌ Missing tables: {', '.join(missing_tables)}")
        return False
    else:
        print(f"✅ All required tables found: {', '.join(required_tables)}")
    
    # Check for OHLCV columns in price history
    ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = []
    
    for col in ohlcv_columns:
        if not re.search(rf'\b{col}\b\s+DECIMAL', schema_content):
            missing_columns.append(col)
    
    if missing_columns:
        print(f"❌ Missing OHLCV columns: {', '.join(missing_columns)}")
        return False
    else:
        print(f"✅ All OHLCV columns found: {', '.join(ohlcv_columns)}")
    
    # Check for sentiment score column
    if 'sentiment_score' not in schema_content:
        print("❌ Missing sentiment_score column")
        return False
    else:
        print("✅ Sentiment score column found")
    
    # Check for indexes
    if schema_content.count('CREATE INDEX') < 5:
        print("⚠️  Warning: Less than 5 indexes defined, may impact query performance")
    else:
        print(f"✅ Adequate indexes defined: {schema_content.count('CREATE INDEX')}")
    
    # Check for RLS
    if 'ROW LEVEL SECURITY' not in schema_content:
        print("❌ Missing Row Level Security configuration")
        return False
    else:
        print("✅ Row Level Security enabled")
    
    # Check for constraints
    constraint_patterns = [
        'CHECK.*>=.*0',  # Positive value checks
        'UNIQUE',  # Uniqueness
        'REFERENCES',  # Foreign keys
    ]
    
    for pattern in constraint_patterns:
        if not re.search(pattern, schema_content):
            print(f"⚠️  Warning: No constraints matching pattern: {pattern}")
    
    print("✅ Constraint validations passed")
    
    return True

def validate_config_alignment():
    """Validate that schema supports config requirements."""
    config = load_config()
    
    # Check that schema supports configured data features
    features = config.get('data', {}).get('features', [])
    print(f"\n📊 Checking support for {len(features)} configured features:")
    
    required_mappings = {
        'open': 'open',
        'high': 'high', 
        'low': 'low',
        'close': 'close',
        'volume': 'volume',
        'market_cap': 'market_cap',
        'sentiment_score': 'sentiment_score'
    }
    
    schema_path = get_latest_migration()
    with open(schema_path, 'r') as f:
        schema_content = f.read()
    
    all_supported = True
    for feature in features:
        feature_lower = feature.lower()
        if feature_lower in required_mappings:
            if required_mappings[feature_lower] in schema_content:
                print(f"  ✅ {feature}: supported")
            else:
                print(f"  ❌ {feature}: NOT supported in schema")
                all_supported = False
        else:
            print(f"  ℹ️  {feature}: no direct column mapping needed")
    
    return all_supported

def main():
    """Run all validations."""
    print("=" * 60)
    print("Database Schema Validation")
    print("=" * 60)
    print()
    
    # Check schema structure
    print("1. Validating schema structure...")
    print("-" * 60)
    schema_valid = check_schema_file()
    print()
    
    # Check config alignment
    print("2. Validating configuration alignment...")
    print("-" * 60)
    config_valid = validate_config_alignment()
    print()
    
    # Summary
    print("=" * 60)
    if schema_valid and config_valid:
        print("✅ All validations passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some validations failed!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
