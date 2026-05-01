from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StockData(BaseModel):
    """Stock price data."""
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    day_high: float
    day_low: float
    volume: int
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    historical_data: List[Dict[str, Any]]
    timestamp: str


class StockSearchResult(BaseModel):
    """Stock search result."""
    symbol: str
    name: str
    sector: str


class IndicatorSignal(BaseModel):
    """Individual indicator signal."""
    value: Optional[float] = None
    signal: str
    interpretation: Optional[str] = None


class MACDSignal(BaseModel):
    """MACD indicator values."""
    macd: Optional[float] = None
    signal: Optional[float] = None
    histogram: Optional[float] = None
    signal_type: Dict[str, Any]


class MovingAverages(BaseModel):
    """Moving average signals."""
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    price_vs_sma20: str
    price_vs_sma50: str
    price_vs_sma200: str


class BollingerBands(BaseModel):
    """Bollinger Bands values."""
    upper: Optional[float] = None
    middle: Optional[float] = None
    lower: Optional[float] = None
    position: str


class TechnicalAnalysis(BaseModel):
    """Complete technical analysis."""
    rsi: IndicatorSignal
    macd: MACDSignal
    moving_averages: MovingAverages
    bollinger_bands: BollingerBands
    stochastic: Dict[str, Any]
    atr: Dict[str, Any]


class TradingSignal(BaseModel):
    """Composite trading signal."""
    signal: str  # STRONG_BUY, BUY, WEAK_BUY, NEUTRAL, WEAK_SELL, SELL, STRONG_SELL
    confidence: int
    buy_signals: int
    sell_signals: int
    reasons: List[str]


class AnalysisResponse(BaseModel):
    """Full analysis response."""
    symbol: str
    name: str
    current_price: float
    timestamp: str
    technical_indicators: TechnicalAnalysis
    trading_signal: TradingSignal


class OrderRequest(BaseModel):
    """Order creation request."""
    symbol: str
    action: str  # BUY or SELL
    quantity: int = Field(ge=1)
    order_type: str = "MARKET"  # MARKET, LIMIT, SL, SLM
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None


class Order(BaseModel):
    """Order with ID."""
    id: str
    symbol: str
    action: str
    quantity: int
    order_type: str
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXECUTED
    created_at: str
    approved_at: Optional[str] = None


class PortfolioItem(BaseModel):
    """Portfolio holding."""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    invested_value: float
    current_value: float
    pnl: float
    pnl_percent: float


class PortfolioResponse(BaseModel):
    """Portfolio summary."""
    total_invested: float
    total_current_value: float
    total_pnl: float
    total_pnl_percent: float
    holdings: List[PortfolioItem]
