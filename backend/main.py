from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
import uuid
from datetime import datetime

from data.fetcher import get_stock_data, search_stocks, get_stock_info
from analysis.indicators import calculate_indicators, get_indicator_signals, generate_composite_signal
from models.schemas import (
    StockData, StockSearchResult, AnalysisResponse,
    OrderRequest, Order, PortfolioResponse, PortfolioItem
)

app = FastAPI(
    title="Stock Trading Bot API",
    description="AI-powered stock analysis and trading bot for Indian markets",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
orders_db: List[Order] = []
portfolio_db: List[PortfolioItem] = []
watchlist_db: List[str] = []


@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "ok",
        "message": "Stock Trading Bot API is running",
        "version": "1.0.0"
    }


@app.get("/api/stocks/search", response_model=List[StockSearchResult])
async def search_stock(q: str, exchange: str = "NS"):
    """
    Search for stocks by name or symbol.

    - **q**: Search query (company name or symbol)
    - **exchange**: "NS" for NSE, "BO" for BSE
    """
    results = search_stocks(q, exchange)
    if not results:
        raise HTTPException(status_code=404, detail="No stocks found")
    return results


@app.get("/api/stocks/{symbol}/data", response_model=StockData)
async def get_stock_price_data(symbol: str):
    """
    Get stock price data and historical OHLCV.

    - **symbol**: Stock symbol (e.g., RELIANCE.NS for NSE)
    """
    data = get_stock_data(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return data


@app.get("/api/stocks/{symbol}/info")
async def get_stock_details(symbol: str):
    """
    Get detailed stock information including company details.
    """
    info = get_stock_info(symbol)
    if not info:
        raise HTTPException(status_code=404, detail="Stock info not found")
    return info


@app.get("/api/stocks/{symbol}/analysis", response_model=AnalysisResponse)
async def analyze_stock(symbol: str):
    """
    Get comprehensive technical analysis and AI-powered trading signal.

    This endpoint:
    1. Fetches historical stock data
    2. Calculates 15+ technical indicators
    3. Generates a composite trading signal with confidence score
    """
    # Fetch data
    data = get_stock_data(symbol, period="6mo", interval="1d")
    if not data:
        raise HTTPException(status_code=404, detail="Stock data not found")

    # Convert to DataFrame for analysis
    df = pd.DataFrame(data["historical_data"])
    df["Date"] = pd.to_datetime(df["date"])
    df.set_index("Date", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]

    # Calculate indicators
    df = calculate_indicators(df)

    # Get signals
    indicator_signals = get_indicator_signals(df)
    trading_signal = generate_composite_signal(indicator_signals)

    return AnalysisResponse(
        symbol=symbol,
        name=data["name"],
        current_price=data["current_price"],
        timestamp=datetime.now().isoformat(),
        technical_indicators=indicator_signals,
        trading_signal=trading_signal
    )


@app.post("/api/orders", response_model=Order)
async def create_order(order: OrderRequest):
    """
    Create a new trading order (requires manual approval).

    The order is created in PENDING status and must be approved before execution.
    """
    order_id = str(uuid.uuid4())[:8]

    new_order = Order(
        id=order_id,
        symbol=order.symbol,
        action=order.action,
        quantity=order.quantity,
        order_type=order.order_type,
        price=order.price,
        stop_loss=order.stop_loss,
        target=order.target,
        status="PENDING",
        created_at=datetime.now().isoformat()
    )

    orders_db.append(new_order)
    return new_order


@app.get("/api/orders", response_model=List[Order])
async def list_orders(status: Optional[str] = None):
    """
    List all orders, optionally filtered by status.
    """
    if status:
        return [o for o in orders_db if o.status == status]
    return orders_db


@app.post("/api/orders/{order_id}/approve")
async def approve_order(order_id: str):
    """
    Approve a pending order for execution.
    """
    for order in orders_db:
        if order.id == order_id:
            if order.status != "PENDING":
                raise HTTPException(status_code=400, detail="Order not in PENDING status")
            order.status = "APPROVED"
            order.approved_at = datetime.now().isoformat()
            return {"status": "approved", "order_id": order_id}

    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/api/orders/{order_id}/reject")
async def reject_order(order_id: str):
    """
    Reject a pending order.
    """
    for order in orders_db:
        if order.id == order_id:
            order.status = "REJECTED"
            return {"status": "rejected", "order_id": order_id}

    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    """
    Get current portfolio holdings and P/L.
    """
    total_invested = sum(h.invested_value for h in portfolio_db)
    total_current = sum(h.current_value for h in portfolio_db)
    total_pnl = total_current - total_invested
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    return PortfolioResponse(
        total_invested=round(total_invested, 2),
        total_current_value=round(total_current, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_percent=round(total_pnl_percent, 2),
        holdings=portfolio_db
    )


@app.post("/api/portfolio/simulate")
async def simulate_trade(order: OrderRequest):
    """
    Simulate a trade without actually executing it.

    Useful for testing strategies with paper trading.
    """
    # Get current price
    data = get_stock_data(order.symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")

    current_price = data["current_price"]

    # Calculate simulated P/L
    if order.action == "BUY":
        simulated_value = order.quantity * current_price
        return {
            "action": "BUY",
            "quantity": order.quantity,
            "price": current_price,
            "total_value": round(simulated_value, 2),
            "message": f"Simulated BUY: {order.quantity} shares of {order.symbol} at ₹{current_price}"
        }
    else:
        # Find existing holding
        holding = next((h for h in portfolio_db if h.symbol == order.symbol), None)
        if not holding:
            raise HTTPException(status_code=400, detail="No holding to sell")

        pnl = (current_price - holding.avg_price) * order.quantity
        pnl_percent = (pnl / (holding.avg_price * order.quantity)) * 100

        return {
            "action": "SELL",
            "quantity": order.quantity,
            "price": current_price,
            "avg_price": holding.avg_price,
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "message": f"Simulated SELL: {order.quantity} shares of {order.symbol} at ₹{current_price}"
        }


@app.get("/api/watchlist", response_model=List[str])
async def get_watchlist():
    """Get user's watchlist."""
    return watchlist_db


@app.post("/api/watchlist/{symbol}")
async def add_to_watchlist(symbol: str):
    """Add a stock to watchlist."""
    if symbol not in watchlist_db:
        watchlist_db.append(symbol)
    return {"watchlist": watchlist_db}


@app.delete("/api/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Remove a stock from watchlist."""
    if symbol in watchlist_db:
        watchlist_db.remove(symbol)
    return {"watchlist": watchlist_db}


@app.get("/api/market/indices")
async def get_market_indices():
    """
    Get major Indian market indices.
    """
    indices = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY NEXT 50": "^NSMIDCP",
        "SENSEX": "^BSESN",
        "NIFTY IT": "^CNXIT"
    }

    results = {}
    for name, symbol in indices.items():
        data = get_stock_data(symbol, period="1d", interval="5m")
        if data:
            results[name] = {
                "symbol": symbol,
                "value": data["current_price"],
                "change": data["change"],
                "change_percent": data["change_percent"]
            }

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
