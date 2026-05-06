from fastapi import FastAPI

app = FastAPI(title="IKRAAZ Trading Bot API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "IKRAAZ ENGINE RUNNING"}


@app.get("/stocks")
def stocks() -> list[dict[str, str | float]]:
    return [
        {"symbol": "OGDC", "name": "Oil & Gas Development Co.", "price": 133.5},
        {"symbol": "PPL", "name": "Pakistan Petroleum Ltd.", "price": 109.2},
        {"symbol": "PSO", "name": "Pakistan State Oil", "price": 177.1},
        {"symbol": "HBL", "name": "Habib Bank Ltd.", "price": 124.9},
        {"symbol": "UBL", "name": "United Bank Ltd.", "price": 184.4},
        {"symbol": "MCB", "name": "MCB Bank Ltd.", "price": 235.7},
        {"symbol": "ENGRO", "name": "Engro Corporation", "price": 316.8},
        {"symbol": "LUCK", "name": "Lucky Cement", "price": 737.0},
        {"symbol": "FFC", "name": "Fauji Fertilizer Co.", "price": 142.6},
        {"symbol": "SYS", "name": "Systems Ltd.", "price": 418.2},
    ]
