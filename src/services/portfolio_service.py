"""
Portfolio service for handling stock portfolio operations.
"""
from typing import Optional, List, Dict, Any
import logging

from src.database.db_access import DBAccess
from src.models.api_models import StockCreate, StockUpdate, StockResponse

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service class for portfolio management operations."""
    
    def __init__(self, db_access: DBAccess):
        """
        Initialize PortfolioService with database access.
        
        Args:
            db_access: Database access layer instance
        """
        self.db_access = db_access
    
    async def add_stock(self, user_id: int, stock_data: StockCreate) -> Optional[StockResponse]:
        """
        Add a new stock to user's portfolio.
        
        Args:
            user_id: User ID
            stock_data: Stock creation data
            
        Returns:
            StockResponse if successful, None if stock already exists
        """
        try:
            # Check if stock already exists in user's portfolio
            existing_stocks = await self.db_access.get_stocks_by_user_id(user_id)
            for stock in existing_stocks:
                if stock["ticker"] == stock_data.ticker:
                    logger.warning(
                        f"Stock {stock_data.ticker} already exists in portfolio for user {user_id}"
                    )
                    return None
            
            # Add stock to portfolio
            stock_dict = await self.db_access.add_stock_to_portfolio(
                user_id=user_id,
                ticker=stock_data.ticker,
                quantity=stock_data.quantity,
                average_buy_price=stock_data.average_buy_price
            )
            
            if stock_dict is None:
                logger.error(f"Failed to add stock {stock_data.ticker} to portfolio for user {user_id}")
                return None
            
            # Convert to response model
            return self._convert_to_stock_response(stock_dict)
            
        except Exception as e:
            logger.error(f"Error adding stock {stock_data.ticker} for user {user_id}: {str(e)}")
            raise
    
    async def get_user_stocks(self, user_id: int) -> List[StockResponse]:
        """
        Get all stocks in user's portfolio.
        
        Args:
            user_id: User ID
            
        Returns:
            List of StockResponse objects
        """
        try:
            stocks = await self.db_access.get_stocks_by_user_id(user_id)
            return [self._convert_to_stock_response(stock) for stock in stocks]
            
        except Exception as e:
            logger.error(f"Error getting stocks for user {user_id}: {str(e)}")
            raise
    
    async def get_stock_by_id(self, stock_id: int, user_id: int) -> Optional[StockResponse]:
        """
        Get specific stock by ID, ensuring it belongs to the user.
        
        Args:
            stock_id: Stock ID
            user_id: User ID (for authorization check)
            
        Returns:
            StockResponse if found and authorized, None otherwise
        """
        try:
            stock_dict = await self.db_access.get_stock_by_id(stock_id)
            
            if stock_dict is None:
                logger.warning(f"Stock with ID {stock_id} not found")
                return None
                
            if stock_dict["user_id"] != user_id:
                logger.warning(f"User {user_id} not authorized to access stock {stock_id}")
                return None
            
            return self._convert_to_stock_response(stock_dict)
            
        except Exception as e:
            logger.error(f"Error getting stock {stock_id} for user {user_id}: {str(e)}")
            raise
    
    async def update_stock(
        self, 
        stock_id: int, 
        user_id: int, 
        stock_update: StockUpdate
    ) -> Optional[StockResponse]:
        """
        Update stock in user's portfolio.
        
        Args:
            stock_id: Stock ID
            user_id: User ID (for authorization check)
            stock_update: Stock update data
            
        Returns:
            Updated StockResponse if successful, None if not found/unauthorized
        """
        try:
            # Check if stock exists and belongs to user
            existing_stock = await self.get_stock_by_id(stock_id, user_id)
            if existing_stock is None:
                return None
            
            # Update only provided fields
            quantity = stock_update.quantity if stock_update.quantity is not None else existing_stock.quantity
            average_buy_price = (
                stock_update.average_buy_price 
                if stock_update.average_buy_price is not None 
                else existing_stock.average_buy_price
            )
            
            # Perform update
            success = await self.db_access.update_stock_in_portfolio(
                stock_id=stock_id,
                quantity=quantity,
                average_buy_price=average_buy_price
            )
            
            if not success:
                logger.error(f"Failed to update stock {stock_id} for user {user_id}")
                return None
            
            # Return updated stock
            return await self.get_stock_by_id(stock_id, user_id)
            
        except Exception as e:
            logger.error(f"Error updating stock {stock_id} for user {user_id}: {str(e)}")
            raise
    
    async def delete_stock(self, stock_id: int, user_id: int) -> bool:
        """
        Delete stock from user's portfolio.
        
        Args:
            stock_id: Stock ID
            user_id: User ID (for authorization check)
            
        Returns:
            True if deleted successfully, False if not found/unauthorized
        """
        try:
            # Check if stock exists and belongs to user
            existing_stock = await self.get_stock_by_id(stock_id, user_id)
            if existing_stock is None:
                return False
            
            # Delete stock
            success = await self.db_access.delete_stock_from_portfolio(stock_id)
            
            if success:
                logger.info(f"Stock {stock_id} deleted from portfolio for user {user_id}")
            else:
                logger.error(f"Failed to delete stock {stock_id} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting stock {stock_id} for user {user_id}: {str(e)}")
            raise
    
    async def add_stock_from_analysis(self, user_id: int, ticker: str) -> Optional[StockResponse]:
        """
        Add stock from analysis results with default values.
        
        Args:
            user_id: User ID
            ticker: Stock ticker symbol
            
        Returns:
            StockResponse if successful, None otherwise
        """
        try:
            # TODO: Get actual current price from market data
            # For now, use placeholder values
            default_quantity = 1.0
            default_price = 100.0
            
            stock_data = StockCreate(
                ticker=ticker,
                quantity=default_quantity,
                average_buy_price=default_price
            )
            
            return await self.add_stock(user_id, stock_data)
            
        except Exception as e:
            logger.error(f"Error adding stock {ticker} from analysis for user {user_id}: {str(e)}")
            raise
    
    def _convert_to_stock_response(self, stock_dict: Dict[str, Any]) -> StockResponse:
        """
        Convert database stock dictionary to StockResponse model.
        
        Args:
            stock_dict: Stock data from database
            
        Returns:
            StockResponse object
        """
        # Calculate derived values
        current_price = stock_dict.get("current_price")
        total_value = None
        profit_loss = None
        profit_loss_percentage = None
        
        if current_price is not None:
            total_value = stock_dict["quantity"] * current_price
            cost_basis = stock_dict["quantity"] * stock_dict["average_buy_price"]
            profit_loss = total_value - cost_basis
            if cost_basis > 0:
                profit_loss_percentage = (profit_loss / cost_basis) * 100
        
        return StockResponse(
            id=stock_dict["id"],
            ticker=stock_dict["ticker"],
            quantity=stock_dict["quantity"],
            average_buy_price=stock_dict["average_buy_price"],
            current_price=current_price,
            total_value=total_value,
            profit_loss=profit_loss,
            profit_loss_percentage=profit_loss_percentage,
            user_id=stock_dict["user_id"],
            created_at=stock_dict["created_at"],
            updated_at=stock_dict.get("updated_at")
        )