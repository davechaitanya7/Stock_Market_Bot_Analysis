"""Futures & Options endpoints - Option chain, live streaming, F&O orders."""
import asyncio
import json
from typing import Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from datetime import datetime

from data.fno_data import get_option_chain, get_expiry_dates, calculate_greeks, get_futures_symbol
from data.live_provider import get_live_price, FNO_INDICES, stream_prices, active_connections, connection_symbols

router = APIRouter(prefix="/api/fno", tags=["Futures & Options"])


@router.get("/option-chain")
async def get_option_chain_endpoint(
    underlying: str = Query(..., description="Underlying symbol (e.g., NIFTY, BANKNIFTY)"),
    expiry: Optional[str] = Query(None, description="Expiry date (YYYY-MM-DD)"),
):
    """
    Get option chain for an underlying.

    Returns all strikes with CE/PE data: LTP, OI, volume, IV.
    """
    if not expiry:
        # Get nearest expiry
        expiries = get_expiry_dates(underlying, count=1)
        expiry = expiries[0]

    chain = await get_option_chain(underlying, expiry)
    return chain


@router.get("/expiry-dates")
async def get_expiry_dates_endpoint(
    underlying: str = Query(..., description="Underlying symbol"),
    count: int = Query(5, description="Number of expiries to return"),
):
    """Get upcoming expiry dates for an underlying."""
    return get_expiry_dates(underlying, count)


@router.get("/futures/symbol")
async def get_futures_symbol_endpoint(
    underlying: str = Query(..., description="Underlying symbol"),
    expiry_month: int = Query(0, description="0=current, 1=next, 2=far"),
):
    """Get futures symbol for underlying."""
    return {
        "symbol": get_futures_symbol(underlying, expiry_month),
        "underlying": underlying.upper(),
        "expiry_month": expiry_month,
    }


@router.get("/futures/data")
async def get_futures_data(
    symbol: str = Query(..., description="Futures symbol"),
):
    """Get futures price data."""
    data = await get_live_price(symbol)
    return data


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live price streaming.

    Client sends: {"action": "subscribe", "symbols": ["NIFTY", "RELIANCE.NS"]}
    Server sends: {"symbol": "NIFTY", "ltp": 22150.50, "change": 125.30, ...}
    """
    await websocket.accept()
    active_connections.add(websocket)
    connection_symbols[websocket] = set()

    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "subscribe":
                symbols = message.get("symbols", [])
                connection_symbols[websocket] = set(symbols)
                await websocket.send_json({
                    "type": "subscribed",
                    "symbols": symbols,
                })

            elif message.get("action") == "unsubscribe":
                connection_symbols[websocket] = set()
                await websocket.send_json({
                    "type": "unsubscribed",
                })

    except WebSocketDisconnect:
        active_connections.discard(websocket)
        connection_symbols.pop(websocket, None)
    except Exception as e:
        active_connections.discard(websocket)
        connection_symbols.pop(websocket, None)


@router.get("/instruments")
async def get_fno_instruments():
    """Get list of F&O tradable instruments."""
    return {
        "indices": list(FNO_INDICES.keys()),
        "stocks": [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
            "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
            "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TATAMOTORS",
            "TITAN", "SUNPHARMA", "BAJFINANCE", "WIPRO", "ULTRACEMCO",
        ],
        "products": ["MIS", "CNC", "NRML"],
        "order_types": ["MARKET", "LIMIT", "SL", "SLM"],
    }


@router.post("/greeks")
async def calculate_option_greeks(
    underlying_price: float,
    strike: float,
    expiry_days: int,
    option_type: str,
    ltp: float,
):
    """
    Calculate option Greeks using Black-Scholes model.

    - underlying_price: Current price of underlying
    - strike: Option strike price
    - expiry_days: Days to expiry
    - option_type: "CE" or "PE"
    - ltp: Option last traded price
    """
    greeks = calculate_greeks(
        underlying_price=underlying_price,
        strike=strike,
        expiry_days=expiry_days,
        option_type=option_type,
        ltp=ltp,
    )
    return greeks


# Background task for broadcasting live prices
async def broadcast_live_prices():
    """Broadcast live prices to all connected WebSocket clients."""
    while True:
        # Get all subscribed symbols
        all_symbols = set()
        for symbols in connection_symbols.values():
            all_symbols.update(symbols)

        if all_symbols and active_connections:
            for symbol in all_symbols:
                # Map index symbol to yahoo symbol
                yahoo_symbol = FNO_INDICES.get(symbol.upper(), f"{symbol}.NS")
                data = await get_live_price(yahoo_symbol)

                if "error" not in data:
                    # Broadcast to all connections subscribed to this symbol
                    for conn in list(active_connections):
                        if symbol in connection_symbols.get(conn, set()):
                            try:
                                await conn.send_json(data)
                            except:
                                pass  # Connection closed

        await asyncio.sleep(5)  # Update every 5 seconds
