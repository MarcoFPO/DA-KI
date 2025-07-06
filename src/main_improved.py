"""
Improved FastAPI main application with better architecture.
"""
import os
import logging
from typing import Annotated, List
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

# Import models
from src.models.api_models import (
    StockCreate, StockUpdate, StockResponse, UserCreate, UserResponse,
    TokenResponse, AnalysisRequest, AnalysisResult, SystemStatus,
    ErrorResponse, SuccessResponse
)

# Import services
from src.services.user_service import UserService
from src.services.portfolio_service import PortfolioService
from src.services.analysis_service import AnalysisService

# Import utilities
from src.auth.jwt_utils import create_access_token, create_refresh_token, verify_token
from src.database.db_access_extended import DBAccessExtended
from src.config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DA-KI Stock Analysis API",
    description="Automated stock portfolio management system with AI-powered analysis",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_access = DBAccessExtended()
user_service = UserService(db_access)
portfolio_service = PortfolioService(db_access)
analysis_service = AnalysisService(db_access)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


# Dependency functions
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token, credentials_exception)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception
            
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise credentials_exception


async def get_current_admin_user(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """Ensure current user has admin privileges."""
    if not user_service.is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


# Authentication endpoints
@app.post("/api/auth/token", response_model=TokenResponse, tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    try:
        # Authenticate user
        user = await user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Update last login
        await db_access.update_last_login(user["id"])
        
        # Create tokens
        access_token_expires = timedelta(minutes=Config.get("jwt", {}).get("access_token_expire_minutes", 30))
        refresh_token_expires = timedelta(days=Config.get("jwt", {}).get("refresh_token_expire_days", 7))
        
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user["username"]}, 
            expires_delta=refresh_token_expires
        )
        
        logger.info(f"User '{form_data.username}' logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_token_expires.total_seconds())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user '{form_data.username}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


@app.post("/api/auth/register", response_model=SuccessResponse, tags=["Authentication"])
async def register_user(user_data: UserCreate) -> SuccessResponse:
    """Register a new user."""
    try:
        user = await user_service.create_user(user_data)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        logger.info(f"New user '{user_data.username}' registered successfully")
        
        return SuccessResponse(
            message="User registered successfully",
            data={"username": user.username, "id": user.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for user '{user_data.username}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )


# User management endpoints (Admin only)
@app.get("/api/admin/users", response_model=List[UserResponse], tags=["User Management"])
async def get_all_users(
    admin_user: Annotated[dict, Depends(get_current_admin_user)]
) -> List[UserResponse]:
    """Get all registered users (admin only)."""
    try:
        users = await user_service.get_all_users()
        logger.info(f"Admin user {admin_user['username']} requested user list")
        return users
        
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@app.delete("/api/admin/users/{user_id}", response_model=SuccessResponse, tags=["User Management"])
async def delete_user(
    user_id: int,
    admin_user: Annotated[dict, Depends(get_current_admin_user)]
) -> SuccessResponse:
    """Delete a user by ID (admin only)."""
    try:
        # Prevent admin from deleting themselves
        if user_id == admin_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin user {admin_user['username']} deleted user {user_id}")
        
        return SuccessResponse(
            message=f"User with ID {user_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )


# Portfolio management endpoints
@app.get("/api/portfolio/stocks", response_model=List[StockResponse], tags=["Portfolio"])
async def get_user_stocks(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> List[StockResponse]:
    """Get all stocks in user's portfolio."""
    try:
        stocks = await portfolio_service.get_user_stocks(current_user["id"])
        return stocks
        
    except Exception as e:
        logger.error(f"Error getting stocks for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving portfolio"
        )


@app.post("/api/portfolio/stocks", response_model=StockResponse, tags=["Portfolio"])
async def add_stock(
    stock_data: StockCreate,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> StockResponse:
    """Add a new stock to user's portfolio."""
    try:
        stock = await portfolio_service.add_stock(current_user["id"], stock_data)
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock already exists in portfolio or invalid data"
            )
        
        logger.info(f"User {current_user['username']} added stock {stock_data.ticker}")
        return stock
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock {stock_data.ticker} for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding stock to portfolio"
        )


@app.get("/api/portfolio/stocks/{stock_id}", response_model=StockResponse, tags=["Portfolio"])
async def get_stock_details(
    stock_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> StockResponse:
    """Get details of a specific stock in user's portfolio."""
    try:
        stock = await portfolio_service.get_stock_by_id(stock_id, current_user["id"])
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found or not authorized"
            )
        
        return stock
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock {stock_id} for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving stock details"
        )


@app.put("/api/portfolio/stocks/{stock_id}", response_model=StockResponse, tags=["Portfolio"])
async def update_stock(
    stock_id: int,
    stock_update: StockUpdate,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> StockResponse:
    """Update a stock in user's portfolio."""
    try:
        stock = await portfolio_service.update_stock(stock_id, current_user["id"], stock_update)
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found or not authorized"
            )
        
        logger.info(f"User {current_user['username']} updated stock {stock_id}")
        return stock
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating stock {stock_id} for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating stock"
        )


@app.delete("/api/portfolio/stocks/{stock_id}", response_model=SuccessResponse, tags=["Portfolio"])
async def delete_stock(
    stock_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> SuccessResponse:
    """Delete a stock from user's portfolio."""
    try:
        success = await portfolio_service.delete_stock(stock_id, current_user["id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found or not authorized"
            )
        
        logger.info(f"User {current_user['username']} deleted stock {stock_id}")
        
        return SuccessResponse(
            message="Stock deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting stock {stock_id} for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting stock"
        )


# Analysis endpoints
@app.post("/api/analysis/start", response_model=List[AnalysisResult], tags=["Analysis"])
async def start_analysis(
    analysis_request: AnalysisRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> List[AnalysisResult]:
    """Start comprehensive analysis for given tickers."""
    try:
        results = await analysis_service.analyze_stocks(analysis_request, current_user["id"])
        
        logger.info(
            f"User {current_user['username']} completed analysis for "
            f"{len(analysis_request.tickers)} tickers"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error during analysis for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during stock analysis"
        )


@app.post("/api/portfolio/add-from-analysis", response_model=StockResponse, tags=["Portfolio"])
async def add_stock_from_analysis(
    ticker: str = Body(..., description="Ticker symbol to add from analysis"),
    current_user: Annotated[dict, Depends(get_current_user)] = None
) -> StockResponse:
    """Add stock from analysis results to portfolio."""
    try:
        stock = await portfolio_service.add_stock_from_analysis(current_user["id"], ticker)
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock already exists in portfolio or invalid data"
            )
        
        logger.info(f"User {current_user['username']} added stock {ticker} from analysis")
        return stock
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock {ticker} from analysis for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding stock from analysis"
        )


# System status endpoints
@app.get("/api/system/status", response_model=SystemStatus, tags=["System"])
async def get_system_status() -> SystemStatus:
    """Get system status information."""
    try:
        # Check database connection
        db_healthy = await db_access.check_connection()
        db_info = await db_access.get_database_info()
        
        # TODO: Check plugin statuses
        active_plugins = []  # Placeholder
        
        # TODO: Get performance metrics
        performance_metrics = {
            "database_size_mb": db_info.get("database_size_mb", 0),
            "total_users": db_info.get("table_counts", {}).get("users", 0),
            "total_portfolios": db_info.get("table_counts", {}).get("portfolios", 0)
        }
        
        return SystemStatus(
            status="healthy" if db_healthy else "unhealthy",
            uptime="Unknown",  # TODO: Implement uptime tracking
            active_plugins=active_plugins,
            database_status="connected" if db_healthy else "disconnected",
            last_analysis_run=None,  # TODO: Track last analysis
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving system status"
        )


# Health check endpoints
@app.get("/health/liveness", tags=["Health"])
async def liveness_check():
    """Liveness probe endpoint."""
    return {"status": "alive"}


@app.get("/health/readiness", tags=["Health"])
async def readiness_check():
    """Readiness probe endpoint."""
    try:
        # Check database connection
        db_healthy = await db_access.check_connection()
        
        if not db_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to DA-KI Stock Analysis API",
        "version": "0.1.0",
        "docs_url": "/api/docs",
        "health_check": "/health/liveness"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return ErrorResponse(
        error=exc.detail,
        detail=f"HTTP {exc.status_code}: {exc.detail}"
    )


if __name__ == "__main__":
    import uvicorn
    
    # Load configuration
    Config.load_secrets()
    
    # Run the application
    uvicorn.run(
        "main_improved:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )