# CoinScribe AI Model API Documentation

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Response Format

All responses are in JSON format with the following structure:

**Success Response:**
```json
{
  "data": {...},
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "status": "error",
  "traceback": "..." // Only in debug mode
}
```

## Endpoints

### 1. Health Check

Check if the API server is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "0.1.0"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 2. Get Model Information

Retrieve information about the loaded AI model.

**Endpoint:** `GET /api/model/info`

**Response:**
```json
{
  "model_path": "ai_model/models/checkpoints/best_model.pth",
  "device": "cuda",
  "architecture": "lstm",
  "input_features": 32,
  "hidden_size": 128,
  "num_layers": 2,
  "output_size": 10,
  "model_exists": true
}
```

**Example:**
```bash
curl http://localhost:5000/api/model/info
```

---

### 3. Predict Investment Indices

Generate AI-powered investment index predictions based on market data.

**Endpoint:** `POST /api/predict/indices`

**Request Body:**
```json
{
  "symbols": ["BTC-USD", "ETH-USD"],  // Optional, uses config default if not provided
  "period": "1mo",                     // Optional, default: "1y"
  "interval": "1h"                     // Optional, default: "1h"
}
```

**Parameters:**
- `symbols` (array, optional): List of cryptocurrency symbols in Yahoo Finance format
- `period` (string, optional): Historical data period
  - Valid values: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
- `interval` (string, optional): Data interval
  - Valid values: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"

**Response:**
```json
{
  "indices": [0.75, 0.82, 0.68, 0.91, 0.77, 0.85, 0.73, 0.88, 0.79, 0.84],
  "index_names": [
    "Index_1", "Index_2", "Index_3", "Index_4", "Index_5",
    "Index_6", "Index_7", "Index_8", "Index_9", "Index_10"
  ],
  "confidence": 0.85,
  "symbols": ["BTC-USD", "ETH-USD"],
  "timestamp": "2024-01-01T12:00:00",
  "model_path": "ai_model/models/checkpoints/best_model.pth"
}
```

**Response Fields:**
- `indices`: Array of predicted index values (0-1 scale)
- `index_names`: Names of the indices
- `confidence`: Confidence score for the prediction (0-1)
- `symbols`: Symbols used for prediction
- `timestamp`: Timestamp of the latest data used
- `model_path`: Path to the model used for prediction

**Example:**
```bash
curl -X POST http://localhost:5000/api/predict/indices \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC-USD", "ETH-USD", "BNB-USD"],
    "period": "1mo",
    "interval": "1h"
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/predict/indices',
    json={
        'symbols': ['BTC-USD', 'ETH-USD'],
        'period': '1mo',
        'interval': '1h'
    }
)

result = response.json()
print(f"Predicted Indices: {result['indices']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

### 4. Fetch Market Data

Retrieve historical market data for specified cryptocurrency symbols.

**Endpoint:** `POST /api/data/fetch`

**Request Body:**
```json
{
  "symbols": ["BTC-USD", "ETH-USD"],
  "period": "1mo",
  "interval": "1d"
}
```

**Parameters:**
- `symbols` (array, required): List of cryptocurrency symbols
- `period` (string, optional): Historical data period
- `interval` (string, optional): Data interval

**Response:**
```json
{
  "data": [
    {
      "Datetime": "2024-01-01T00:00:00",
      "Open": 42000.0,
      "High": 42500.0,
      "Low": 41800.0,
      "Close": 42300.0,
      "Volume": 1234567890,
      "symbol": "BTC-USD"
    },
    ...
  ],
  "count": 30,
  "symbols": ["BTC-USD", "ETH-USD"],
  "columns": ["Datetime", "Open", "High", "Low", "Close", "Volume", "symbol"]
}
```

**Response Fields:**
- `data`: Array of data records
- `count`: Number of records returned
- `symbols`: Symbols queried
- `columns`: List of data columns

**Example:**
```bash
curl -X POST http://localhost:5000/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC-USD"],
    "period": "1mo",
    "interval": "1d"
  }'
```

---

### 5. List Available Indices

Get a list of all available AI investment indices.

**Endpoint:** `GET /api/indices/list`

**Response:**
```json
{
  "indices": [
    {
      "name": "Index_1",
      "description": "AI-generated investment index 1",
      "type": "composite"
    },
    {
      "name": "Index_2",
      "description": "AI-generated investment index 2",
      "type": "composite"
    },
    ...
  ],
  "count": 10
}
```

**Response Fields:**
- `indices`: Array of index information
- `count`: Number of indices

**Example:**
```bash
curl http://localhost:5000/api/indices/list
```

---

### 6. Get API Configuration

Retrieve current API configuration (non-sensitive information only).

**Endpoint:** `GET /api/config`

**Response:**
```json
{
  "model": {
    "architecture": "lstm",
    "input_features": 32,
    "output_size": 10
  },
  "data": {
    "sequence_length": 60,
    "features": [
      "open", "high", "low", "close", "volume",
      "market_cap", "sentiment_score"
    ]
  },
  "api": {
    "version": "0.1.0"
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/config
```

---

## Error Codes

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Endpoint or resource not found |
| 500 | Internal Server Error - Server error |

## Error Response Examples

**400 Bad Request:**
```json
{
  "error": "Invalid symbol format"
}
```

**404 Not Found:**
```json
{
  "error": "No data retrieved",
  "symbols": ["INVALID-SYMBOL"]
}
```

**500 Internal Server Error:**
```json
{
  "error": "Model not loaded",
  "traceback": "..."
}
```

## Rate Limiting

Currently, there are no rate limits. Consider implementing rate limiting in production environments.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins by default. Modify `cors_origins` in the configuration for production use.

## WebSocket Support

WebSocket support is not currently implemented but is planned for future releases to enable real-time predictions.

## Versioning

The current API version is `0.1.0`. Future versions will maintain backwards compatibility or provide versioned endpoints.

## Best Practices

1. **Batch Requests**: When fetching data for multiple symbols, include them in a single request rather than making multiple requests.

2. **Caching**: Implement client-side caching for prediction results to reduce API calls.

3. **Error Handling**: Always implement proper error handling for API calls.

4. **Timeout**: Set appropriate timeout values for API requests (recommended: 30 seconds).

## Example Integration

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function predictIndices() {
  try {
    const response = await axios.post(
      'http://localhost:5000/api/predict/indices',
      {
        symbols: ['BTC-USD', 'ETH-USD'],
        period: '1mo',
        interval: '1h'
      }
    );
    
    console.log('Indices:', response.data.indices);
    console.log('Confidence:', response.data.confidence);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

predictIndices();
```

### Python

```python
import requests

def predict_indices():
    try:
        response = requests.post(
            'http://localhost:5000/api/predict/indices',
            json={
                'symbols': ['BTC-USD', 'ETH-USD'],
                'period': '1mo',
                'interval': '1h'
            },
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print('Indices:', result['indices'])
        print('Confidence:', result['confidence'])
        
    except requests.exceptions.RequestException as e:
        print('Error:', str(e))

predict_indices()
```

### cURL

```bash
#!/bin/bash

# Predict indices
curl -X POST http://localhost:5000/api/predict/indices \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC-USD", "ETH-USD"],
    "period": "1mo",
    "interval": "1h"
  }' \
  | jq '.'
```

## Testing

Test the API using the provided examples or tools like:
- cURL
- Postman
- Insomnia
- HTTPie

## Support

For API support and questions:
1. Review this documentation
2. Check example scripts in the repository
3. Open an issue on GitHub
