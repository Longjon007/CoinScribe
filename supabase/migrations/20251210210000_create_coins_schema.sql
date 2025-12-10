-- Create coins table
-- This table stores cryptocurrency market data and metadata for the CoinScribe application

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create coins table
CREATE TABLE IF NOT EXISTS public.coins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    
    -- Current market data
    current_price DECIMAL(20, 8),
    market_cap DECIMAL(30, 2),
    volume_24h DECIMAL(30, 2),
    
    -- Price change data
    price_change_24h DECIMAL(20, 8),
    price_change_percentage_24h DECIMAL(10, 4),
    price_change_7d DECIMAL(20, 8),
    price_change_percentage_7d DECIMAL(10, 4),
    
    -- Historical high/low
    all_time_high DECIMAL(20, 8),
    all_time_high_date TIMESTAMP WITH TIME ZONE,
    all_time_low DECIMAL(20, 8),
    all_time_low_date TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    description TEXT,
    website_url VARCHAR(500),
    image_url VARCHAR(500),
    
    -- Sentiment and AI data
    sentiment_score DECIMAL(5, 4) DEFAULT 0.0,
    ai_index_value DECIMAL(10, 4),
    last_ai_prediction TIMESTAMP WITH TIME ZONE,
    
    -- Tracking fields
    is_active BOOLEAN DEFAULT true,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_price CHECK (current_price >= 0),
    CONSTRAINT positive_market_cap CHECK (market_cap >= 0),
    CONSTRAINT positive_volume CHECK (volume_24h >= 0),
    CONSTRAINT valid_sentiment CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_coins_symbol ON public.coins(symbol);
CREATE INDEX IF NOT EXISTS idx_coins_market_cap ON public.coins(market_cap DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_coins_volume ON public.coins(volume_24h DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_coins_last_updated ON public.coins(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_coins_active ON public.coins(is_active) WHERE is_active = true;

-- Create historical price data table
CREATE TABLE IF NOT EXISTS public.coin_price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES public.coins(id) ON DELETE CASCADE,
    
    -- OHLCV data
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(30, 2) NOT NULL,
    
    -- Technical indicators
    ma_7 DECIMAL(20, 8),
    ma_25 DECIMAL(20, 8),
    ma_99 DECIMAL(20, 8),
    ema_12 DECIMAL(20, 8),
    ema_26 DECIMAL(20, 8),
    rsi DECIMAL(5, 2),
    macd DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_ohlc CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT valid_high_low CHECK (high >= low),
    CONSTRAINT valid_open CHECK (open BETWEEN low AND high),
    CONSTRAINT valid_close CHECK (close BETWEEN low AND high),
    CONSTRAINT valid_rsi CHECK (rsi IS NULL OR (rsi >= 0 AND rsi <= 100)),
    CONSTRAINT positive_volume_history CHECK (volume >= 0),
    CONSTRAINT unique_coin_timestamp UNIQUE (coin_id, timestamp)
);

-- Create indexes for historical data
CREATE INDEX IF NOT EXISTS idx_price_history_coin_id ON public.coin_price_history(coin_id);
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON public.coin_price_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_coin_timestamp ON public.coin_price_history(coin_id, timestamp DESC);

-- Create news and sentiment table
CREATE TABLE IF NOT EXISTS public.coin_news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES public.coins(id) ON DELETE CASCADE,
    
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source VARCHAR(200),
    url VARCHAR(1000),
    author VARCHAR(200),
    
    sentiment_score DECIMAL(5, 4),
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_news_sentiment CHECK (sentiment_score IS NULL OR (sentiment_score >= -1.0 AND sentiment_score <= 1.0)),
    CONSTRAINT valid_url CHECK (url IS NULL OR url ~ '^https?://.*')
);

-- Create indexes for news data
CREATE INDEX IF NOT EXISTS idx_news_coin_id ON public.coin_news(coin_id);
CREATE INDEX IF NOT EXISTS idx_news_published ON public.coin_news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_sentiment ON public.coin_news(sentiment_score DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.coins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coin_price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coin_news ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Enable read access for all users" ON public.coins
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON public.coin_price_history
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON public.coin_news
    FOR SELECT USING (true);

-- Create policies for authenticated write access (for API/admin operations)
CREATE POLICY "Enable insert for authenticated users only" ON public.coins
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable update for authenticated users only" ON public.coins
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable insert for authenticated users only" ON public.coin_price_history
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable update for authenticated users only" ON public.coin_price_history
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable insert for authenticated users only" ON public.coin_news
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable update for authenticated users only" ON public.coin_news
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- Create function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER update_coins_updated_at
    BEFORE UPDATE ON public.coins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO public.coins (symbol, name, description) VALUES
    ('BTC-USD', 'Bitcoin', 'Bitcoin is a decentralized cryptocurrency originally described in a 2008 whitepaper by a person, or group of people, using the alias Satoshi Nakamoto.'),
    ('ETH-USD', 'Ethereum', 'Ethereum is a decentralized open-source blockchain system that features its own cryptocurrency, Ether.'),
    ('BNB-USD', 'Binance Coin', 'Binance Coin is the cryptocurrency issued by Binance exchange and trades with the BNB symbol.'),
    ('ADA-USD', 'Cardano', 'Cardano is a public blockchain platform. It is open-source and decentralized, with consensus achieved using proof of stake.'),
    ('SOL-USD', 'Solana', 'Solana is a high-performance cryptocurrency blockchain which supports smart contracts and decentralized applications.')
ON CONFLICT (symbol) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE public.coins IS 'Main table for storing cryptocurrency metadata and current market data';
COMMENT ON TABLE public.coin_price_history IS 'Historical OHLCV price data and technical indicators for coins';
COMMENT ON TABLE public.coin_news IS 'News articles and sentiment analysis for coins';
COMMENT ON COLUMN public.coins.sentiment_score IS 'Overall sentiment score from -1.0 (very negative) to 1.0 (very positive)';
COMMENT ON COLUMN public.coins.ai_index_value IS 'AI-generated investment index value';
