"""Futures & Options data - Option chain, Greeks, OI analysis."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import random


# Predefined expiry dates (weekly for NIFTY, BANKNIFTY)
def get_expiry_dates(underlying: str, count: int = 5) -> List[str]:
    """Get upcoming expiry dates for an underlying."""
    expiries = []
    today = datetime.now()

    # Weekly expiries (Thursday for NIFTY, BANKNIFTY)
    for i in range(count):
        # Find next Thursday
        days_until_thursday = (3 - today.weekday()) % 7
        if days_until_thursday == 0 and today.hour >= 15:  # After market hours
            days_until_thursday = 7
        expiry = today + timedelta(days=days_until_thursday + (i * 7))
        expiries.append(expiry.strftime("%Y-%m-%d"))

    return expiries


def get_strike_range(underlying_ltp: float, underlying: str) -> List[float]:
    """Get strike price range around LTP."""
    # Define strike gap based on underlying
    strike_gaps = {
        "NIFTY": 50,
        "BANKNIFTY": 100,
        "FINNIFTY": 50,
        "SENSEX": 100,
    }
    gap = strike_gaps.get(upper(underlying), 100)

    # Generate strikes: 10 ITM, ATM, 10 OTM
    atm_strike = round(underlying_ltp / gap) * gap
    strikes = [atm_strike + (i * gap) for i in range(-10, 11)]

    return strikes


def upper(s: str) -> str:
    """Safe uppercase."""
    return s.upper() if s else ""


async def get_option_chain(underlying: str, expiry: str) -> Dict[str, Any]:
    """
    Get option chain for underlying at expiry.

    Note: Yahoo Finance doesn't provide Indian option chain data.
    This is a simulated response. In production, integrate with:
    - Fyers API
    - Zerodha Kite Connect
    - NSE India direct scraping
    """
    # Get underlying price
    underlying_symbol = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "NIFTYFIN.NS",
        "SENSEX": "^BSESN",
    }.get(upper(underlying), "^NSEI")

    try:
        ticker = yf.Ticker(underlying_symbol)
        data = ticker.history(period="1d", interval="1m")
        underlying_ltp = round(data["Close"].iloc[-1], 2) if not data.empty else 10000
    except:
        underlying_ltp = 10000  # Default for NIFTY

    # Generate strikes
    strikes = get_strike_range(underlying_ltp, underlying)

    # Simulated option chain data
    option_chain = []
    for strike in strikes:
        # Simulated option prices (Black-Scholes approximation)
        moneyness = (underlying_ltp - strike) / strike

        # Call option: ITM when strike < LTP
        call_iv = 0.15 + random.uniform(-0.05, 0.05)
        call_ltp = max(0, underlying_ltp - strike) + (strike * call_iv * 0.1)

        # Put option: ITM when strike > LTP
        put_iv = 0.15 + random.uniform(-0.05, 0.05)
        put_ltp = max(0, strike - underlying_ltp) + (strike * put_iv * 0.1)

        # Simulated OI (higher at ATM and near strikes)
        distance_from_atm = abs(strike - underlying_ltp)
        base_oi = 100000 - int(distance_from_atm * 2)

        option_chain.append({
            "strike": strike,
            "call_ltp": round(call_ltp, 2),
            "call_oi": max(0, base_oi + random.randint(-10000, 10000)),
            "call_volume": random.randint(1000, 50000),
            "call_iv": round(call_iv, 4),
            "put_ltp": round(put_ltp, 2),
            "put_oi": max(0, base_oi + random.randint(-10000, 10000)),
            "put_volume": random.randint(1000, 50000),
            "put_iv": round(put_iv, 4),
        })

    return {
        "underlying": underlying.upper(),
        "underlying_ltp": underlying_ltp,
        "underlying_symbol": underlying_symbol,
        "expiry": expiry,
        "strikes": option_chain,
        "timestamp": datetime.now().isoformat(),
    }


def calculate_greeks(
    underlying_price: float,
    strike: float,
    expiry_days: int,
    option_type: str,
    ltp: float,
    risk_free_rate: float = 0.065,
) -> Dict[str, float]:
    """
    Calculate option Greeks (simplified Black-Scholes).

    Returns delta, gamma, theta, vega, rho.
    """
    import math

    # Simplified calculations
    time_to_expiry = expiry_days / 365.0
    if time_to_expiry <= 0:
        time_to_expiry = 0.001

    # Moneyness
    moneyness = underlying_price / strike

    # Intrinsic value
    if option_type.upper() == "CE":
        intrinsic = max(0, underlying_price - strike)
    else:
        intrinsic = max(0, strike - underlying_price)

    time_value = max(0, ltp - intrinsic)

    # Delta approximation
    if option_type.upper() == "CE":
        if moneyness > 1.05:
            delta = 0.9
        elif moneyness < 0.95:
            delta = 0.1
        else:
            delta = 0.5 + (moneyness - 1) * 5
    else:
        if moneyness > 1.05:
            delta = -0.1
        elif moneyness < 0.95:
            delta = -0.9
        else:
            delta = -0.5 + (moneyness - 1) * 5

    # Gamma (same for call and put)
    gamma = 0.02 / math.sqrt(time_to_expiry) if time_to_expiry > 0 else 0

    # Theta (time decay)
    theta = -time_value / expiry_days if expiry_days > 0 else 0

    # Vega (volatility sensitivity)
    vega = time_value * 0.5

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
        "rho": round(0.01 * time_to_expiry, 6),
    }


def get_futures_symbol(underlying: str, expiry_month: int = 0) -> str:
    """
    Get futures symbol for underlying.

    expiry_month: 0 = current month, 1 = next month, 2 = far month
    """
    # Futures symbol format: UNDERLYING YYMMM FUT
    # Example: NIFTY 24MAY FUT
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    today = datetime.now()
    target_month = today.month + expiry_month
    target_year = today.year + (target_month - 1) // 12
    target_month = ((target_month - 1) % 12) + 1

    expiry_str = f"{str(target_year)[-2:]}{months[target_month - 1]}"

    return f"{underlying.upper()}{expiry_str}FUT"
