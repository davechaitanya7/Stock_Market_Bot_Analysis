# Stock Trading Bot

AI-powered stock analysis and trading bot for Indian markets (NSE/BSE).

## Features

- Real-time stock data from Yahoo Finance (free)
- 15+ technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
- AI-powered trading signals with confidence scores
- Manual order approval workflow
- Watchlist management
- Market indices dashboard

## Tech Stack

**Backend:**
- Python + FastAPI
- yfinance (free stock data)
- pandas-ta (technical analysis)
- Rule-based AI analysis engine

**Frontend:**
- React + Vite
- Tailwind CSS
- Recharts (charting)

## Quick Start

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

Frontend will run at: http://localhost:5173

## Usage

1. **Search for stocks**: Type company name or symbol (e.g., "RELIANCE", "TCS", "TATAMOTORS")
2. **View analysis**: Click on a stock to see chart and AI analysis
3. **Place order**: Click "Trade" button, select BUY/SELL, quantity, and submit
4. **Approve orders**: Pending orders appear in the side panel - approve or reject
5. **Watchlist**: Add stocks to watchlist for quick access

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stocks/search?q=...` | Search stocks |
| `GET /api/stocks/{symbol}/data` | Get stock price data |
| `GET /api/stocks/{symbol}/analysis` | Get AI analysis |
| `GET /api/market/indices` | Get market indices |
| `POST /api/orders` | Create order |
| `GET /api/orders` | List orders |
| `POST /api/orders/{id}/approve` | Approve order |
| `POST /api/orders/{id}/reject` | Reject order |
| `GET /api/watchlist` | Get watchlist |
| `POST /api/watchlist/{symbol}` | Add to watchlist |

## Trading Signals

The AI generates signals based on multiple technical indicators:

| Signal | Meaning |
|--------|---------|
| STRONG_BUY | Multiple bullish indicators, high confidence |
| BUY | Bullish bias |
| WEAK_BUY | Slight bullish bias |
| NEUTRAL | Mixed signals |
| WEAK_SELL | Slight bearish bias |
| SELL | Bearish bias |
| STRONG_SELL | Multiple bearish indicators, high confidence |

## Indicators Used

- **RSI (14)**: Relative Strength Index - oversold/overbought
- **MACD**: Moving Average Convergence Divergence - trend momentum
- **SMA 20/50/200**: Simple Moving Averages - trend direction
- **EMA 12/26**: Exponential Moving Averages - faster trend
- **Bollinger Bands**: Volatility bands
- **Stochastic**: Momentum indicator
- **ATR**: Average True Range - volatility

## Disclaimer

This is for **educational and paper trading purposes only**. The analysis is based on historical data and technical indicators. Past performance does not guarantee future results. Always do your own research before making investment decisions.

## Data Sources

- Stock data: Yahoo Finance (free, delayed)
- Indian stocks: NSE/BSE via yfinance (.NS for NSE, .BO for BSE)

## License

MIT
