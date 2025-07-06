"""
Pydantic models for API request/response validation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class StockCreate(BaseModel):
    """Model for creating a new stock in portfolio."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")
    quantity: float = Field(..., gt=0, description="Number of shares")
    average_buy_price: float = Field(..., gt=0, description="Average purchase price per share")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Ticker symbol must be 1-10 characters')
        # Allow alphanumeric and some special characters for international tickers
        if not v.replace('.', '').replace('-', '').isalnum():
            raise ValueError('Ticker symbol contains invalid characters')
        return v.upper()


class StockUpdate(BaseModel):
    """Model for updating an existing stock in portfolio."""
    quantity: Optional[float] = Field(None, gt=0, description="Number of shares")
    average_buy_price: Optional[float] = Field(None, gt=0, description="Average purchase price per share")


class StockResponse(BaseModel):
    """Model for stock response data."""
    id: int
    ticker: str
    quantity: float
    average_buy_price: float
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """Model for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(BaseModel):
    """Model for user response data."""
    id: int
    username: str
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Model for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int


class AnalysisRequest(BaseModel):
    """Model for analysis request."""
    tickers: List[str] = Field(..., min_items=1, max_items=50, description="List of ticker symbols to analyze")
    
    @validator('tickers')
    def validate_tickers(cls, v):
        validated_tickers = []
        for ticker in v:
            if not ticker or len(ticker) > 10:
                raise ValueError(f'Invalid ticker symbol: {ticker}')
            validated_tickers.append(ticker.upper())
        return validated_tickers


class TechnicalScore(BaseModel):
    """Model for technical analysis score."""
    total_score: float = Field(..., ge=-20, le=20, description="Total technical score")
    individual_scores: Dict[str, float] = Field(..., description="Breakdown of individual indicator scores")
    confidence_level: str = Field(..., description="Confidence level (low/medium/high)")
    recommendation: str = Field(..., description="Investment recommendation")
    signal_strength: str = Field(..., description="Signal strength")


class EventScore(BaseModel):
    """Model for event-driven score."""
    total_event_score: float = Field(..., ge=-5, le=5, description="Total event score")
    individual_events: Dict[str, Any] = Field(..., description="Individual event scores")
    weighted_events: Dict[str, float] = Field(..., description="Weighted event scores")
    active_events: List[str] = Field(..., description="List of active events")


class AnalysisResult(BaseModel):
    """Model for complete analysis result."""
    ticker: str
    status: str = Field(..., description="Analysis status (success/failed)")
    message: Optional[str] = Field(None, description="Status message or error details")
    technical_score: Optional[TechnicalScore] = None
    event_score: Optional[EventScore] = None
    ml_prediction: Optional[float] = Field(None, description="ML prediction score")
    ml_confidence: Optional[float] = Field(None, ge=0, le=1, description="ML prediction confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemStatus(BaseModel):
    """Model for system status information."""
    status: str = Field(..., description="Overall system status")
    uptime: str = Field(..., description="System uptime")
    active_plugins: List[str] = Field(..., description="List of active plugins")
    database_status: str = Field(..., description="Database connection status")
    last_analysis_run: Optional[datetime] = Field(None, description="Timestamp of last analysis")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")


class PluginStatus(BaseModel):
    """Model for plugin status information."""
    name: str
    status: str = Field(..., description="Plugin status (active/inactive/error)")
    last_run: Optional[datetime] = None
    error_message: Optional[str] = None
    success_rate: Optional[float] = Field(None, ge=0, le=1)
    avg_response_time: Optional[float] = Field(None, ge=0)


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Model for generic success responses."""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)