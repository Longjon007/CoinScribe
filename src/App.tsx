import { useState, useEffect } from 'react'
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
    // This is a placeholder - in production, you would fetch from your Netlify function
    // that connects to CoinGecko or similar crypto API
    const mockCoins: Coin[] = [
      { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', current_price: 45000, price_change_percentage_24h: 2.5 },
      { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', current_price: 3000, price_change_percentage_24h: -1.2 },
      { id: 'cardano', symbol: 'ADA', name: 'Cardano', current_price: 0.5, price_change_percentage_24h: 5.7 },
    ]

    setTimeout(() => {
      setCoins(mockCoins)
      setLoading(false)
    }, 1000)
  }, [])

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
          {coins.map((coin) => (
            <div key={coin.id} className="coin-card">
              <div className="coin-info">
                <h2>{coin.name}</h2>
                <span className="symbol">{coin.symbol.toUpperCase()}</span>
              </div>
              <div className="coin-price">
                <span className="price">${coin.current_price.toLocaleString()}</span>
                <span className={`change ${coin.price_change_percentage_24h >= 0 ? 'positive' : 'negative'}`}>
                  {coin.price_change_percentage_24h >= 0 ? '+' : ''}
                  {coin.price_change_percentage_24h.toFixed(2)}%
                </span>
              </div>
            </div>
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
