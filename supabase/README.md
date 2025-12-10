# CoinScribe Database Schema

This directory contains the Supabase database schema and migrations for the CoinScribe application.

## Database Structure

### Tables

#### 1. `coins`
Main table for storing cryptocurrency metadata and current market data.

**Columns:**
- `id` (UUID): Primary key
- `symbol` (VARCHAR): Unique ticker symbol (e.g., 'BTC-USD')
- `name` (VARCHAR): Full name of the cryptocurrency
- `current_price` (DECIMAL): Current market price
- `market_cap` (DECIMAL): Market capitalization
- `volume_24h` (DECIMAL): 24-hour trading volume
- `price_change_24h` (DECIMAL): Price change in last 24 hours
- `price_change_percentage_24h` (DECIMAL): Percentage change in last 24 hours
- `price_change_7d` (DECIMAL): Price change in last 7 days
- `price_change_percentage_7d` (DECIMAL): Percentage change in last 7 days
- `all_time_high` (DECIMAL): All-time high price
- `all_time_high_date` (TIMESTAMP): Date of all-time high
- `all_time_low` (DECIMAL): All-time low price
- `all_time_low_date` (TIMESTAMP): Date of all-time low
- `description` (TEXT): Description of the cryptocurrency
- `website_url` (VARCHAR): Official website URL
- `image_url` (VARCHAR): Logo/image URL
- `sentiment_score` (DECIMAL): Overall sentiment score (-1.0 to 1.0)
- `ai_index_value` (DECIMAL): AI-generated investment index
- `last_ai_prediction` (TIMESTAMP): Last prediction timestamp
- `is_active` (BOOLEAN): Whether the coin is actively tracked
- `last_updated` (TIMESTAMP): Last update timestamp
- `created_at` (TIMESTAMP): Record creation timestamp

**Indexes:**
- `idx_coins_symbol`: Index on symbol for fast lookups
- `idx_coins_market_cap`: Index on market cap for sorting
- `idx_coins_volume`: Index on volume for sorting
- `idx_coins_last_updated`: Index on last updated for recent data queries
- `idx_coins_active`: Index on active coins

#### 2. `coin_price_history`
Historical OHLCV (Open, High, Low, Close, Volume) price data and technical indicators.

**Columns:**
- `id` (UUID): Primary key
- `coin_id` (UUID): Foreign key to coins table
- `timestamp` (TIMESTAMP): Data point timestamp
- `open` (DECIMAL): Opening price
- `high` (DECIMAL): Highest price
- `low` (DECIMAL): Lowest price
- `close` (DECIMAL): Closing price
- `volume` (DECIMAL): Trading volume
- `ma_7` (DECIMAL): 7-period moving average
- `ma_25` (DECIMAL): 25-period moving average
- `ma_99` (DECIMAL): 99-period moving average
- `ema_12` (DECIMAL): 12-period exponential moving average
- `ema_26` (DECIMAL): 26-period exponential moving average
- `rsi` (DECIMAL): Relative Strength Index
- `macd` (DECIMAL): MACD indicator
- `macd_signal` (DECIMAL): MACD signal line
- `macd_histogram` (DECIMAL): MACD histogram
- `created_at` (TIMESTAMP): Record creation timestamp

**Indexes:**
- `idx_price_history_coin_id`: Index on coin_id for filtering
- `idx_price_history_timestamp`: Index on timestamp for time-based queries
- `idx_price_history_coin_timestamp`: Composite index for efficient coin history queries

#### 3. `coin_news`
News articles and sentiment analysis for cryptocurrencies.

**Columns:**
- `id` (UUID): Primary key
- `coin_id` (UUID): Foreign key to coins table
- `title` (VARCHAR): News article title
- `content` (TEXT): Article content/summary
- `source` (VARCHAR): News source name
- `url` (VARCHAR): Article URL
- `author` (VARCHAR): Article author
- `sentiment_score` (DECIMAL): Article sentiment score (-1.0 to 1.0)
- `sentiment_label` (VARCHAR): Sentiment label (positive/negative/neutral)
- `published_at` (TIMESTAMP): Publication timestamp
- `created_at` (TIMESTAMP): Record creation timestamp

**Indexes:**
- `idx_news_coin_id`: Index on coin_id for filtering
- `idx_news_published`: Index on publication date
- `idx_news_sentiment`: Index on sentiment score

## Security

### Row Level Security (RLS)

All tables have Row Level Security enabled with the following policies:

**Read Access:**
- Public read access is enabled for all tables (anyone can query data)

**Write Access:**
- Insert/Update operations require authentication
- Only authenticated users or service role can write data
- This protects the database from unauthorized modifications while allowing public read access

## Migrations

Migrations are stored in the `migrations/` directory with timestamps:

- `20251210210000_create_coins_schema.sql`: Initial schema creation

## Usage

### Running Migrations

```bash
# Apply all migrations
supabase db push

# Reset database (drops all data and reapplies migrations)
supabase db reset
```

### Local Development

```bash
# Start local Supabase
supabase start

# Stop local Supabase
supabase stop
```

### Connecting to the Database

Use the Supabase client library or direct PostgreSQL connection:

```python
from supabase import create_client, Client

url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_KEY"
supabase: Client = create_client(url, key)

# Query coins
response = supabase.table('coins').select("*").execute()
```

## Configuration

The `config.toml` file contains Supabase project configuration including:
- API settings
- Database settings
- Authentication settings
- Storage settings

## Sample Data

The initial migration includes sample data for 5 major cryptocurrencies:
- Bitcoin (BTC-USD)
- Ethereum (ETH-USD)
- Binance Coin (BNB-USD)
- Cardano (ADA-USD)
- Solana (SOL-USD)

## Future Enhancements

Potential schema improvements:
- Add portfolio tracking tables
- Add user watchlists
- Add price alerts table
- Add trading signals table
- Add social media sentiment data
- Add exchange-specific data
