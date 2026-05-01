import pandas as pd
import pandas_ta as ta
from typing import Dict, Any, List


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for a stock.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with added indicators
    """
    # Momentum indicators
    df.ta.rsi(length=14, append=True)  # RSI_14
    df.ta.macd(append=True)  # MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
    df.ta.stoch(append=True)  # STOCHk_14_3_3, STOCHd_14_3_3
    df.ta.cci(length=20, append=True)  # CCI_20
    df.ta.willr(append=True)  # WILLR_14

    # Trend indicators
    df.ta.sma(length=20, append=True)  # SMA_20
    df.ta.sma(length=50, append=True)  # SMA_50
    df.ta.sma(length=200, append=True)  # SMA_200
    df.ta.ema(length=12, append=True)  # EMA_12
    df.ta.ema(length=26, append=True)  # EMA_26
    df.ta.vwap(append=True)  # VWAP_D

    # Volatility indicators
    df.ta.bbands(length=20, std=2, append=True)  # BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
    df.ta.atr(length=14, append=True)  # ATR_14

    # Volume indicators
    df.ta.obv(append=True)  # OBV
    df.ta.vwap(append=True)  # VWAP

    return df


def get_indicator_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate signals from technical indicators.

    Returns:
        Dictionary with indicator signals and values
    """
    if df.empty or len(df) < 50:
        return {"error": "Insufficient data for analysis"}

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    signals = {
        "rsi": {
            "value": round(latest["RSI_14"], 2) if "RSI_14" in latest else None,
            "signal": get_rsi_signal(latest.get("RSI_14", 50)),
            "interpretation": interpret_rsi(latest.get("RSI_14", 50))
        },
        "macd": {
            "macd": round(latest["MACD_12_26_9"], 4) if "MACD_12_26_9" in latest else None,
            "signal": round(latest["MACDs_12_26_9"], 4) if "MACDs_12_26_9" in latest else None,
            "histogram": round(latest["MACDh_12_26_9"], 4) if "MACDh_12_26_9" in latest else None,
            "signal_type": get_macd_signal(latest, prev)
        },
        "moving_averages": {
            "sma_20": round(latest["SMA_20"], 2) if "SMA_20" in latest else None,
            "sma_50": round(latest["SMA_50"], 2) if "SMA_50" in latest else None,
            "sma_200": round(latest["SMA_200"], 2) if "SMA_200" in latest else None,
            "ema_12": round(latest["EMA_12"], 2) if "EMA_12" in latest else None,
            "ema_26": round(latest["EMA_26"], 2) if "EMA_26" in latest else None,
            "price_vs_sma20": get_price_vs_ma_signal(latest["Close"], latest.get("SMA_20")),
            "price_vs_sma50": get_price_vs_ma_signal(latest["Close"], latest.get("SMA_50")),
            "price_vs_sma200": get_price_vs_ma_signal(latest["Close"], latest.get("SMA_200"))
        },
        "bollinger_bands": {
            "upper": round(latest["BBU_20_2.0"], 2) if "BBU_20_2.0" in latest else None,
            "middle": round(latest["BBM_20_2.0"], 2) if "BBM_20_2.0" in latest else None,
            "lower": round(latest["BBL_20_2.0"], 2) if "BBL_20_2.0" in latest else None,
            "position": get_bb_position(latest["Close"], latest)
        },
        "stochastic": {
            "k": round(latest["STOCHk_14_3_3"], 2) if "STOCHk_14_3_3" in latest else None,
            "d": round(latest["STOCHd_14_3_3"], 2) if "STOCHd_14_3_3" in latest else None,
            "signal": get_stoch_signal(latest)
        },
        "atr": {
            "value": round(latest["ATR_14"], 2) if "ATR_14" in latest else None,
            "interpretation": interpret_atr(latest.get("ATR_14", 0), latest["Close"])
        }
    }

    return signals


def get_rsi_signal(rsi_value: float) -> str:
    """Get RSI trading signal."""
    if rsi_value < 30:
        return "BUY"
    elif rsi_value > 70:
        return "SELL"
    elif rsi_value < 40:
        return "WEAK_BUY"
    elif rsi_value > 60:
        return "WEAK_SELL"
    return "NEUTRAL"


def interpret_rsi(rsi_value: float) -> str:
    """Interpret RSI value."""
    if rsi_value < 30:
        return "Oversold - Potential reversal upward"
    elif rsi_value > 70:
        return "Overbought - Potential reversal downward"
    elif rsi_value < 40:
        return "Approaching oversold"
    elif rsi_value > 60:
        return "Approaching overbought"
    return "Neutral momentum"


def get_macd_signal(latest: pd.Series, prev: pd.Series) -> Dict[str, Any]:
    """Get MACD trading signal."""
    macd = latest.get("MACD_12_26_9", 0)
    signal_line = latest.get("MACDs_12_26_9", 0)
    histogram = latest.get("MACDh_12_26_9", 0)
    prev_histogram = prev.get("MACDh_12_26_9", 0) if len(prev) > 0 else 0

    # Determine crossover
    crossover = "NONE"
    if macd > signal_line and prev.get("MACD_12_26_9", 0) <= prev.get("MACDs_12_26_9", 0):
        crossover = "BULLISH_CROSSOVER"
    elif macd < signal_line and prev.get("MACD_12_26_9", 0) >= prev.get("MACDs_12_26_9", 0):
        crossover = "BEARISH_CROSSOVER"

    # Histogram trend
    histogram_trend = "INCREASING" if histogram > prev_histogram else "DECREASING"

    # Signal
    if crossover == "BULLISH_CROSSOVER":
        signal = "BUY"
    elif crossover == "BEARISH_CROSSOVER":
        signal = "SELL"
    elif macd > signal_line:
        signal = "BULLISH"
    elif macd < signal_line:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    return {
        "signal": signal,
        "crossover": crossover,
        "histogram_trend": histogram_trend
    }


def get_price_vs_ma_signal(price: float, ma_value: float) -> str:
    """Get signal based on price vs moving average."""
    if ma_value is None:
        return "NEUTRAL"

    if price > ma_value:
        return "BULLISH"
    elif price < ma_value:
        return "BEARISH"
    return "NEUTRAL"


def get_bb_position(price: float, latest: pd.Series) -> str:
    """Get price position relative to Bollinger Bands."""
    upper = latest.get("BBU_20_2.0", 0)
    middle = latest.get("BBM_20_2.0", 0)
    lower = latest.get("BBL_20_2.0", 0)

    if price >= upper:
        return "AT_UPPER"  # Overbought
    elif price <= lower:
        return "AT_LOWER"  # Oversold
    elif price >= middle:
        return "ABOVE_MIDDLE"
    else:
        return "BELOW_MIDDLE"


def get_stoch_signal(latest: pd.Series) -> str:
    """Get Stochastic oscillator signal."""
    k = latest.get("STOCHk_14_3_3", 50)
    d = latest.get("STOCHd_14_3_3", 50)

    if k < 20 and d < 20:
        return "OVERSOLD_BUY"
    elif k > 80 and d > 80:
        return "OVERBOUGHT_SELL"
    elif k < 30:
        return "WEAK_BUY"
    elif k > 70:
        return "WEAK_SELL"
    return "NEUTRAL"


def interpret_atr(atr_value: float, price: float) -> str:
    """Interpret ATR as volatility percentage."""
    if price == 0:
        return "N/A"

    atr_percent = (atr_value / price) * 100

    if atr_percent > 5:
        return "High volatility"
    elif atr_percent > 3:
        return "Moderate volatility"
    else:
        return "Low volatility"


def generate_composite_signal(indicator_signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a composite trading signal from all indicators.

    Returns:
        Dictionary with overall signal, confidence, and reasoning
    """
    buy_signals = 0
    sell_signals = 0
    neutral_signals = 0
    reasons = []

    # RSI signal
    rsi = indicator_signals.get("rsi", {})
    if rsi.get("signal") == "BUY":
        buy_signals += 2
        reasons.append(f"RSI oversold ({rsi.get('value', 'N/A')})")
    elif rsi.get("signal") == "SELL":
        sell_signals += 2
        reasons.append(f"RSI overbought ({rsi.get('value', 'N/A')})")
    elif rsi.get("signal") == "WEAK_BUY":
        buy_signals += 1
        reasons.append("RSI approaching oversold")
    elif rsi.get("signal") == "WEAK_SELL":
        sell_signals += 1
        reasons.append("RSI approaching overbought")

    # MACD signal
    macd = indicator_signals.get("macd", {})
    macd_signal = macd.get("signal_type", {}).get("signal", "NEUTRAL")
    if macd_signal == "BUY":
        buy_signals += 2
        reasons.append("MACD bullish crossover")
    elif macd_signal == "SELL":
        sell_signals += 2
        reasons.append("MACD bearish crossover")
    elif macd_signal == "BULLISH":
        buy_signals += 1
    elif macd_signal == "BEARISH":
        sell_signals += 1

    # Moving averages
    ma = indicator_signals.get("moving_averages", {})
    ma_signals = [
        ma.get("price_vs_sma20"),
        ma.get("price_vs_sma50"),
        ma.get("price_vs_sma200")
    ]
    for sig in ma_signals:
        if sig == "BULLISH":
            buy_signals += 1
        elif sig == "BEARISH":
            sell_signals += 1

    if ma.get("price_vs_sma200") == "BULLISH":
        reasons.append("Price above 200-day SMA (long-term bullish)")
    elif ma.get("price_vs_sma200") == "BEARISH":
        reasons.append("Price below 200-day SMA (long-term bearish)")

    # Bollinger Bands
    bb = indicator_signals.get("bollinger_bands", {})
    bb_pos = bb.get("position", "")
    if bb_pos == "AT_LOWER":
        buy_signals += 1
        reasons.append("Price at lower Bollinger Band (potential bounce)")
    elif bb_pos == "AT_UPPER":
        sell_signals += 1
        reasons.append("Price at upper Bollinger Band (potential pullback)")

    # Stochastic
    stoch = indicator_signals.get("stochastic", {})
    stoch_signal = stoch.get("signal", "NEUTRAL")
    if "OVERSOLD" in stoch_signal:
        buy_signals += 1
    elif "OVERBOUGHT" in stoch_signal:
        sell_signals += 1

    # Calculate overall signal
    total = buy_signals + sell_signals + neutral_signals
    if total == 0:
        overall_signal = "NEUTRAL"
        confidence = 0
    else:
        net_score = buy_signals - sell_signals
        if net_score >= 4:
            overall_signal = "STRONG_BUY"
            confidence = min(95, 60 + net_score * 5)
        elif net_score >= 2:
            overall_signal = "BUY"
            confidence = min(80, 50 + net_score * 5)
        elif net_score >= 1:
            overall_signal = "WEAK_BUY"
            confidence = 40
        elif net_score <= -4:
            overall_signal = "STRONG_SELL"
            confidence = min(95, 60 + abs(net_score) * 5)
        elif net_score <= -2:
            overall_signal = "SELL"
            confidence = min(80, 50 + abs(net_score) * 5)
        elif net_score <= -1:
            overall_signal = "WEAK_SELL"
            confidence = 40
        else:
            overall_signal = "NEUTRAL"
            confidence = 30

    return {
        "signal": overall_signal,
        "confidence": confidence,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "reasons": reasons[:5]  # Top 5 reasons
    }
