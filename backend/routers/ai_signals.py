"""AI Trading Signals endpoint."""
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from datetime import datetime

from data.fetcher import get_stock_data
from analysis.indicators import calculate_indicators, get_indicator_signals
from analysis.ai_engine import ai_engine
from models.schemas import AnalysisResponse, TradingSignal

router = APIRouter(prefix="/api/ai", tags=["AI Signals"])


@router.get("/signal/{symbol}")
async def get_ai_signal(
    symbol: str,
    period: str = Query("3mo", description="Data period for analysis"),
):
    """
    Get AI-powered trading signal for a symbol.

    Combines technical indicators, pattern recognition, and trend analysis.
    """
    # Fetch stock data
    data = get_stock_data(symbol, period=period, interval="1d")
    if not data:
        raise HTTPException(status_code=404, detail="Stock data not found")

    # Convert to DataFrame
    df = pd.DataFrame(data["historical_data"])
    if df.empty:
        raise HTTPException(status_code=400, detail="Insufficient data")

    df["Date"] = pd.to_datetime(df["date"])
    df.set_index("Date", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]

    # Calculate indicators
    df = calculate_indicators(df)
    indicators = get_indicator_signals(df)

    # Generate AI signal
    ai_signal = ai_engine.generate_signal(df, indicators)

    return {
        "symbol": symbol,
        "name": data["name"],
        "current_price": data["current_price"],
        "ai_signal": ai_signal,
        "technical_indicators": indicators,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/scanner")
async def scan_market(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
):
    """
    Scan multiple symbols and return top picks.

    Returns symbols sorted by AI signal strength.
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    results = []

    for symbol in symbol_list:
        try:
            data = get_stock_data(symbol, period="1mo", interval="1d")
            if not data:
                continue

            df = pd.DataFrame(data["historical_data"])
            if len(df) < 20:
                continue

            df["Date"] = pd.to_datetime(df["date"])
            df.set_index("Date", inplace=True)
            df = df[["open", "high", "low", "close", "volume"]]
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            df = calculate_indicators(df)
            indicators = get_indicator_signals(df)
            ai_signal = ai_engine.generate_signal(df, indicators)

            results.append({
                "symbol": symbol,
                "name": data["name"],
                "price": data["current_price"],
                "signal": ai_signal["signal"],
                "confidence": ai_signal["confidence"],
                "trend": ai_signal["trend"],
            })
        except Exception:
            continue

    # Sort by signal strength
    signal_order = {"STRONG_BUY": 5, "BUY": 4, "HOLD": 3, "SELL": 2, "STRONG_SELL": 1}
    results.sort(key=lambda x: (signal_order.get(x["signal"], 3), x["confidence"]), reverse=True)

    return {"scans": results, "timestamp": datetime.now().isoformat()}


@router.get("/patterns/{symbol}")
async def detect_patterns(symbol: str):
    """Detect candlestick patterns for a symbol."""
    data = get_stock_data(symbol, period="6mo", interval="1d")
    if not data:
        raise HTTPException(status_code=404, detail="Stock data not found")

    df = pd.DataFrame(data["historical_data"])
    df["Date"] = pd.to_datetime(df["date"])
    df.set_index("Date", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]

    patterns = ai_engine._scan_patterns(df)

    return {
        "symbol": symbol,
        "patterns": patterns,
        "timestamp": datetime.now().isoformat(),
    }
