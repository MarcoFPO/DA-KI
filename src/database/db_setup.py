import sqlite3
import os

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'daki.db')

def initialize_db():
    """
    Initialisiert die SQLite-Datenbank und erstellt die notwendigen Tabellen.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True) # Sicherstellen, dass das Datenverzeichnis existiert

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Tabelle: candidates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                selection_reason TEXT,
                timestamp TEXT NOT NULL,
                is_complete INTEGER NOT NULL DEFAULT 0
            )
        ''')

        # Tabelle: historical_data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                rsi REAL,
                macd REAL,
                macd_signal REAL,
                macd_hist REAL,
                ema10 REAL,
                ema20 REAL,
                ema50 REAL,
                bollinger_upper REAL,
                bollinger_middle REAL,
                bollinger_lower REAL,
                atr REAL,
                stoch_k REAL,
                stoch_d REAL,
                roc5 REAL,
                roc10 REAL,
                event_data_json TEXT,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        ''')

        # Tabelle: users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')

        # Tabelle: portfolios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_buy_price REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, ticker)
            )
        ''')

        # Tabelle: transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                type TEXT NOT NULL, -- 'BUY' or 'SELL'
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                transaction_cost REAL,
                timestamp TEXT NOT NULL,
                cash_balance_after REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        print(f"Database initialized successfully at {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_db()
