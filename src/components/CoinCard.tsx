import { memo } from 'react'

interface CoinCardProps {
  name: string
  upperSymbol: string
  formattedPrice: string
  formattedChange: string
  isPositive: boolean
}

// Memoized component to prevent unnecessary re-renders
const CoinCard = memo(({ name, upperSymbol, formattedPrice, formattedChange, isPositive }: CoinCardProps) => {
  return (
    <div className="coin-card">
      <div className="coin-info">
        <h2>{name}</h2>
        <span className="symbol">{upperSymbol}</span>
      </div>
      <div className="coin-price">
        <span className="price">${formattedPrice}</span>
        <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '+' : ''}
          {formattedChange}%
        </span>
      </div>
    </div>
  )
})

CoinCard.displayName = 'CoinCard'

export default CoinCard
