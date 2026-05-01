"""Live market data provider with WebSocket support."""
import asyncio
from datetime import datetime
from typing import Dict, Set, Any
import yfinance as yf

# Active WebSocket connections
active_connections: Set[Any] = set()

# Subscribed symbols per connection
connection_symbols: Dict[Any, Set[str]] = {}

# F&O Instruments - Indian market
FNO_INDICES = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTYFIN.NS",
    "MIDCPNIFTY": "NIFTYMDCP.NS",
    "SENSEX": "^BSESN",
}

# F&O Stocks (top 50 by volume)
FNO_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TATAMOTORS.NS",
    "TITAN.NS", "SUNPHARMA.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS",
    "TATASTEEL.NS", "ADANIENT.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS",
    "JSWSTEEL.NS", "TATACONSUM.NS", "ADANIPORTS.NS", "BPCL.NS", "BRITANNIA.NS",
    "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "INDUSINDBK.NS", "M&M.NS", "NESTLEIND.NS",
    "NTPC.NS", "POWERGRID.NS", "SHRIRAMFIN.NS", "TECHM.NS", "TATASTEEL.NS",
    "UPL.NS", "ZEEL.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "SBILIFE.NS",
]


async def get_live_price(symbol: str) -> Dict[str, Any]:
    """Get latest price for a symbol (simulated live via yfinance)."""
    try:
        ticker = yf.Ticker(symbol)
        # Get fast price
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return {"error": "No data", "symbol": symbol}

        latest = data.iloc[-1]
        prev_close = data.iloc[-2]["Close"] if len(data) > 1 else latest["Close"]
        current_price = round(latest["Close"], 2)
        change = round(current_price - prev_close, 2)
        change_percent = round((change / prev_close) * 100, 2) if prev_close else 0

        return {
            "symbol": symbol,
            "ltp": current_price,
            "change": change,
            "change_percent": change_percent,
            "high": round(latest["High"], 2),
            "low": round(latest["Low"], 2),
            "volume": int(latest["Volume"]) if latest["Volume"] > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


async def stream_prices(symbols: list, callback):
    """Stream live prices for symbols."""
    while True:
        for symbol in symbols:
            data = await get_live_price(symbol)
            if "error" not in data:
                await callback(data)
        await asyncio.sleep(5)  # Update every 5 seconds


def get_fno_symbol(underlying: str, expiry: str, strike: float, option_type: str) -> str:
    """
    Generate F&O symbol string.

    Example: NIFTY 24MAY 22000 CE -> NIFTY24052222000CE
    """
    # Map month to number
    months = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }

    # Parse expiry: "24MAY" -> "2405"
    expiry_year = expiry[:2]
    expiry_month = months.get(expiry[2:5].upper(), "01")

    symbol = f"{underlying}{expiry_year}{expiry_month}{strike}{option_type}"
    return symbol.upper()
