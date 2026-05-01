"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== Auth Schemas ==============

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """User data response (without sensitive fields)."""
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ============== Stock Schemas ==============

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

# ============== Technical Analysis Schemas ==============

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
    signal: str
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

# ============== Order Schemas ==============

class OrderRequest(BaseModel):
    """Order creation request."""
    symbol: str
    action: str  # BUY or SELL
    quantity: int = Field(ge=1)
    order_type: str = "MARKET"
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
    status: str = "PENDING"
    created_at: str
    approved_at: Optional[str] = None

# ============== Portfolio Schemas ==============

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

# ============== F&O Schemas ==============

class F&OOrderRequest(BaseModel):
    """Futures & Options order request."""
    symbol: str  # e.g., "NIFTY24MAY22000CE"
    action: str  # BUY or SELL
    order_type: str = "MARKET"  # MARKET, LIMIT, SL, SLM
    quantity: int = Field(ge=1, description="Lot size * number of lots")
    price: Optional[float] = None  # For limit orders
    product_type: str = "MIS"  # MIS (intraday), CNC (delivery), NRML (F&O)
    validity: str = "DAY"  # DAY or IOC
    stop_loss: Optional[float] = None
    target: Optional[float] = None

class OptionChainItem(BaseModel):
    """Single option chain strike data."""
    strike: float
    call_ltp: Optional[float] = None
    call_oi: Optional[int] = None
    call_volume: Optional[int] = None
    call_iv: Optional[float] = None
    put_ltp: Optional[float] = None
    put_oi: Optional[int] = None
    put_volume: Optional[int] = None
    put_iv: Optional[float] = None

class OptionChainResponse(BaseModel):
    """Option chain response for an underlying."""
    underlying: str
    underlying_ltp: float
    expiry: str
    strikes: List[OptionChainItem]

class F&OPosition(BaseModel):
    """F&O position."""
    symbol: str
    product_type: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float
