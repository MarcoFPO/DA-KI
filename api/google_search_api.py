#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime

app = FastAPI(title="Google Search Mock API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_stock_data(symbol: str):
    """Generate mock stock data for any symbol"""
    random.seed(hash(symbol) % 2**32)
    
    base_prices = {
        'AAPL': 195.89, 'MSFT': 421.32, 'GOOGL': 167.84, 'AMZN': 181.50, 'META': 538.45,
        'TSLA': 248.50, 'NVDA': 875.50, 'NFLX': 483.26, 'ADBE': 512.78, 'CRM': 267.89,
        'PLTR': 45.80, 'SNOW': 156.72, 'CRWD': 298.45, 'NET': 87.23, 'DDOG': 128.67,
        'SAP': 234.56, 'BMW': 89.45, 'MBG': 67.89, 'ASML': 723.45, 'NESN': 98.76
    }
    
    price = base_prices.get(symbol, random.uniform(50, 500))
    change = random.uniform(-20, 20)
    change_percent = (change / price) * 100
    
    market_caps = ['50M', '100M', '500M', '1B', '5B', '10B', '50B', '100B', '500B', '1T']
    pe_ratios = ['15.2', '23.7', '31.4', '45.8', '67.2', '89.1', '156.3', '234.5']
    
    return {
        "name": f"{symbol} Corporation",
        "current_price": round(price, 2),
        "change": f"{change:+.2f}",
        "change_percent": f"{change_percent:+.2f}%",
        "market_cap": random.choice(market_caps),
        "pe_ratio": random.choice(pe_ratios),
        "news": [
            {
                "title": f"{symbol} zeigt starke Performance in Q4",
                "snippet": f"Die {symbol}-Aktie verzeichnet positive Entwicklung mit stabilen Fundamentaldaten.",
                "source": "Financial Times",
                "date": datetime.now().strftime('%Y-%m-%d')
            }
        ]
    }

@app.get("/")
async def root():
    return {"message": "Google Search Mock API", "version": "1.0.0"}

@app.get("/api/google-suche/{symbol}")
async def get_stock_info(symbol: str):
    """Get stock information for any symbol"""
    try:
        stock_data = generate_stock_data(symbol.upper())
        
        return {
            "symbol": symbol.upper(),
            "daten": stock_data,
            "quelle": "Mock Google Search",
            "zeitstempel": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.1.1.110", port=8002)