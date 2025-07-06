import os # Import hinzufügen
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from src.auth.jwt_utils import create_access_token, create_refresh_token, verify_token
from src.database.db_access import DBAccess
from src.security.auth_utils import hash_password, verify_password
from src.config.config import Config

app = FastAPI()

db_access = DBAccess()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Abhängigkeit für den aktuellen Benutzer
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token, credentials_exception)
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = await db_access.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

# Hilfsfunktion zur Überprüfung von Admin-Rechten
async def get_current_admin_user(current_user: Annotated[dict, Depends(get_current_user)]):
    # Im Entwicklungsmodus: Prüfe, ob der Benutzer der 'dev_admin' ist
    env = os.getenv("DAKI_ENV", "development")
    if env == "development":
        if current_user["username"] == Config.get("users", {}).get("admin", {}).get("username"):
            return current_user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    else:
        # Im Produktionsmodus: Hier müsste eine echte Rollenprüfung erfolgen
        # Für jetzt: Nur der Benutzer mit ID 1 (erster registrierter Admin)
        if current_user["id"] == 1: # Annahme: Erster Benutzer ist Admin
            return current_user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

@app.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await db_access.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    # Umgebungsabhängige Passwortprüfung
    env = os.getenv("DAKI_ENV", "development")
    if env == "development":
        # Im Entwicklungsmodus: Passwort direkt prüfen
        dev_admin_username = Config.get("users", {}).get("admin", {}).get("username")
        dev_admin_password = Config.get("users", {}).get("admin", {}).get("password")
        if form_data.username == dev_admin_username and form_data.password == dev_admin_password:
            access_token_expires = timedelta(minutes=Config.get("jwt", {}).get("access_token_expire_minutes", 30))
            refresh_token_expires = timedelta(days=Config.get("jwt", {}).get("refresh_token_expire_days", 7))
            access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
            refresh_token = create_refresh_token(data={"sub": user["username"]}, expires_delta=refresh_token_expires)
            return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    else: # Produktion
        # Im Produktionsmodus: Gehashtes Passwort prüfen
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=Config.get("jwt", {}).get("access_token_expire_minutes", 30))
    refresh_token_expires = timedelta(days=Config.get("jwt", {}).get("refresh_token_expire_days", 7))
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user["username"]}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@app.post("/users/register", tags=["Authentication"])
async def register_user(username: str, password: str):
    # Im Produktionsmodus: Passwort hashen
    env = os.getenv("DAKI_ENV", "development")
    if env == "production":
        hashed_password = hash_password(password)
    else:
        hashed_password = password # Im Entwicklungsmodus Klartext speichern

    user = await db_access.create_user(username, hashed_password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return {"message": "User registered successfully", "username": user["username"]}

@app.get("/users/me", tags=["Authentication"])
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user

@app.get("/users", tags=["User Management"])
async def get_all_users(admin_user: Annotated[dict, Depends(get_current_admin_user)]):
    """
    Listet alle registrierten Benutzer auf (nur für Administratoren).
    """
    conn = db_access._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, created_at, last_login FROM users")
    users = []
    for row in cursor.fetchall():
        users.append({
            "id": row[0],
            "username": row[1],
            "created_at": row[2],
            "last_login": row[3]
        })
    conn.close()
    return users

@app.delete("/users/{user_id}", tags=["User Management"])
async def delete_user(user_id: int, admin_user: Annotated[dict, Depends(get_current_admin_user)]):
    """
    Löscht einen Benutzer anhand seiner ID (nur für Administratoren).
    """
    conn = db_access._get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    if deleted_rows == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to DA-KI API!"}


@app.get("/stocks", tags=["Stock Management"])
async def get_user_stocks(current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Listet alle Aktien im Portfolio des aktuellen Benutzers auf.
    """
    stocks = await db_access.get_stocks_by_user_id(current_user["id"])
    return stocks

@app.post("/stocks", tags=["Stock Management"])
async def add_stock(stock: StockCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Fügt eine neue Aktie zum Portfolio des aktuellen Benutzers hinzu.
    """
    new_stock = await db_access.add_stock_to_portfolio(
        current_user["id"], stock.ticker, stock.quantity, stock.average_buy_price
    )
    if new_stock is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock already in portfolio or invalid data")
    return new_stock

@app.get("/stocks/{stock_id}", tags=["Stock Management"])
async def get_stock_details(stock_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Ruft Details einer bestimmten Aktie im Portfolio des Benutzers ab.
    """
    stock = await db_access.get_stock_by_id(stock_id)
    if stock is None or stock["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found or not authorized")
    return stock

@app.put("/stocks/{stock_id}", tags=["Stock Management"])
async def update_stock(stock_id: int, stock: StockUpdate, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Aktualisiert eine Aktie im Portfolio des Benutzers.
    """
    existing_stock = await db_access.get_stock_by_id(stock_id)
    if existing_stock is None or existing_stock["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found or not authorized")

    updated = await db_access.update_stock_in_portfolio(stock_id, stock.quantity, stock.average_buy_price)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update stock")
    return {"message": "Stock updated successfully"}

@app.delete("/stocks/{stock_id}", tags=["Stock Management"])
async def delete_stock(stock_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Löscht eine Aktie aus dem Portfolio des Benutzers.
    """
    existing_stock = await db_access.get_stock_by_id(stock_id)
    if existing_stock is None or existing_stock["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found or not authorized")

    deleted = await db_access.delete_stock_from_portfolio(stock_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete stock")
    return {"message": "Stock deleted successfully"}


@app.post("/analysis/start", tags=["Analysis & Prediction"])
async def start_analysis(tickers: List[str], current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Startet den Analyse- und Prognoseprozess für eine Liste von Tickersymbolen.
    """
    results = []
    for ticker in tickers:
        historical_data = await db_access.get_historical_data_for_ticker(ticker)
        if not historical_data:
            results.append({"ticker": ticker, "status": "failed", "message": "No historical data available"})
            continue

        # 1. Technisches Scoring
        technical_score_output = await scoring_engine.calculate_total_score(ticker, historical_data)

        # 2. Event-driven Scoring (Platzhalter, da Event-Daten noch nicht in DB)
        # event_data = await db_access.get_event_data_for_ticker(ticker) # Annahme: Funktion existiert
        # event_score_output = await event_scoring_engine.calculate_event_score(event_data)
        event_score_output = {"total_event_score": 0.0, "individual_events": {}, "weighted_events": {}, "active_events": []}

        # 3. ML Prediction
        # Für ML Prediction benötigen wir vorbereitete Features
        prepared_data = await data_preparation.prepare_data_for_ml(ticker, historical_data)
        if prepared_data.empty:
            ml_prediction = 0.0
            ml_message = "Not enough data for ML prediction."
        else:
            ml_prediction = await ml_predictor.predict(ticker, prepared_data.to_dict(orient='records'))
            ml_message = "ML prediction successful."

        results.append({
            "ticker": ticker,
            "status": "success",
            "technical_score": technical_score_output,
            "event_score": event_score_output,
            "ml_prediction": ml_prediction,
            "ml_message": ml_message
        })
    return results

@app.post("/stocks/add_from_analysis", tags=["Stock Management"])
async def add_stock_from_analysis(ticker: str, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Fügt eine Aktie aus den Analyseergebnissen zum Portfolio des Benutzers hinzu.
    (Vereinfacht: Fügt mit Standardwerten hinzu, da keine Kaufdaten aus Analyse kommen)
    """
    # Hier müsste man eigentlich die Analyseergebnisse prüfen und ggf. den Preis nehmen
    # Für jetzt: Annahme eines Standard-Kaufpreises und Menge
    quantity = 1.0 # Beispielmenge
    average_buy_price = 100.0 # Beispielpreis

    new_stock = await db_access.add_stock_to_portfolio(
        current_user["id"], ticker, quantity, average_buy_price
    )
    if new_stock is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock already in portfolio or invalid data")
    return new_stock
