import { useState, useEffect, useMemo } from 'react'
import CoinCard from './components/CoinCard'
import './App.css'

interface Coin {
  id: string
  symbol: string
  name: string
  current_price: number
  price_change_percentage_24h: number
}

function App() {
  const [coins, setCoins] = useState<Coin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const abortController = new AbortController()
    
    // This is a placeholder - in production, you would fetch from your Netlify function
    // that connects to CoinGecko or similar crypto API
    const fetchCoins = async () => {
      try {
        // Simulate API call - replace with actual fetch in production
        // When implementing real API: const response = await fetch(url, { signal: abortController.signal })
        const mockCoins: Coin[] = [
          { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', current_price: 45000, price_change_percentage_24h: 2.5 },
          { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', current_price: 3000, price_change_percentage_24h: -1.2 },
          { id: 'cardano', symbol: 'ADA', name: 'Cardano', current_price: 0.5, price_change_percentage_24h: 5.7 },
        ]
        
        // Only update state if not aborted
        if (!abortController.signal.aborted) {
          setCoins(mockCoins)
          setLoading(false)
        }
      } catch (err) {
        // Only update state if not aborted
        if (!abortController.signal.aborted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch coins')
          setLoading(false)
        }
      }
    }

    fetchCoins()
    
    // Cleanup function to abort fetch on unmount
    return () => {
      abortController.abort()
    }
  }, [])

  // Memoize formatted coin data to avoid recalculating on every render
  const formattedCoins = useMemo(() => {
    return coins.map((coin) => ({
      ...coin,
      formattedPrice: coin.current_price.toLocaleString(),
      formattedChange: coin.price_change_percentage_24h.toFixed(2),
      isPositive: coin.price_change_percentage_24h >= 0,
      upperSymbol: coin.symbol.toUpperCase()
    }))
  }, [coins])

  if (loading) return <div className="loading">Loading crypto data...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="app">
      <header className="header">
        <h1>CoinScribe</h1>
        <p>Crypto tracker with AI-powered news summarization</p>
      </header>

      <main className="main">
        <div className="coin-list">
          {formattedCoins.map((coin) => (
            <CoinCard
              key={coin.id}
              name={coin.name}
              upperSymbol={coin.upperSymbol}
              formattedPrice={coin.formattedPrice}
              formattedChange={coin.formattedChange}
              isPositive={coin.isPositive}
            />
          ))}
        </div>
      </main>

      <footer className="footer">
        <p>Powered by Netlify | Data refreshes every 60 seconds</p>
      </footer>
    </div>
  )
}

export default App
