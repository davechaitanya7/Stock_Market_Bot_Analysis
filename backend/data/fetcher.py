import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> Optional[Dict[str, Any]]:
    """
    Fetch stock data from Yahoo Finance.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS" for NSE, "RELIANCE.BO" for BSE)
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

    Returns:
        Dictionary with stock data or None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            return None

        df = df.reset_index()

        # Format data for frontend
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": row["Date"].isoformat() if hasattr(row["Date"], 'isoformat') else str(row["Date"]),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0
            })

        # Get current price (latest close)
        current_price = round(df["Close"].iloc[-1], 2)
        previous_close = round(df["Close"].iloc[-2], 2) if len(df) > 1 else current_price
        change = round(current_price - previous_close, 2)
        change_percent = round((change / previous_close) * 100, 2) if previous_close else 0

        # Get additional info
        info = ticker.info

        return {
            "symbol": symbol,
            "name": info.get("shortName", info.get("longName", symbol)),
            "current_price": current_price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "day_high": round(df["High"].max(), 2),
            "day_low": round(df["Low"].min(), 2),
            "volume": int(df["Volume"].iloc[-1]) if pd.notna(df["Volume"].iloc[-1]) else 0,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "historical_data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def search_stocks(query: str, exchange: str = "NS") -> list:
    """
    Search for stocks by name or symbol.

    Args:
        query: Search query (company name or symbol)
        exchange: "NS" for NSE, "BO" for BSE

    Returns:
        List of matching stocks
    """
    try:
        # Common Indian stocks for search
        indian_stocks = [
            {"symbol": f"RELIANCE.{exchange}", "name": "Reliance Industries", "sector": "Oil & Gas"},
            {"symbol": f"TCS.{exchange}", "name": "Tata Consultancy Services", "sector": "IT"},
            {"symbol": f"HDFCBANK.{exchange}", "name": "HDFC Bank", "sector": "Banking"},
            {"symbol": f"INFY.{exchange}", "name": "Infosys", "sector": "IT"},
            {"symbol": f"ICICIBANK.{exchange}", "name": "ICICI Bank", "sector": "Banking"},
            {"symbol": f"HINDUNILVR.{exchange}", "name": "Hindustan Unilever", "sector": "FMCG"},
            {"symbol": f"SBIN.{exchange}", "name": "State Bank of India", "sector": "Banking"},
            {"symbol": f"BHARTIARTL.{exchange}", "name": "Bharti Airtel", "sector": "Telecom"},
            {"symbol": f"ITC.{exchange}", "name": "ITC Limited", "sector": "FMCG"},
            {"symbol": f"KOTAKBANK.{exchange}", "name": "Kotak Mahindra Bank", "sector": "Banking"},
            {"symbol": f"LT.{exchange}", "name": "Larsen & Toubro", "sector": "Engineering"},
            {"symbol": f"AXISBANK.{exchange}", "name": "Axis Bank", "sector": "Banking"},
            {"symbol": f"ASIANPAINT.{exchange}", "name": "Asian Paints", "sector": "Paints"},
            {"symbol": f"MARUTI.{exchange}", "name": "Maruti Suzuki", "sector": "Auto"},
            {"symbol": f"TATAMOTORS.{exchange}", "name": "Tata Motors", "sector": "Auto"},
            {"symbol": f"TITAN.{exchange}", "name": "Titan Company", "sector": "Consumer"},
            {"symbol": f"SUNPHARMA.{exchange}", "name": "Sun Pharmaceutical", "sector": "Pharma"},
            {"symbol": f"BAJFINANCE.{exchange}", "name": "Bajaj Finance", "sector": "Finance"},
            {"symbol": f"WIPRO.{exchange}", "name": "Wipro", "sector": "IT"},
            {"symbol": f"ULTRACEMCO.{exchange}", "name": "UltraTech Cement", "sector": "Cement"},
            {"symbol": f"TATASTEEL.{exchange}", "name": "Tata Steel", "sector": "Steel"},
            {"symbol": f"ADANIENT.{exchange}", "name": "Adani Enterprises", "sector": "Diversified"},
            {"symbol": f"POWERGRID.{exchange}", "name": "Power Grid Corporation", "sector": "Power"},
            {"symbol": f"NTPC.{exchange}", "name": "NTPC Limited", "sector": "Power"},
            {"symbol": f"ONGC.{exchange}", "name": "Oil & Natural Gas Corp", "sector": "Oil & Gas"},
        ]

        query = query.lower()
        results = [
            stock for stock in indian_stocks
            if query in stock["symbol"].lower() or query in stock["name"].lower()
        ]

        return results[:10]  # Return top 10 results
    except Exception as e:
        print(f"Error searching stocks: {e}")
        return []


def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
    """Get detailed stock information."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "name": info.get("shortName", info.get("longName", symbol)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": info.get("longBusinessSummary", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "eps": info.get("trailingEps"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
        }
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return None
