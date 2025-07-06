import sqlite3
import os
from typing import Dict, Any, List, Optional

from src.config.config import Config

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'daki.db')

class DBAccess:
    def __init__(self):
        self.db_path = DATABASE_PATH

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"id": user[0], "username": user[1], "hashed_password": user[2]}
        return None

    async def create_user(self, username: str, hashed_password: str) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, hashed_password, created_at) VALUES (?, ?, datetime('now'))",
                           (username, hashed_password))
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username}
        except sqlite3.IntegrityError:
            return None # Benutzername existiert bereits
        finally:
            conn.close()

    async def check_connection(self) -> bool:
        """
        Prüft die Datenbankverbindung.
        """
        try:
            conn = self._get_connection()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    async def get_stocks_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ticker, quantity, average_buy_price, created_at, updated_at FROM portfolios WHERE user_id = ?", (user_id,))
        stocks = []
        for row in cursor.fetchall():
            stocks.append({
                "id": row[0],
                "ticker": row[1],
                "quantity": row[2],
                "average_buy_price": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        conn.close()
        return stocks

    async def add_stock_to_portfolio(self, user_id: int, ticker: str, quantity: float, average_buy_price: float) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO portfolios (user_id, ticker, quantity, average_buy_price, created_at, updated_at) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                (user_id, ticker, quantity, average_buy_price)
            )
            conn.commit()
            stock_id = cursor.lastrowid
            return {
                "id": stock_id,
                "user_id": user_id,
                "ticker": ticker,
                "quantity": quantity,
                "average_buy_price": average_buy_price
            }
        except sqlite3.IntegrityError:
            # Handle case where user already has this stock (e.g., update instead of insert)
            # For now, just return None to indicate failure due to unique constraint
            return None
        finally:
            conn.close()

    async def get_stock_by_id(self, stock_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, ticker, quantity, average_buy_price, created_at, updated_at FROM portfolios WHERE id = ?", (stock_id,))
        stock = cursor.fetchone()
        conn.close()
        if stock:
            return {
                "id": stock[0],
                "user_id": stock[1],
                "ticker": stock[2],
                "quantity": stock[3],
                "average_buy_price": stock[4],
                "created_at": stock[5],
                "updated_at": stock[6]
            }
        return None

    async def update_stock_in_portfolio(self, stock_id: int, quantity: float, average_buy_price: float) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE portfolios SET quantity = ?, average_buy_price = ?, updated_at = datetime('now') WHERE id = ?",
            (quantity, average_buy_price, stock_id)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    async def delete_stock_from_portfolio(self, stock_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolios WHERE id = ?", (stock_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    async def get_historical_data_for_ticker(self, ticker: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                hd.date, hd.open, hd.high, hd.low, hd.close, hd.volume,
                hd.rsi, hd.macd, hd.macd_signal, hd.macd_hist, hd.ema10, hd.ema20, hd.ema50,
                hd.bollinger_upper, hd.bollinger_middle, hd.bollinger_lower,
                hd.atr, hd.stoch_k, hd.stoch_d, hd.roc5, hd.roc10, hd.event_data_json
            FROM historical_data hd
            JOIN candidates c ON hd.candidate_id = c.id
            WHERE c.ticker = ?
            ORDER BY hd.date ASC
        """
        params = (ticker,)

        if limit:
            query += " LIMIT ?"
            params = (ticker, limit)

        cursor.execute(query, params)
        
        columns = [
            "date", "open", "high", "low", "close", "volume",
            "rsi", "macd", "macd_signal", "macd_hist", "ema10", "ema20", "ema50",
            "bollinger_upper", "bollinger_middle", "bollinger_lower",
            "atr", "stoch_k", "stoch_d", "roc5", "roc10", "event_data_json"
        ]
        
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        
        conn.close()
        return data

    async def get_user_cash_balance(self, user_id: int) -> float:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Hole den letzten Cash-Bestand des Benutzers
        cursor.execute("SELECT cash_balance_after FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0 # Standardmäßig 0, wenn keine Transaktionen

    async def record_transaction(self, user_id: int, ticker: str, type: str, quantity: float, price: float, transaction_cost: float, cash_balance_after: float) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (user_id, ticker, type, quantity, price, transaction_cost, timestamp, cash_balance_after) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)",
            (user_id, ticker, type, quantity, price, transaction_cost, cash_balance_after)
        )
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        return {"id": transaction_id, "user_id": user_id, "ticker": ticker, "type": type, "quantity": quantity, "price": price}

    async def update_portfolio_after_trade(self, user_id: int, ticker: str, quantity_change: float, cost_change: float):
        conn = self._get_connection()
        cursor = conn.cursor()
        # Prüfen, ob Aktie bereits im Portfolio
        cursor.execute("SELECT id, quantity, average_buy_price FROM portfolios WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        existing_stock = cursor.fetchone()

        if existing_stock:
            stock_id, current_quantity, current_avg_price = existing_stock
            new_quantity = current_quantity + quantity_change

            if new_quantity <= 0:
                # Aktie komplett verkauft, aus Portfolio entfernen
                cursor.execute("DELETE FROM portfolios WHERE id = ?", (stock_id,))
            else:
                # Durchschnittlichen Kaufpreis neu berechnen (nur bei Kauf relevant)
                if quantity_change > 0: # Kauf
                    new_total_cost = (current_quantity * current_avg_price) + cost_change
                    new_average_buy_price = new_total_cost / new_quantity
                else: # Verkauf, Durchschnittspreis bleibt gleich
                    new_average_buy_price = current_avg_price

                cursor.execute(
                    "UPDATE portfolios SET quantity = ?, average_buy_price = ?, updated_at = datetime('now') WHERE id = ?",
                    (new_quantity, new_average_buy_price, stock_id)
                )
        else:
            # Neue Aktie zum Portfolio hinzufügen (nur bei Kauf relevant)
            if quantity_change > 0:
                cursor.execute(
                    "INSERT INTO portfolios (user_id, ticker, quantity, average_buy_price, created_at, updated_at) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    (user_id, ticker, quantity_change, cost_change / quantity_change)
                )
            else:
                # Sollte nicht passieren: Verkauf einer nicht vorhandenen Aktie
                raise ValueError("Cannot sell stock not in portfolio.")
        conn.commit()
        conn.close()
