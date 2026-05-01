# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

**Backend** (`backend/`) - FastAPI application with modular architecture:
- `main.py` - All API endpoints, in-memory storage for orders/portfolio/watchlist
- `data/fetcher.py` - Yahoo Finance integration via yfinance, hardcoded Indian stock search
- `analysis/indicators.py` - Technical analysis engine using pandas-ta (RSI, MACD, Bollinger Bands, etc.)
- `models/schemas.py` - Pydantic models for request/response validation

**Frontend** (`frontend/`) - React + Vite single-page application:
- `src/App.jsx` - All components in single file (MarketIndices, StockChart, AnalysisPanel, OrderForm, OrdersPanel, Watchlist)
- `src/api/client.js` - API client with fetch wrappers for all backend endpoints

**Data Flow:**
1. Frontend fetches market indices on mount
2. User searches stock → `search_stocks()` in fetcher.py returns hardcoded Indian stocks
3. User selects stock → `get_stock_data()` fetches OHLCV from yfinance
4. `calculate_indicators()` computes 15+ indicators via pandas-ta
5. `generate_composite_signal()` aggregates indicator signals into trading recommendation
6. Orders flow: Create (PENDING) → Approve/Reject → (optionally) Execute

## Commands

```bash
# Backend - install and run
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend - install and run
cd frontend
npm install
npm run dev

# Test API
curl http://localhost:8000/api/stocks/search?q=RELIANCE
curl http://localhost:8000/api/stocks/RELIANCE.NS/analysis
```

## Key Conventions

- **Stock symbols:** NSE uses `.NS` suffix, BSE uses `.BO` (e.g., `RELIANCE.NS`, `TATAMOTORS.BO`)
- **In-memory storage:** `orders_db`, `portfolio_db`, `watchlist_db` in main.py - not persistent
- **Signal generation:** Composite signal weights multiple indicators (RSI, MACD, MAs, Bollinger Bands, Stochastic)
- **Order workflow:** All orders require manual approval before execution

## Extending

- **New indicators:** Add to `calculate_indicators()` in indicators.py, add signal logic in `get_indicator_signals()`
- **New endpoints:** Add route in main.py, define Pydantic models in schemas.py
- **New components:** Extract from App.jsx into `src/components/` when complexity grows
