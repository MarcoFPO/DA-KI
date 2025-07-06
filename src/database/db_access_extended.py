"""
Extended database access layer with improved error handling and additional methods.
"""
import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.config.config import Config

logger = logging.getLogger(__name__)


class DBAccessExtended:
    """Extended database access layer with better error handling and logging."""
    
    def __init__(self):
        """Initialize database access with configuration."""
        self.db_path = self._get_database_path()
        self._ensure_database_exists()
    
    def _get_database_path(self) -> str:
        """Get database path from configuration."""
        database_url = Config.get("database", {}).get("url", "sqlite:///./data/daki.db")
        if database_url.startswith("sqlite:///"):
            return database_url[10:]  # Remove sqlite:/// prefix
        return "./data/daki.db"  # Fallback
    
    def _ensure_database_exists(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    # User management methods
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, hashed_password, created_at, last_login FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "hashed_password": row["hashed_password"],
                    "created_at": row["created_at"],
                    "last_login": row["last_login"]
                }
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error getting user by username '{username}': {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, hashed_password, created_at, last_login FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "hashed_password": row["hashed_password"],
                    "created_at": row["created_at"],
                    "last_login": row["last_login"]
                }
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise
    
    async def create_user(self, username: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        """Create new user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, hashed_password, created_at) VALUES (?, ?, ?)",
                (username, hashed_password, datetime.utcnow())
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Created user '{username}' with ID {user_id}")
            return {
                "id": user_id,
                "username": username,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
            
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed: username '{username}' already exists")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error creating user '{username}': {str(e)}")
            raise
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, created_at, last_login FROM users ORDER BY created_at")
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row["id"],
                    "username": row["username"],
                    "created_at": row["created_at"],
                    "last_login": row["last_login"]
                }
                for row in rows
            ]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            success = rows_affected > 0
            if success:
                logger.info(f"Deleted user with ID {user_id}")
            
            return success
            
        except sqlite3.Error as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.utcnow(), user_id)
            )
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            return rows_affected > 0
            
        except sqlite3.Error as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            raise
    
    # Portfolio management methods
    async def get_stocks_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all stocks in user's portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, user_id, ticker, quantity, average_buy_price, created_at, updated_at 
                   FROM portfolios WHERE user_id = ? ORDER BY ticker""",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "ticker": row["ticker"],
                    "quantity": row["quantity"],
                    "average_buy_price": row["average_buy_price"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in rows
            ]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting stocks for user {user_id}: {str(e)}")
            raise
    
    async def get_stock_by_id(self, stock_id: int) -> Optional[Dict[str, Any]]:
        """Get stock by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, user_id, ticker, quantity, average_buy_price, created_at, updated_at 
                   FROM portfolios WHERE id = ?""",
                (stock_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "ticker": row["ticker"],
                    "quantity": row["quantity"],
                    "average_buy_price": row["average_buy_price"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error getting stock by ID {stock_id}: {str(e)}")
            raise
    
    async def add_stock_to_portfolio(
        self, 
        user_id: int, 
        ticker: str, 
        quantity: float, 
        average_buy_price: float
    ) -> Optional[Dict[str, Any]]:
        """Add stock to user's portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.utcnow()
            cursor.execute(
                """INSERT INTO portfolios (user_id, ticker, quantity, average_buy_price, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, ticker, quantity, average_buy_price, now, now)
            )
            conn.commit()
            stock_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Added stock {ticker} to portfolio for user {user_id}")
            return {
                "id": stock_id,
                "user_id": user_id,
                "ticker": ticker,
                "quantity": quantity,
                "average_buy_price": average_buy_price,
                "created_at": now,
                "updated_at": now
            }
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"Failed to add stock {ticker} for user {user_id}: {str(e)}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding stock {ticker} for user {user_id}: {str(e)}")
            raise
    
    async def update_stock_in_portfolio(
        self, 
        stock_id: int, 
        quantity: float, 
        average_buy_price: float
    ) -> bool:
        """Update stock in portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE portfolios SET quantity = ?, average_buy_price = ?, updated_at = ? 
                   WHERE id = ?""",
                (quantity, average_buy_price, datetime.utcnow(), stock_id)
            )
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            success = rows_affected > 0
            if success:
                logger.info(f"Updated stock with ID {stock_id}")
            
            return success
            
        except sqlite3.Error as e:
            logger.error(f"Error updating stock {stock_id}: {str(e)}")
            raise
    
    async def delete_stock_from_portfolio(self, stock_id: int) -> bool:
        """Delete stock from portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portfolios WHERE id = ?", (stock_id,))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            success = rows_affected > 0
            if success:
                logger.info(f"Deleted stock with ID {stock_id}")
            
            return success
            
        except sqlite3.Error as e:
            logger.error(f"Error deleting stock {stock_id}: {str(e)}")
            raise
    
    # Analysis data methods
    async def get_historical_data_for_ticker(
        self, 
        ticker: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get historical data for ticker."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT
                    hd.date, hd.open, hd.high, hd.low, hd.close, hd.volume,
                    hd.rsi, hd.macd, hd.macd_signal, hd.macd_hist, 
                    hd.ema10, hd.ema20, hd.ema50,
                    hd.bollinger_upper, hd.bollinger_middle, hd.bollinger_lower,
                    hd.atr, hd.stoch_k, hd.stoch_d, hd.roc5, hd.roc10, 
                    hd.event_data_json
                FROM historical_data hd
                JOIN candidates c ON hd.candidate_id = c.id
                WHERE c.ticker = ?
                ORDER BY hd.date ASC
            """
            
            params = [ticker]
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting historical data for {ticker}: {str(e)}")
            raise
    
    async def get_event_data_for_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Get event data for ticker (placeholder implementation)."""
        try:
            # TODO: Implement actual event data retrieval
            logger.debug(f"Getting event data for {ticker} (placeholder)")
            return []
            
        except Exception as e:
            logger.error(f"Error getting event data for {ticker}: {str(e)}")
            raise
    
    # Health check methods
    async def check_connection(self) -> bool:
        """Check database connection health."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information for monitoring."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['users', 'portfolios', 'candidates', 'historical_data']
            table_counts = {}
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except sqlite3.Error:
                    table_counts[table] = 0
            
            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_bytes = page_count * page_size
            
            conn.close()
            
            return {
                "database_path": self.db_path,
                "table_counts": table_counts,
                "database_size_bytes": db_size_bytes,
                "database_size_mb": round(db_size_bytes / (1024 * 1024), 2)
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error getting database info: {str(e)}")
            raise