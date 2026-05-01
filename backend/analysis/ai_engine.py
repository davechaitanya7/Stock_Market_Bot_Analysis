"""AI-powered trading signal engine with pattern recognition."""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class AISignalEngine:
    """
    AI-powered trading signal generator.

    Combines:
    - Technical indicators (RSI, MACD, Bollinger, etc.)
    - Candlestick pattern recognition
    - Trend analysis
    - Volume analysis
    """

    def __init__(self):
        self.patterns = {
            "DOJI": self._detect_doji,
            "HAMMER": self._detect_hammer,
            "SHOOTING_STAR": self._detect_shooting_star,
            "ENGULFING_BULLISH": self._detect_engulfing_bullish,
            "ENGULFING_BEARISH": self._detect_engulfing_bearish,
            "MORNING_STAR": self._detect_morning_star,
            "EVENING_STAR": self._detect_evening_star,
            "INSIDE_BAR": self._detect_inside_bar,
        }

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI trading signal.

        Returns:
        {
            "signal": "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL",
            "confidence": 0-100,
            "patterns_detected": [...],
            "trend": "BULLISH" | "BEARISH" | "SIDEWAYS",
            "support_levels": [...],
            "resistance_levels": [...],
            "reasoning": [...]
        }
        """
        if df.empty or len(df) < 20:
            return {"error": "Insufficient data for AI analysis"}

        signals_score = 0
        reasons = []
        patterns_detected = []

        # 1. Pattern Recognition (weight: 30%)
        patterns = self._scan_patterns(df)
        for pattern in patterns:
            patterns_detected.append(pattern)
            if pattern["signal"] == "BULLISH":
                signals_score += 2
                reasons.append(f"Bullish pattern: {pattern['name']}")
            elif pattern["signal"] == "BEARISH":
                signals_score -= 2
                reasons.append(f"Bearish pattern: {pattern['name']}")

        # 2. Technical Indicators (weight: 40%)
        tech_score = self._analyze_technicals(indicators)
        signals_score += tech_score
        if tech_score > 0:
            reasons.append(f"Technical indicators bullish (+{tech_score})")
        elif tech_score < 0:
            reasons.append(f"Technical indicators bearish ({tech_score})")

        # 3. Trend Analysis (weight: 20%)
        trend = self._analyze_trend(df)
        if trend == "BULLISH":
            signals_score += 2
            reasons.append("Uptrend confirmed")
        elif trend == "BEARISH":
            signals_score -= 2
            reasons.append("Downtrend confirmed")
        else:
            reasons.append("Sideways/consolidation")

        # 4. Volume Analysis (weight: 10%)
        volume_signal = self._analyze_volume(df)
        if volume_signal == "HIGH_BUY":
            signals_score += 1
            reasons.append("High volume buying")
        elif volume_signal == "HIGH_SELL":
            signals_score -= 1
            reasons.append("High volume selling")

        # 5. Support/Resistance
        support, resistance = self._find_key_levels(df)

        # Calculate final signal
        total_score = abs(signals_score)
        max_possible = 10

        if signals_score >= 5:
            signal = "STRONG_BUY"
            confidence = min(95, 60 + signals_score * 5)
        elif signals_score >= 3:
            signal = "BUY"
            confidence = min(80, 50 + signals_score * 5)
        elif signals_score >= 1:
            signal = "HOLD"
            confidence = 40
        elif signals_score <= -5:
            signal = "STRONG_SELL"
            confidence = min(95, 60 + abs(signals_score) * 5)
        elif signals_score <= -3:
            signal = "SELL"
            confidence = min(80, 50 + abs(signals_score) * 5)
        else:
            signal = "HOLD"
            confidence = 30

        return {
            "signal": signal,
            "confidence": confidence,
            "patterns_detected": patterns_detected[:5],  # Top 5 patterns
            "trend": trend,
            "support_levels": support,
            "resistance_levels": resistance,
            "reasoning": reasons[:7],  # Top 7 reasons
            "timestamp": datetime.now().isoformat(),
        }

    def _scan_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Scan for candlestick patterns."""
        detected = []
        for pattern_name, detector in self.patterns.items():
            result = detector(df)
            if result:
                detected.append(result)
        return detected

    def _detect_doji(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Doji pattern (open ≈ close)."""
        if len(df) < 1:
            return None
        row = df.iloc[-1]
        body = abs(row["Close"] - row["Open"])
        range_size = row["High"] - row["Low"]

        if range_size > 0 and body / range_size < 0.1:
            return {
                "name": "DOJI",
                "signal": "NEUTRAL",  # Reversal signal needs context
                "strength": "WEAK",
            }
        return None

    def _detect_hammer(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Hammer (bullish reversal)."""
        if len(df) < 2:
            return None
        row = df.iloc[-1]
        prev = df.iloc[-2]

        body = row["Close"] - row["Open"]
        lower_shadow = min(row["Open"], row["Close"]) - row["Low"]
        upper_shadow = row["High"] - max(row["Open"], row["Close"])
        range_size = row["High"] - row["Low"]

        # Hammer criteria
        if (
            lower_shadow > 2 * body
            and upper_shadow < body
            and row["Close"] > row["Open"]  # Bullish close
            and row["Close"] < prev["Close"]  # After decline
        ):
            return {
                "name": "HAMMER",
                "signal": "BULLISH",
                "strength": "MODERATE",
            }
        return None

    def _detect_shooting_star(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Shooting Star (bearish reversal)."""
        if len(df) < 2:
            return None
        row = df.iloc[-1]
        prev = df.iloc[-2]

        body = row["Close"] - row["Open"]
        upper_shadow = row["High"] - max(row["Open"], row["Close"])
        lower_shadow = min(row["Open"], row["Close"]) - row["Low"]

        if (
            upper_shadow > 2 * body
            and lower_shadow < body
            and row["Close"] < row["Open"]  # Bearish close
            and row["Close"] > prev["Close"]  # After rise
        ):
            return {
                "name": "SHOOTING_STAR",
                "signal": "BEARISH",
                "strength": "MODERATE",
            }
        return None

    def _detect_engulfing_bullish(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Bullish Engulfing pattern."""
        if len(df) < 2:
            return None
        current = df.iloc[-1]
        prev = df.iloc[-2]

        prev_body = prev["Close"] - prev["Open"]
        curr_body = current["Close"] - current["Open"]

        if (
            prev_body < 0  # Previous bearish
            and curr_body > 0  # Current bullish
            and current["Open"] < prev["Close"]  # Opens below prev close
            and current["Close"] > prev["Open"]  # Closes above prev open
        ):
            return {
                "name": "BULLISH_ENGULFING",
                "signal": "BULLISH",
                "strength": "STRONG",
            }
        return None

    def _detect_engulfing_bearish(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Bearish Engulfing pattern."""
        if len(df) < 2:
            return None
        current = df.iloc[-1]
        prev = df.iloc[-2]

        prev_body = prev["Close"] - prev["Open"]
        curr_body = current["Close"] - current["Open"]

        if (
            prev_body > 0  # Previous bullish
            and curr_body < 0  # Current bearish
            and current["Open"] > prev["Close"]  # Opens above prev close
            and current["Close"] < prev["Open"]  # Closes below prev open
        ):
            return {
                "name": "BEARISH_ENGULFING",
                "signal": "BEARISH",
                "strength": "STRONG",
            }
        return None

    def _detect_morning_star(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Morning Star (3-candle bullish reversal)."""
        if len(df) < 3:
            return None
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

        if (
            c1["Close"] < c1["Open"]  # First: bearish
            and abs(c2["Close"] - c2["Open"]) < (c2["High"] - c2["Low"]) * 0.3  # Second: small body
            and c3["Close"] > c3["Open"]  # Third: bullish
            and c3["Close"] > (c1["Open"] + c1["Close"]) / 2  # Close into first candle
        ):
            return {
                "name": "MORNING_STAR",
                "signal": "BULLISH",
                "strength": "STRONG",
            }
        return None

    def _detect_evening_star(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Evening Star (3-candle bearish reversal)."""
        if len(df) < 3:
            return None
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

        if (
            c1["Close"] > c1["Open"]  # First: bullish
            and abs(c2["Close"] - c2["Open"]) < (c2["High"] - c2["Low"]) * 0.3  # Second: small body
            and c3["Close"] < c3["Open"]  # Third: bearish
            and c3["Close"] < (c1["Open"] + c1["Close"]) / 2  # Close into first candle
        ):
            return {
                "name": "EVENING_STAR",
                "signal": "BEARISH",
                "strength": "STRONG",
            }
        return None

    def _detect_inside_bar(self, df: pd.DataFrame) -> Dict[str, Any] | None:
        """Detect Inside Bar pattern."""
        if len(df) < 2:
            return None
        current = df.iloc[-1]
        prev = df.iloc[-2]

        if (
            current["High"] < prev["High"]
            and current["Low"] > prev["Low"]
        ):
            # Inside bar - direction depends on breakout
            return {
                "name": "INSIDE_BAR",
                "signal": "NEUTRAL",
                "strength": "WEAK",
                "note": "Wait for breakout direction",
            }
        return None

    def _analyze_technicals(self, indicators: Dict[str, Any]) -> int:
        """Analyze technical indicators and return score (-5 to +5)."""
        score = 0

        # RSI
        rsi = indicators.get("rsi", {}).get("value", 50)
        if rsi < 30:
            score += 2
        elif rsi < 40:
            score += 1
        elif rsi > 70:
            score -= 2
        elif rsi > 60:
            score -= 1

        # MACD
        macd_signal = indicators.get("macd", {}).get("signal_type", {}).get("signal", "NEUTRAL")
        if macd_signal == "BUY" or macd_signal == "BULLISH":
            score += 2
        elif macd_signal == "SELL" or macd_signal == "BEARISH":
            score -= 2

        # Moving averages
        ma = indicators.get("moving_averages", {})
        if ma.get("price_vs_sma20") == "BULLISH":
            score += 1
        elif ma.get("price_vs_sma20") == "BEARISH":
            score -= 1

        if ma.get("price_vs_sma50") == "BULLISH":
            score += 1
        elif ma.get("price_vs_sma50") == "BEARISH":
            score -= 1

        if ma.get("price_vs_sma200") == "BULLISH":
            score += 1
        elif ma.get("price_vs_sma200") == "BEARISH":
            score -= 1

        # Bollinger Bands
        bb_pos = indicators.get("bollinger_bands", {}).get("position", "")
        if bb_pos == "AT_LOWER":
            score += 1
        elif bb_pos == "AT_UPPER":
            score -= 1

        return max(-5, min(5, score))

    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze trend direction."""
        if len(df) < 50:
            return "SIDEWAYS"

        # Simple trend: higher highs and higher lows = bullish
        recent_high = df["High"].iloc[-20:].max()
        prev_high = df["High"].iloc[-40:-20].max()
        recent_low = df["Low"].iloc[-20:].min()
        prev_low = df["Low"].iloc[-40:-20].min()

        if recent_high > prev_high and recent_low > prev_low:
            return "BULLISH"
        elif recent_high < prev_high and recent_low < prev_low:
            return "BEARISH"
        return "SIDEWAYS"

    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze volume for smart money activity."""
        if len(df) < 20:
            return "NEUTRAL"

        recent_volume = df["Volume"].iloc[-5:].mean()
        avg_volume = df["Volume"].iloc[-20:].mean()

        if recent_volume > 2 * avg_volume:
            # High volume - check price direction
            price_change = df["Close"].iloc[-1] - df["Close"].iloc[-5]
            if price_change > 0:
                return "HIGH_BUY"
            else:
                return "HIGH_SELL"
        return "NEUTRAL"

    def _find_key_levels(self, df: pd.DataFrame) -> tuple:
        """Find support and resistance levels."""
        if len(df) < 20:
            return [], []

        # Find pivot highs and lows
        window = 10
        highs = df["High"].iloc[-50:]
        lows = df["Low"].iloc[-50:]

        resistance = []
        support = []

        for i in range(window, len(highs) - window):
            if highs.iloc[i] == highs.iloc[i - window:i + window + 1].max():
                resistance.append(round(highs.iloc[i], 2))
            if lows.iloc[i] == lows.iloc[i - window:i + window + 1].min():
                support.append(round(lows.iloc[i], 2))

        return support[-3:], resistance[-3:]  # Top 3 levels


# Singleton instance
ai_engine = AISignalEngine()
